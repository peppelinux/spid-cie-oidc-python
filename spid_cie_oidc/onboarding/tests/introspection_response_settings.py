
from copy import deepcopy


INTROSPECTION_RESPONSE = {
    "active": True,
    "scope": ["openid"],
    "exp": 162545274,
    "sub": "OP-1234567890",
    "client_id": "https://rp.agid.gov.it/",
    "iss": "https://op.spid.agid.gov.it/",
    "aud": ["https://rp.spid.agid.gov.it/auth"]
}


INTROSPECTION_RESPONSE_NO_ACTIVE = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_ACTIVE.pop("active")

INTROSPECTION_RESPONSE_NO_CORRECT_ACTIVE = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_ACTIVE["active"] = "ciao"

INTROSPECTION_RESPONSE_NO_CORRECT_SCOPE = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_SCOPE["scope"] = "scope"

INTROSPECTION_RESPONSE_NO_CORRECT_EXP = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_EXP["exp"] = "exp"

INTROSPECTION_RESPONSE_NO_CORRECT_SUB = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_SUB["sub"] = []

INTROSPECTION_RESPONSE_NO_CORRECT_CLIENT_ID = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_CLIENT_ID["client_id"] = "https/op.agid.gov.it/"

INTROSPECTION_RESPONSE_NO_CORRECT_ISS = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_ISS["iss"] = ""

INTROSPECTION_RESPONSE_NO_CORRECT_AUD = deepcopy(INTROSPECTION_RESPONSE)
INTROSPECTION_RESPONSE_NO_CORRECT_AUD["aud"] = "https://rp.spid.agid.gov.it/auth"


INTROSPECTION_ERROR_RESPONSE = {
    "error": "invalid_request",
    "error_description": "descrizione dell’errore"
}

INTROSPECTION_ERROR_RESPONSE_SPID_NO_ERROR = deepcopy(INTROSPECTION_ERROR_RESPONSE)
INTROSPECTION_ERROR_RESPONSE_SPID_NO_ERROR.pop("error")

INTROSPECTION_ERROR_RESPONSE_SPID_NO_CORRECT_ERROR = deepcopy(INTROSPECTION_ERROR_RESPONSE)
INTROSPECTION_ERROR_RESPONSE_SPID_NO_CORRECT_ERROR["error"] = "invalid_token"

INTROSPECTION_ERROR_RESPONSE_CIE_NO_ERROR = deepcopy(INTROSPECTION_ERROR_RESPONSE)
INTROSPECTION_ERROR_RESPONSE_CIE_NO_ERROR.pop("error")

INTROSPECTION_ERROR_RESPONSE_CIE_NO_CORRECT_ERROR = deepcopy(INTROSPECTION_ERROR_RESPONSE)
INTROSPECTION_ERROR_RESPONSE_CIE_NO_CORRECT_ERROR["error"] = "error"

INTROSPECTION_ERROR_RESPONSE_NO_ERROR_DESCRIPTION = deepcopy(INTROSPECTION_ERROR_RESPONSE)
INTROSPECTION_ERROR_RESPONSE_NO_ERROR_DESCRIPTION.pop("error_description")

INTROSPECTION_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION = deepcopy(INTROSPECTION_ERROR_RESPONSE)
INTROSPECTION_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION["error_description"] = []
