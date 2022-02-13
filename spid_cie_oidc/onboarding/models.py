from copy import deepcopy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
# from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from spid_cie_oidc.entity.abstract_models import TimeStampedModel
from spid_cie_oidc.entity.models import (
    ENTITY_TYPES,
    ENTITY_STATUS,
    FederationEntityConfiguration,
    PublicJwk
)

from spid_cie_oidc.entity.exceptions import (
    MissingAuthorityHintsClaim,
    NotDescendant
)
from spid_cie_oidc.entity.statements import (
    get_entity_configuration,
    EntityConfiguration
)
from spid_cie_oidc.entity.jwtse import create_jws
from spid_cie_oidc.entity.trust_chain import HTTPC_PARAMS
from spid_cie_oidc.entity.utils import iat_now
from spid_cie_oidc.entity.utils import exp_from_now
from typing import Union

from . import settings as local_settings

import json
import logging
import uuid


FEDERATION_DEFAULT_POLICY = getattr(
    settings, "FEDERATION_DEFAULT_POLICY",
    local_settings.FEDERATION_DEFAULT_POLICY
)
FEDERATION_DEFAUL_EXP = getattr(
    settings, "FEDERATION_DEFAUL_EXP",
    local_settings.FEDERATION_DEFAUL_EXP
)

logger = logging.getLogger(__name__)


def get_first_self_trust_anchor(sub:str = None) -> Union[FederationEntityConfiguration, None]:
    """
        get the first available Trust Anchor that represent self
        as a qualified issuer
    """
    lk = dict(
        metadata__federation_entity__isnull=False,
        is_active=True
    )
    if sub:
        lk['sub'] = sub
    return FederationEntityConfiguration.objects.filter(**lk).first()


class FederationEntityProfile(TimeStampedModel):
    """
        Federation OnBoarding profile.
        It optionally defines trust marks templates
    """
    name = models.CharField(
        max_length=33,
        help_text=_(
            "Profile name. "
        ),
    )
    profile_category = models.CharField(
        max_length=64,
        help_text=_(
            "Profile id. It SHOULD be a URL but feel free to put whatever"
        ),
        choices=[(i, i) for i in ENTITY_TYPES]
    )
    profile_id = models.CharField(
        max_length=1024,
        help_text=_(
            "Profile id. It SHOULD be a URL but feel free to put whatever"
        ),
        unique=True
    )
    trust_mark_template = models.JSONField(
        blank=True,
        help_text=_("trust marks template for this profile"),
        default=dict,
    )

    class Meta:
        verbose_name = "Federation Entity Profile"
        verbose_name_plural = "Federation Entity Profiles"

    @property
    def trust_mark_template_as_json(self):
        return json.dumps(self.trust_mark_template)
    
    def __str__(self):
        return f"{self.name} {self.profile_id}"


