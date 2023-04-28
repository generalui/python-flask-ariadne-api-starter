import json
import pytest
from os import getenv
from faker import Faker
from random import choice, randrange
from werkzeug.security import generate_password_hash
from tests import NoneType
from api.resolvers.resolver_helpers.paging_utils import from_cursor_hash, to_cursor_hash, Paging
from api.db_models import Address, User


@pytest.fixture(scope='module')
def common_query_builder():
    def f(query_fields):
        return """query Users(
            $paging: PagingInput
            $distinct:Boolean
            $addressId: [ID!]
            $email: [String!]
            $firstName: [String!]
            $lastName: [String!]
            $prefix: [UserPrefixEnum!]
            $status: [UserStatusEnum!]
            $telephone: [String!]
        ) {
            users(
                paging: $paging
                distinct: $distinct
                addressId: $addressId
                email: $email
                firstName: $firstName
                lastName: $lastName
                prefix: $prefix
                status: $status
                telephone: $telephone
            )""" + query_fields + "}"
    return f


@pytest.fixture(scope='function')
def test_addresses(db_session, address_1, address_2, city, country, state, zipcode):
    def f(num_records):
        fake = Faker(['en-US', 'en_US', 'en_US', 'en-US'])
        records = set()
        records.add(
            address_1 + address_2 + city + country + state + zipcode)

        # Create one predictable record.
        test_address = Address(address_1=address_1, address_2=address_2,
                               city=city, country=country, state=state, zipcode=zipcode)
        db_session.add(test_address)
        db_session.commit()

        # Create as many more random records as required. The set won't allow dups.
        while len(records) < num_records:
            current_length = len(records)
            fake_address_1 = fake.street_address()
            fake_address_2 = fake.secondary_address()
            fake_city = fake.city()
            fake_state = fake.state()
            fake_zipcode = fake.postcode()
            records.add(
                fake_address_1 + fake_address_2 + fake_city + country + fake_state + fake_zipcode)
            if current_length < len(records):
                fake_test_address = Address(address_1=fake_address_1, address_2=fake_address_2,
                                            city=fake_city, country=country, state=fake_state, zipcode=fake_zipcode)
                db_session.add(fake_test_address)
                db_session.commit()

        return db_session.query(Address).order_by(Address.id).all()
    return f


@pytest.fixture(scope='function')
def test_users(db_session, test_addresses, email, first_name, last_name, password, status, telephone):
    def f(num_records):
        num_addresses = min([num_records, 10])
        user_addresses = test_addresses(num_addresses)
        fake = Faker(['en-US', 'en_US', 'en_US', 'en-US'])
        first_address_id = user_addresses[0].id
        records = set()
        records.add(email + first_name + last_name + status + telephone)

        # Create one predictable record.
        test_user = User(
            address_id=first_address_id, email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password), status=status, telephone=telephone)
        db_session.add(test_user)
        db_session.commit()

        # Create as many more random records as required. The set won't allow dups.
        while len(records) < num_records:
            random_address_index = randrange(1, 10)
            current_length = len(records)
            random_address_id = user_addresses[random_address_index].id
            fake_email = fake.email()
            fake_first_name = fake.first_name()
            fake_last_name = fake.last_name()
            fake_password = fake.password()
            fake_status = choice(['Active', 'Banned', 'Inactive', 'Pending'])
            fake_telephone = fake.phone_number()
            records.add(
                fake_email + fake_first_name + fake_last_name + fake_status + fake_telephone)
            if current_length < len(records):
                fake_test_user = User(
                    address_id=random_address_id, email=fake_email, first_name=fake_first_name, last_name=last_name, password=generate_password_hash(fake_password), status=fake_status, telephone=fake_telephone)
                db_session.add(fake_test_user)
                db_session.commit()

        return db_session.query(User).all(), user_addresses
    return f


