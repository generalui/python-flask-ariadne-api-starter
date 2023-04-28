from api import db
from .resolver_helpers import build_address_graphql_response, build_address_request, address_request_fields, get_requested
from .resolver_helpers.paging_utils import paginate, Paging, paging_fields


def resolve_addresses(
        _,
        info,
        distinct=False,
        paging=None,
        address1=None,
        address2=None,
        city=None,
        country=None,
        state=None,
        zipcode=None):
    # The selection is nested under the 'items' node.
    requested = get_requested(
        info, requested_field_mapping=address_request_fields, child_node='items')

    paging = paging if paging else Paging.DEFAULT

    query, count_query = build_address_request(requested, distinct=distinct, paging=paging,
                                               address_1=address1, address_2=address2, city=city, country=country, state=state, zipcode=zipcode)

    pagination_requested = get_requested(info, paging_fields, 'paging')
    return paginate(
        query, count_query, paging, distinct, build_address_graphql_response, pagination_requested)
