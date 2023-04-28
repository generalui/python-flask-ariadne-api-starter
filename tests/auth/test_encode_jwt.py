import pytest
from api.auth import encode_jwt


@pytest.fixture(scope='module')
def user_id():
    return 42


def test_encode_jwt(app, user_id):
    auth_token = encode_jwt(user_id)
    assert isinstance(auth_token, bytes)
