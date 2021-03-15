import pytest
from api.constants.error_messages import INVALID_TOKEN, SIGNATURE_EXP
from api.database import decode_jwt, encode_jwt


@pytest.fixture(scope='module')
def user_id():
    return 42


@pytest.fixture(scope='module')
def jwt(app, user_id):
    return encode_jwt(user_id)


@pytest.fixture(scope='module')
def jwt_expired(app, user_id):
    return encode_jwt(user_id, life=-42)


def test_decode_jwt(jwt, user_id):
    assert isinstance(jwt, bytes)
    assert jwt != user_id
    id = decode_jwt(jwt)
    assert id == user_id
    id = decode_jwt(user_id)
    assert id != user_id


def test_decode_jwt_invalid(app, user_id):
    error = decode_jwt(user_id)
    assert error == INVALID_TOKEN


def test_decode_jwt_expired(jwt_expired, user_id):
    error = decode_jwt(jwt_expired)
    assert error == SIGNATURE_EXP
