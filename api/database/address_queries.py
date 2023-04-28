from api.db_models import Address
from .database_helpers import build_general_query


address_core_fields = [
    'id',
    'address_1',
    'address_2',
    'created_at',
    'city',
    'country',
    'state',
    'updated_at',
    'zipcode'
]

address_related_fields = []


def return_address_query(*args, model=Address):
    return build_general_query(
        model, args=args,
        accepted_option_args=address_related_fields,
        accepted_query_args=address_core_fields)
