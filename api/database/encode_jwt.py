from datetime import datetime, timedelta
from jwt import encode
from flask import current_app


def encode_jwt(user_id, life=900):
    '''
    Generates the Auth Token (JWT)

            Parameters:
                    user_id (str): The value to encode (this should be returned when decoded).
                    life (int): The life of the auth token in seconds. The default is 15 minutes (900 seconds).

            Returns:
                    JWT (str): The encoded JWT
    '''
    payload = {
        'exp': datetime.utcnow() + timedelta(seconds=life),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )
