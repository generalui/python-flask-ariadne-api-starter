from sqlalchemy import and_
from sqlalchemy.orm import aliased
from api import db
from api.db_models import Address, User
from .general_resolvers import get_selected, get_value
from .address import build_address_graphql_response
from .paging_utils import get_pagination_queries, Paging

simple_user_request_fields = {'id',
                              'addressId',
                              'email',
                              'firstName',
                              'lastName',
                              'password',
                              'prefix',
                              'status',
                              'telephone',
                              'created',
                              'modified'}

user_request_fields = simple_user_request_fields.union({'addresses'})


def build_user_graphql_response(user):
    return {
        'id': get_value(user, 'id'),
        'address': build_address_graphql_response(user),
        'addressId': get_value(user, 'address_id'),
        'email': get_value(user, 'email'),
        'firstName': get_value(user, 'first_name'),
        'lastName': get_value(user, 'last_name'),
        'prefix': get_value(user, 'prefix'),
        'status': get_value(user, 'status'),
        'telephone': get_value(user, 'telephone'),
        'created': get_value(user, 'created'),
        'modified': get_value(user, 'modified')
    }


def build_users_query(
        requested, address_requested, distinct=False, paging=Paging.DEFAULT, address_id=None, email=None, first_name=None, last_name=None, prefix=None, status=None, telephone=None):
    """
    Builds a SQL request.

    All positional arguments are required. Positional arguments are:
        1st position - a set of the requested fields at the root of the graphql request
        2nd position - a set of the requested fields in the 'address' node of the graphql request. If 'address' is not requested, this will be an empty set.

    All keyword arguments are optional. Keyword arguments are:
        `distinct` - a boolean, indicates whether duplicate records should be filtered out
        `paging` - a dict containing pagination metadata
        `address_id` - a list of strings
        `first_name` - a list of strings
        `last_name` - a list of strings
        `prefix` - a list of UserPrefixEnum values
        `status` - a list of UserStatusEnum values
        `telephone` - a list of strings
    """
    session = db.session

    user = aliased(User, name='u')
    address = aliased(Address, name='a')

    core_field_mapping = {
        'id': user.id.label('id'),
        'addressId': user.address_id.label('address_id'),
        'email': user.email.label('email'),
        'firstName': user.first_name.label('first_name'),
        'lastName': user.last_name.label('last_name'),
        'password': user.password.label('password'),
        'prefix': user.prefix.label('prefix'),
        'status': user.status.label('status'),
        'telephone': user.telephone.label('telephone'),
        'created': user.created_at.label('created'),
        'modified': user.updated_at.label('modified')}

    address_field_mapping = {
        'id': address.id.label('address_id'),
        'address1': address.address_1.label('address_1'),
        'address2': address.address_2.label('address_2'),
        'city': address.city.label('city'),
        'country': address.country.label('country'),
        'state': address.state.label('state'),
        'zipcode': address.zipcode.label('zipcode'),
        'created': address.created_at.label('address_created'),
        'modified': address.updated_at.label('address_modified')}

    core = get_selected(requested, core_field_mapping)
    core |= get_selected(address_requested, address_field_mapping)

    if not distinct and 'id' not in requested:
        # Add the id as a cursor if not selecting distinct and it is not already added.
        core.add(user.id.label('id'))

    query = session.query(*core)
    query = query.select_from(user)

    if address_id:
        query = query.filter(user.address_id.in_(address_id))

    if email:
        query = query.filter(user.email.in_(email))

    if first_name:
        query = query.filter(user.first_name.in_(first_name))

    if last_name:
        query = query.filter(user.last_name.in_(last_name))

    if prefix:
        query = query.filter(user.prefix.in_(prefix))

    if status:
        query = query.filter(user.status.in_(status))

    if telephone:
        query = query.filter(user.telephone.in_(telephone))

    if 'address' in requested:
        query = query.join(address, address.id == user.address_id)

    return (query, user)


def build_users_request(requested, address_requested, **kwargs):
    """
    Builds a SQL request.

    All positional arguments are required. Positional arguments are:
        1st position - a set of the requested fields at the root of the graphql request
        2nd position - a set of the requested fields in the 'address' node of the graphql request. If 'address' is not requested, this will be an empty set.

    All keyword arguments are optional. Keyword arguments are:
        `distinct` - a boolean, indicates whether duplicate records should be filtered out
        `paging` - a dict containing pagination metadata
        `address_id` - a list of strings
        `first_name` - a list of strings
        `last_name` - a list of strings
        `prefix` - a list of UserPrefixEnum values
        `status` - a list of UserStatusEnum values
        `telephone` - a list of strings
    """
    distinct = kwargs.pop('distinct', False)
    paging = kwargs.pop('paging', Paging.DEFAULT)

    query, alias = build_users_query(requested, address_requested, **kwargs)

    return get_pagination_queries(query, paging, distinct, cursor_field=alias.id)