def test_users_cursor_pagination_first(client, common_query_builder, test_users):
    '''
    Test that forward cursor pagination gives us the expected pagingInfo
    '''
    query = common_query_builder("""{
            items { id }
            paging {
                type
                pages
                total
                startCursor
                endCursor
                hasPreviousPage
                hasNextPage
                page
                limit
            }
        }""")
    num = 10
    num_pages = 2
    users, _addresses = test_users(num * num_pages)
    response = client.post(
        '/api', json={'query': query, 'variables': {
            'paging': {'first': num}
        }})
    json_data = json.loads(response.data)
    page = json_data['data']['users']
    items = page['items']
    paging = page['paging']
    start = from_cursor_hash(paging['startCursor'])
    end = from_cursor_hash(paging['endCursor'])

    assert len(items) == num
    assert paging['hasNextPage'] == True
    assert paging['hasPreviousPage'] == False
    assert start == items[0]['id']
    assert end == items[num - 1]['id']
    assert int(end) - int(start) > 0


def test_users_cursor_pagination_last(client, common_query_builder, test_users):
    query = common_query_builder("""{
            items { id }
            paging {
                type
                pages
                total
                startCursor
                endCursor
                hasPreviousPage
                hasNextPage
                page
                limit
            }
        }""")
    num = 10
    num_pages = 2
    users, _addresses = test_users(num * num_pages)
    response = client.post(
        '/api', json={'query': query, 'variables': {
            'paging': {
                'last': num,
            }
        }})
    json_data = json.loads(response.data)
    page = json_data['data']['users']
    items = page['items']
    paging = page['paging']
    start = from_cursor_hash(paging['startCursor'])
    end = from_cursor_hash(paging['endCursor'])

    assert len(items) == num
    assert paging['hasNextPage'] == False
    assert paging['hasPreviousPage'] == True
    assert start == items[0]['id']
    assert end == items[num - 1]['id']


def test_users_cursor_distinct_pagination(client, common_query_builder, test_users):
    query = common_query_builder("""{
            items { id }
            paging { page }
        }""")
    page_num = 2
    num = 10
    num_pages = 3
    users, _addresses = test_users(num * num_pages)
    response = client.post(
        '/api', json={'query': query, 'variables': {
            'paging': {
                'page': page_num,
                'first': num,
            },
            'distinct': True
        }})
    json_data = json.loads(response.data)
    page = json_data['data']['users']
    items = page['items']

    assert len(items) == num
    assert page_num == page['paging']['page']


def test_users_unique_query(
        client, common_query_builder, test_users, email, first_name, last_name, status, telephone):
    query = common_query_builder("""{
            items {
                addressId
                email
                firstName
                lastName
                status
                telephone
            }
            paging { page }
        }""")
    num = 10
    num_pages = 2
    users, addresses = test_users(num * num_pages)
    address_id = addresses[0].id
    response = client.post('/api', json={'query': query, 'variables': {
        'addressId': [address_id],
        'email': email,
        'firstName': [first_name],
        'lastName': [last_name],
        'status': [status],
        'telephone': [telephone]
    }})

    json_data = json.loads(response.data)
    page = json_data['data']['users']
    results = page['items']

    assert isinstance(results, list)
    assert len(results) == 1
    for result in results:
        assert result['addressId'] == str(address_id)
        assert result['email'] == email
        assert result['firstName'] == first_name
        assert result['lastName'] == last_name
        assert result['status'] == status
        assert result['telephone'] == telephone


def test_users_query_with_no_arguments(
        client, common_query_builder, test_users, address_1, email, first_name, last_name, status, telephone):
    query = common_query_builder("""{
            items {
                addressId
                email
                firstName
                lastName
                status
                telephone
            }
            paging { page }
        }""")
    num = 10
    num_pages = 1
    users = test_users(num * num_pages)
    response = client.post('/api', json={'query': query})
    json_data = json.loads(response.data)
    page = json_data['data']['users']
    results = page['items']
    assert isinstance(results, list)
    assert len(results) == 10
    for result in results:
        assert type(result['addressId']) is str
        assert type(result['email']) is str
        assert type(result['firstName']) is str
        assert type(result['lastName']) is str
        assert type(result['status']) is str
        assert type(result['telephone']) is str
