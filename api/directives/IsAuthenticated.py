from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver, GraphQLError
from api.constants.error_messages import NOT_AUTHENTICATED


class IsAuthenticatedDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        def resolve_is_authenticated(obj, info, **kwargs):
            user = info.context.get('user')
            error = info.context.get('error')
            if user is None:
                raise GraphQLError(message=error)
            result = original_resolver(obj, info, **kwargs)
            return result
        field.resolve = resolve_is_authenticated
        return field
