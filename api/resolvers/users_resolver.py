from api import db
from .resolver_helpers import address_request_fields, build_user_graphql_response, build_users_request, user_request_fields, get_requested, get_selection_set
from .resolver_helpers.paging_utils import paginate, Paging, paging_fields


def resolve_users(
        _,
        info,
        distinct=False,
        paging=None,
        addressId=None,
        email=None,
        firstName=None,
        lastName=None,
        status=None,
        telephone=None):
    # The selection is nested under the 'items' node.
    selection_set = get_selection_set(info=info, child_node='items')
    requested = get_requested(
        selection_set=selection_set, requested_field_mapping=user_request_fields)

    address_requested = get_requested(
        selection_set=selection_set, requested_field_mapping=address_request_fields, child_node='address')

    paging = paging if paging else Paging.DEFAULT

    query, count_query = build_users_request(requested, address_requested, distinct=distinct, paging=paging,
                                             address_id=addressId, email=email, first_name=firstName, last_name=lastName, status=status, telephone=telephone)

    pagination_requested = get_requested(info, paging_fields, 'paging')
    return paginate(
        query, count_query, paging, distinct, build_user_graphql_response, pagination_requested)
