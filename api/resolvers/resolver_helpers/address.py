from sqlalchemy import and_
from sqlalchemy.orm import aliased
from api import db
from api.db_models import Address
from .general_resolvers import get_selected, get_value
from .paging_utils import get_pagination_queries, Paging

address_request_fields = {'id',
                          'address1',
                          'address2',
                          'city',
                          'country',
                          'state',
                          'zipcode',
                          'created',
                          'modified'}


def build_address_graphql_response(address):
    return {
        'id': get_value(address, 'address_id', default=get_value(address, 'id')),
        'address1': get_value(address, 'address_1'),
        'address2': get_value(address, 'address_2'),
        'city': get_value(address, 'city'),
        'country': get_value(address, 'country'),
        'state': get_value(address, 'state'),
        'zipcode': get_value(address, 'zipcode'),
        'created': get_value(address, 'address_created', default=get_value(address, 'created')),
        'modified': get_value(address, 'address_modified', default=get_value(address, 'modified'))
    }


def build_address_request(requested, distinct=False, paging=Paging.DEFAULT, address_1=None, address_2=None, city=None, country=None, state=None, zipcode=None):
    """
    Builds a SQL request.

    All positional arguments are required. Positional arguments are:
        1st position - a set of the requested fields at the root of the graphql request

    All keyword arguments are optional. Keyword arguments are:
        `distinct` - a boolean, indicates whether duplicate records should be filtered out
        `paging` - a dict containing pagination metadata
        `address_1` - a list of strings
        `address_2` - a list of strings
        `city` - a list of strings
        `country` - a list of strings
        `state` - a list of strings
        `zipcode` - a list of strings
    """
    session = db.session

    # Make an alias for the Model so that it may be re-used.
    address = aliased(Address, name='a')

    core_field_mapping = {'id': address.id.label('id'),
                          'address1': address.address_1.label('address_1'),
                          'address2': address.address_2.label('address_2'),
                          'city': address.city.label('city'),
                          'country': address.country.label('country'),
                          'state': address.state.label('state'),
                          'zipcode': address.zipcode.label('zipcode'),
                          'created': address.created_at.label('created'),
                          'modified': address.updated_at.label('modified')}

    core = get_selected(requested, core_field_mapping)

    if not distinct and 'id' not in requested:
        # Add the id as a cursor if not selecting distinct and it is not already added.
        core.add(address.id.label('id'))

    query = session.query(*core)
    query = query.select_from(address)

    if address_1:
        query = query.filter(address.address_1.in_(address_1))

    if address_2:
        query = query.filter(address.address_2.in_(address_2))

    if city:
        query = query.filter(address.city.in_(city))

    if country:
        query = query.filter(address.country.in_(country))

    if state:
        query = query.filter(address.state.in_(state))

    if zipcode:
        query = query.filter(address.zipcode.in_(zipcode))

    return get_pagination_queries(query, paging, distinct, cursor_field=address.id)
