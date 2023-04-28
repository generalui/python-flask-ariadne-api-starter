import json
import pytest
from sqlalchemy import and_
from api.constants import INVALID_ADDRESS_ID
from api.db_models import Address


@pytest.fixture(scope='module')
def common_mutation():
    return """mutation Registration($input: RegistrationInput!) {
        register(input: $input) {
            status
            id
        }
    } """


@pytest.fixture(scope='function')
def test_address(db_session, address_1, address_2, city, country, state, zipcode):
    test_address = Address(address_1=address_1, address_2=address_2,
                           city=city, country=country, state=state, zipcode=zipcode)
    db_session.add(test_address)
    db_session.commit()

    yield db_session.query(Address).filter(
        and_(Address.address_1 == address_1, Address.address_2 == address_2, Address.city == city, Address.state == state, Address.zipcode == zipcode)).one_or_none()


def test_register_user_mutation_invalid_address(client, common_mutation, email, first_name, last_name, password):
    non_existant_address_id = 1
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': password,
            'addressId': non_existant_address_id
        }
    }
    })
    json_data = json.loads(response.data)
    errors = json_data['errors']
    data = json_data['data']
    message = errors[0]['message']

    assert data == None
    assert isinstance(errors, list)
    assert message == INVALID_ADDRESS_ID


def test_register_user_mutation(client, common_mutation, test_address, email, first_name, last_name, password):
    response = client.post('/api', json={'query': common_mutation, 'variables': {
        'input': {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': password,
            'addressId': test_address.id
        }
    }
    })
    json_data = json.loads(response.data)
    data = json_data['data']
    register = data['register']

    assert type(register['id']) is str
    assert register['status'] == True
