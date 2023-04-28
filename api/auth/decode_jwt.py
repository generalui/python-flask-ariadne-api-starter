from jwt import decode, ExpiredSignatureError, InvalidTokenError
from flask import current_app
from api.constants import INVALID_TOKEN, SECRET_KEY, SIGNATURE_EXP, SIGNING_ALGORITHM


def decode_jwt(auth_token):
    '''
    Decodes the auth token (JWT)

            Parameters:
                    auth_token (str): TheJWT to decode.

            Returns:
                    User ID (integer|string): The original encoded value.
                    or
                    Error message on error.
    '''
    try:
        payload = decode(auth_token, current_app.config.get(
            SECRET_KEY), algorithms=[SIGNING_ALGORITHM])
        return payload['sub']
    except ExpiredSignatureError:
        return SIGNATURE_EXP
    except InvalidTokenError:
        return INVALID_TOKEN