class FederationDescendant(TimeStampedModel):
    """
        Federation OnBoarding entries.
    """
    
    def validate_entity_configuration(value):
        """
            value is the sub url
        """
        try:
            jwt = get_entity_configuration(value)
        except Exception as e:
            raise ValidationError(
                f"Failed to fetch Entity Configuration for {value}: {e}"
            )
        ec = EntityConfiguration(jwt, httpc_params = HTTPC_PARAMS)
        ec.validate_by_itself()

        authority_hints = ec.payload.get('authority_hints', [])
        if not authority_hints:
            raise MissingAuthorityHintsClaim(
                "authority_hints must be present "
                "in a descendant entity configuration"
            )

        proper_descendant = False
        for i in authority_hints:
            if i in settings.OIDCFED_FEDERATION_TRUST_ANCHORS:
                proper_descendant = True
                break
        if not proper_descendant:
            raise NotDescendant(
                "This participant MUST have one of "
                f"{', '.join(settings.OIDCFED_FEDERATION_TRUST_ANCHORS)} in "
                f"its authority_hints claim. It has: {authority_hints}"
            )


    def def_uid():
        return f"autouid-{uuid.uuid4()}"


    uid = models.CharField(
        max_length=1024,
        default=def_uid,
        unique=True,
        help_text=_(
            "an unique code that identifies this entry. "
            "For italian public service it may be the IPA code."
        ),
    )
    name = models.CharField(
        max_length=33,
        help_text=_(
            "human readable name of this entity. "
            "It may be a unit or organization name"
        ),
    )
    sub = models.URLField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        help_text=_("URL that identifies this Entity in the Federation."),
        validators = [validate_entity_configuration]
    )
    type = models.CharField(
        max_length=33,
        blank=True,
        default='openid_relying_party',
        choices = [(i,i) for i in ENTITY_TYPES],
        help_text=_("OpenID Connect Federation entity type")
    )
    registrant = models.ManyToManyField(
        get_user_model(),
        help_text=_(
            "Logged in users can modify only sub, contacts and jwks "
            "attributes, if they're owner of this entry. "
        ),
        blank=True
    )
    metadata_policy = models.JSONField(
        blank=True,
        help_text=_("if present overloads the DEFAULT policy"),
        default=dict,
    )
    constraints = models.JSONField(
        blank=True,
        help_text=_("if present overloads the DEFAULT policy"),
        default=dict,
    )
    extended_claims = models.JSONField(
        blank=True,
        help_text=_(
            "a dictionary containing any other claim like: "
            "jti, crti, policy_language_crit and any other extension"
        ),
        default=dict,
    )
    status = models.CharField(
        max_length=33,
        default=False,
        help_text=_(
            "Its entity configuration is periodically fetched and validated."
        ),
        choices = [(i, i) for i in ENTITY_STATUS.keys()]
    )
    status_log = models.JSONField(
        blank=True,
        help_text=_("status log"),
        default=dict,
    )
    is_active = models.BooleanField(
        default=False, help_text=_("If this entity is active. ")
    )

    class Meta:
        verbose_name = "Federation Entity Descendant"
        verbose_name_plural = "Federation Entity Descendants"

    @property
    def trust_marks(self):
        #
        profiles = FederationEntityAssignedProfile.objects.filter(descendant = self)
        return [i.trust_mark for i in profiles]

    @property
    def trust_marks_as_json(self):
        return json.dumps(self.trust_marks)
    
    @property
    def entity_profiles(self):
        return [
            i.profile.profile_category
            for i in FederationEntityAssignedProfile.objects.filter(
                descendant = self
            )
        ]

    @property
    def entity_statement_as_dict(self) -> dict:
        jwks = [i.jwk.jwk for i in FederationDescendantJwk.objects.filter(
                descendant=self
        )]
        if not jwks:
            return {}

        policies = {
            k:local_settings.FEDERATION_DEFAULT_POLICY[k]
            for k in self.entity_profiles
        }

        # apply custom policies if defined
        policies.update(self.metadata_policy)
        
        data = {
          "exp": exp_from_now(minutes=FEDERATION_DEFAUL_EXP),
          "iat": iat_now(),
          "iss": get_first_self_trust_anchor().sub,
          "sub": self.sub,
          "jwks": {
            "keys": jwks
          },
          "metadata_policy": policies
        }
        return data

    @property
    def entity_statement_as_json(self):
        return json.dumps(self.entity_statement_as_dict)

    @property
    def entity_statement_as_jws(self):
        issuer = get_first_self_trust_anchor()
        return create_jws(
            self.entity_statement_as_dict,
            issuer.jwks[0],
            alg=issuer.default_signature_alg
        )

    def __str__(self):
        return "{} [{} and {}]".format(
            self.sub,
            self.status,
            "active" if self.is_active else "--"
        )


class FederationDescendantJwk(TimeStampedModel):
    descendant = models.ForeignKey(
        FederationDescendant,
        on_delete=models.CASCADE
    )
    jwk = models.ForeignKey(
        PublicJwk,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Federation Descendant Public JWK"
        verbose_name_plural = "Federation Descendant Public JWKs"
    
    def __str__(self):
        return f"{self.descendant.sub} {self.jwk.kid}"


class FederationEntityAssignedProfile(TimeStampedModel):
    descendant = models.ForeignKey(
        FederationDescendant,
        on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        FederationEntityProfile,
        on_delete=models.CASCADE
    )
    issuer = models.ForeignKey(
        FederationEntityConfiguration,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Federation Entity Descendant Assigned Profile"
        verbose_name_plural = "Federation Descendant Assigned Profiles"

    @property
    def trust_mark_as_dict(self) -> dict:
        data = deepcopy(self.profile.trust_mark_template)
        data['sub'] = self.descendant.sub
        data['iss'] = self.issuer.sub
        data['iat'] = iat_now()
        return data

    @property
    def trust_mark_as_json(self):
        return json.dumps(self.trust_mark_as_dict)
    
    @property
    def trust_mark_as_jws(self):
        return create_jws(
            self.trust_mark_as_dict,
            self.issuer.jwks[0],
            alg=self.issuer.default_signature_alg
        )

    @property
    def trust_mark(self):
        return {
            'id': self.profile.profile_id,
            'trust_mark': self.trust_mark_as_jws
        }

    def __str__(self):
        return f"{self.profile} [{self.descendant}]"


class FederationDescendantContact(TimeStampedModel):
    """
        Federation OnBoarding entries.
    """
    entity = models.ForeignKey(
        FederationDescendant,
        on_delete=models.CASCADE,
        help_text=_("Entity for which this contac is related")
    )
    contact = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text=_(
            "any kind of contact type, usually an email."
        ),
    )
    type = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        choices = [(i, i) for i in ('email', 'telephone', 'other')]
    )

    class Meta:
        verbose_name = "Federation Entity Contact"
        verbose_name_plural = "Federation Entity Contacts"

    def __str__(self):
        return f"{self.contact} {self.entity.sub}"


# signal on each save
# def trust_chain_trigger(**kwargs):
    # subject = kwargs['instance'].sub

    # onboarding uses the first available configuration of federation_entity
    # fe = FederationEntityConfiguration.objects.filter(
        # is_active=True,
    # ).first()
    
    # logger.info(
        # f"Receiving trust chain evaluation signal for {subject}"
    # )
    # return trust_chain_builder(subject)
# post_save.connect(trust_chain_trigger, sender=FederationDescendant)
#
