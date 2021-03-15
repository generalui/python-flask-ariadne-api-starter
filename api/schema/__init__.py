from ariadne import EnumType, load_schema_from_path, make_executable_schema, ObjectType, ScalarType
import os
import decimal
from api.directives import IsAuthenticatedDirective
from api.resolvers import resolve_add_address, resolve_addresses, resolver_login, resolve_register_user, resolve_test, resolve_users
from api.enums import PagingType, user_prefix_enum, user_status_enum

schema_dirname, _filename = os.path.split(os.path.abspath(__file__))

### Import GraphQl schemas/ ###
# Base types
base_types = load_schema_from_path(schema_dirname + '/base.graphql')
# The root query type
root_query = load_schema_from_path(schema_dirname + '/root.query.graphql')
# The root mutation type
root_mutation = load_schema_from_path(
    schema_dirname + '/root.mutation.graphql')
# Directives
directives_def = load_schema_from_path(schema_dirname + '/directives.graphql')
# Paging
paging_types = load_schema_from_path(schema_dirname + '/paging.graphql')
# Types
address_types = load_schema_from_path(schema_dirname + '/address.graphql')
test_types = load_schema_from_path(schema_dirname + '/test.graphql')
user_types = load_schema_from_path(schema_dirname + '/user.graphql')

# Create the definitions list.
type_defs = [
    base_types,
    root_query,
    root_mutation,
    directives_def,
    paging_types,
    address_types,
    test_types,
    user_types
]

# Initialize custom scalars.
user_prefix_enum_scalar = ScalarType('UserPrefixEnum')


@user_prefix_enum_scalar.serializer
def serialize_user_prefix_enum(value):
    return value if value in user_prefix_enum.enums else None


user_status_enum_scalar = ScalarType('UserStatusEnum')


@user_status_enum_scalar.serializer
def serialize_user_status_enum(value):
    return value if value in user_status_enum.enums else None


# Initialize schema objects (general).
mutation = ObjectType('Mutation')
root = ObjectType('Query')

# Associate resolvers with query fields.
root.set_field('addresses', resolve_addresses)
root.set_field('test', resolve_test)
root.set_field('testAuth', resolve_test)
root.set_field('users', resolve_users)

# Associate resolvers with mutation fields.
mutation.set_field('addAddress', resolve_add_address)
mutation.set_field('login', resolver_login)
mutation.set_field('register', resolve_register_user)

# Create Directive associations
directives = {'isAuthenticated': IsAuthenticatedDirective}

# Create schema object list
schema_objects = [
    mutation,
    root,
    EnumType('PagingType', PagingType),
    ObjectType('LoginPayload'),
    ObjectType('Paging'),
    ObjectType('ResponsePayload'),
    ObjectType('TestFields'),
    ObjectType('TestHeaders'),
    ObjectType('TestPage'),
    ObjectType('User'),
    user_prefix_enum_scalar,
    user_status_enum_scalar
]

schema = make_executable_schema(
    type_defs, schema_objects, directives=directives)
