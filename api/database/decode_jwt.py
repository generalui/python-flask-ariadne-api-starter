from jwt import decode, ExpiredSignatureError, InvalidTokenError
from flask import current_app
from api.constants.error_messages import INVALID_TOKEN, SIGNATURE_EXP


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
            'SECRET_KEY'), algorithms=['HS256'])
        return payload['sub']
    except ExpiredSignatureError:
        return SIGNATURE_EXP
    except InvalidTokenError:
        return INVALID_TOKEN
