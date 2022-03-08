from copy import deepcopy


TOKEN_RESPONSE = {
    "access_token": "dC34Pf6kdG.Gjpw5HN6c.JSKABYDGye6",
    "token_type": "Bearer",
    "expires_in": 1800,
    "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY.ashajrbGFDGd",
}

TOKEN_RESPONSE_NO_ACCESS_TOKEN = deepcopy(TOKEN_RESPONSE)
TOKEN_RESPONSE_NO_ACCESS_TOKEN.pop("access_token")

TOKEN_RESPONSE_NO_CORRECT_ACCESS_TOKEN = deepcopy(TOKEN_RESPONSE)
TOKEN_RESPONSE_NO_CORRECT_ACCESS_TOKEN["access_token"] = "dC34Pf6kdG.Gjpw5HN"

TOKEN_RESPONSE_NO_TOKEN_TYPE = deepcopy(TOKEN_RESPONSE)
TOKEN_RESPONSE_NO_TOKEN_TYPE.pop("token_type")

TOKEN_RESPONSE_NO_CORRECT_TOKEN_TYPE = deepcopy(TOKEN_RESPONSE)
TOKEN_RESPONSE_NO_CORRECT_TOKEN_TYPE["token_type"] = "prova"

TOKEN_REFRESH_RESPONSE = deepcopy(TOKEN_RESPONSE)
TOKEN_REFRESH_RESPONSE["refresh_token"] = "wJ848BcyLP.hHhJB.kjHMjUGUSGKEE3"

TOKEN_REFRESH_RESPONSE_NO_REFRESH_TOKEN = deepcopy(TOKEN_REFRESH_RESPONSE)
TOKEN_REFRESH_RESPONSE_NO_REFRESH_TOKEN.pop("refresh_token")

TOKEN_REFRESH_RESPONSE_NO_CORRECT_REFRESH_TOKEN = deepcopy(TOKEN_REFRESH_RESPONSE)
TOKEN_REFRESH_RESPONSE_NO_CORRECT_REFRESH_TOKEN["refresh_token"] = "dC34Pf6kdG..Gjpw5HN"

TOKEN_ERROR_RESPONSE = {
    "error": "invalid_request",
    "error_description": "descrizione dell’errore",
}

TOKEN_ERROR_RESPONSE_NO_ERROR = deepcopy(TOKEN_ERROR_RESPONSE)
TOKEN_ERROR_RESPONSE_NO_ERROR.pop("error")

TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR = deepcopy(TOKEN_ERROR_RESPONSE)
TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR["error"] = ""

TOKEN_ERROR_RESPONSE_NO_ERROR_DESCRIPTION = deepcopy(TOKEN_ERROR_RESPONSE)
TOKEN_ERROR_RESPONSE_NO_ERROR_DESCRIPTION.pop("error_description")

TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION = deepcopy(TOKEN_ERROR_RESPONSE)
TOKEN_ERROR_RESPONSE_NO_CORRECT_ERROR_DESCRIPTION["error"] = []
