from datetime import datetime
import json
import pytest
from werkzeug.security import generate_password_hash
from api.constants.error_messages import INVALID_PASSWORD, LOGIN_ERROR, USER_NOT_FOUND
from api.db_models import Address, User
from api.enums import user_prefix_enum, user_status_enum


@pytest.fixture(scope='module')
def common_mutation():
    return """mutation Login($input: LoginInput!) {
        login(input: $input) {
            error
            token
            user { email }
        }
    }"""


@pytest.fixture(scope='function')
def test_user(db_session, email, first_name, last_name, password, status):
    user = User(
        email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password), status=status)
    db_session.add(user)
    db_session.commit()

    yield db_session.query(User).filter_by(email=email).one_or_none()


def test_login_mutation_no_user(client, common_mutation, email, password):
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {
            'email': email,
            'password': password
        }
    }})
    json_data = json.loads(response.data)
    assert json_data['data'] is None
    errors = json_data['errors']
    assert len(errors) == 1
    assert errors[0]['message'] == USER_NOT_FOUND


def test_login_mutation_no_email(client, common_mutation, password):
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {'password': password}
    }})
    json_data = json.loads(response.data)
    assert json_data['data'] is None
    errors = json_data['errors']
    assert len(errors) == 1
    assert type(errors[0]['message']) is str


def test_login_mutation_no_password(client, common_mutation, email):
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {'email': email}
    }})
    json_data = json.loads(response.data)
    assert json_data['data'] is None
    errors = json_data['errors']
    assert len(errors) == 1
    assert type(errors[0]['message']) is str


def test_login_mutation_invalid_password(client, common_mutation, email, password, test_user):
    bad_password = password + 'bad'
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {
            'email': email,
            'password': bad_password
        }
    }})
    json_data = json.loads(response.data)
    assert json_data['data'] is None
    errors = json_data['errors']
    assert len(errors) == 1
    assert type(errors[0]['message']) is str


def test_login_mutation(client, common_mutation, email, password, test_user):
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {
            'email': email,
            'password': password
        }
    }})
    json_data = json.loads(response.data)
    login = json_data['data']['login']
    assert type(login['token']) is str
    assert login['error'] is None
    assert login['user']['email'] == email
