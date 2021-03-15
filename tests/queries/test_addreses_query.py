import json
import pytest
from os import getenv
from faker import Faker
from tests import NoneType
from api.resolvers.resolver_helpers.paging_utils import from_cursor_hash, to_cursor_hash, Paging
from api.db_models import Address


@pytest.fixture(scope='module')
def common_query_builder():
    def f(query_fields):
        return """query Addresses(
            $paging: PagingInput
            $distinct:Boolean
            $address1: [String!]
            $address2: [String!]
            $city: [String!]
            $country: [String!]
            $state: [String!]
            $zipcode: [String!]
        ) {
            addresses(
                paging: $paging
                distinct: $distinct
                address1: $address1
                address2: $address2
                city: $city
                country: $country
                state: $state
                zipcode: $zipcode
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

        return db_session.query(Address).all()
    return f


def test_addresses_cursor_pagination_first(client, common_query_builder, test_addresses):
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
    addresses = test_addresses(num * num_pages)
    response = client.post(
        '/api', json={'query': query, 'variables': {
            'paging': {'first': num}
        }})
    json_data = json.loads(response.data)
    page = json_data['data']['addresses']
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


def test_addresses_cursor_pagination_last(client, common_query_builder, test_addresses):
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
    addresses = test_addresses(num * num_pages)
    response = client.post(
        '/api', json={'query': query, 'variables': {
            'paging': {
                'last': num,
                'before': to_cursor_hash(1000)
            }
        }})
    json_data = json.loads(response.data)
    page = json_data['data']['addresses']
    items = page['items']
    paging = page['paging']
    start = from_cursor_hash(paging['startCursor'])
    end = from_cursor_hash(paging['endCursor'])

    assert len(items) == num
    assert paging['hasNextPage'] == False
    assert paging['hasPreviousPage'] == True
    assert start == items[0]['id']
    assert end == items[num - 1]['id']


def test_addresses_cursor_distinct_pagination(client, common_query_builder, test_addresses):
    query = common_query_builder("""{
            items { id }
            paging { page }
        }""")
    page_num = 2
    num = 10
    num_pages = 3
    addresses = test_addresses(num * num_pages)
    response = client.post(
        '/api', json={'query': query, 'variables': {
            'paging': {
                'page': page_num,
                'first': num,
            },
            'distinct': True
        }})
    json_data = json.loads(response.data)
    page = json_data['data']['addresses']
    items = page['items']

    assert len(items) == num
    assert page_num == page['paging']['page']


def test_addresses_unique_query(
        client, common_query_builder, test_addresses, address_1, address_2, city, country, state, zipcode):
    query = common_query_builder("""{
            items {
                address1
                address2
                city
                country
                state
                zipcode
            }
            paging { page }
        }""")
    num = 10
    num_pages = 2
    addresses = test_addresses(num * num_pages)
    response = client.post('/api', json={'query': query, 'variables': {
        'address_1': [address_1],
        'address_2': address_2,
        'city': [city],
        'country': [country],
        'state': [state],
        'zipcode': [zipcode]
    }})

    json_data = json.loads(response.data)
    page = json_data['data']['addresses']
    results = page['items']

    assert isinstance(results, list)
    assert len(results) == 1
    for result in results:
        assert result['address1'] == address_1
        assert result['address2'] == address_2
        assert result['city'] == city
        assert result['country'] == country
        assert result['state'] == state
        assert result['zipcode'] == zipcode


def test_addresses_query_with_no_arguments(
        client, common_query_builder, test_addresses, address_1, address_2, city, country, state, zipcode):
    query = common_query_builder("""{
            items {
                address1
                address2
                city
                country
                state
                zipcode
            }
            paging { page }
        }""")
    num = 10
    num_pages = 1
    addresses = test_addresses(num * num_pages)
    response = client.post('/api', json={'query': query})
    json_data = json.loads(response.data)
    page = json_data['data']['addresses']
    results = page['items']
    assert isinstance(results, list)
    assert len(results) == 10
    for result in results:
        assert type(result['address1']) is str
        assert type(result['address2']) is str
        assert type(result['city']) is str
        assert type(result['country']) is str
        assert type(result['state']) is str
        assert type(result['zipcode']) is str
