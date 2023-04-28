import json
import pytest
from tests import NoneType
from api.auth import encode_jwt
from api.constants import NOT_AUTHENTICATED
from api.db_models import User


@pytest.fixture(scope='module')
def test_auth_password():
    return "qwerty"


@pytest.fixture(scope='function')
def test_user(db_session, email, first_name, last_name, password, status):
    user = User(
        email=email, first_name=first_name, last_name=last_name, password=password, status=status)
    db_session.add(user)
    db_session.commit()

    yield db_session.query(User).filter_by(email=email).one_or_none()


def test_testAuth_query_no_Authorization_header(client):
    query = """query TestAuth {
        testAuth { items { userAgent } }
    }"""
    response = client.post('/api', json={'query': query})
    json_data = json.loads(response.data)
    test = json_data['data']
    results = json_data['errors']

    assert type(test) is NoneType
    assert isinstance(results, list)
    assert len(results) == 1
    for result in results:
        assert result['message'] == NOT_AUTHENTICATED


def test_testAuth_query_Authenticated(db_session, client, test_user, password):
    jwt = encode_jwt(test_user.id)
    query = """query TestAuth {
        testAuth { items { userAgent } }
    }"""
    response = client.post(
        '/api', json={'query': query}, headers={'Authorization': 'bearer ' + jwt.decode('utf-8')})
    json_data = json.loads(response.data)
    test = json_data['data']['testAuth']
    results = test['items']

    assert type(results['userAgent']) is str


def test_testAuth_query_no_bearer(db_session, client, test_user):
    jwt = encode_jwt(test_user.id)
    query = """query TestAuth {
        testAuth { items { userAgent } }
    }"""
    response = client.post(
        '/api', json={'query': query}, headers={'Authorization': jwt.decode('utf-8')})
    json_data = json.loads(response.data)
    test = json_data['data']
    results = json_data['errors']

    assert type(test) is NoneType
    assert isinstance(results, list)
    assert len(results) == 1
    for result in results:
        assert result['message'] == NOT_AUTHENTICATED


def test_testAuth_query_wrong_auth_schema(db_session, client, test_user):
    jwt = encode_jwt(test_user.id)
    query = """query TestAuth {
        testAuth { items { userAgent } }
    }"""
    response = client.post(
        '/api', json={'query': query}, headers={'Authorization': 'Token ' + jwt.decode('utf-8')})
    json_data = json.loads(response.data)
    test = json_data['data']
    results = json_data['errors']

    assert type(test) is NoneType
    assert isinstance(results, list)
    assert len(results) == 1
    for result in results:
        assert result['message'] == NOT_AUTHENTICATED


def test_testAuth_query_no_user(db_session, client, test_user):
    jwt = encode_jwt(test_user.id)
    query = """query TestAuth {
        testAuth { items { userAgent } }
    }"""
    response = client.post(
        '/api', json={'query': query}, headers={'Authorization': 'Token ' + jwt.decode('utf-8')})
    json_data = json.loads(response.data)
    test = json_data['data']
    results = json_data['errors']

    assert type(test) is NoneType
    assert isinstance(results, list)
    assert len(results) == 1
    for result in results:
        assert result['message'] == NOT_AUTHENTICATED
