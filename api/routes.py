from ariadne import graphql_sync
from ariadne.contrib.tracing.apollotracing import ApolloTracingExtensionSync
from ariadne.explorer import ExplorerGraphiQL
from flask import current_app, jsonify, request
import os
from .context import get_user_context
from .main import bp
from .schema import schema


# Retrieve HTML for the GraphiQL.
# If explorer implements logic dependant on current request,
# change the html(None) call to the html(request)
# and move this line to the graphql_explorer function.
explorer_html = ExplorerGraphiQL().html(None)


@bp.route('/graphiql', methods=['GET'])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep in mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return explorer_html, 200


@bp.route('/graphiql', methods=['POST'])
@bp.route('/api', methods=['POST'])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # By default, no extensions.
    # If the FLASK_ENV environment variable is set to something
    # other than 'production', enable Apollo Tracing.
    extensions = None
    if ('FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] != 'production'):
        extensions = [ApolloTracingExtensionSync]

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=get_user_context(request),
        debug=current_app.debug,
        extensions=extensions
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


@bp.route('/healthcheck')
def healthcheck():
    status_code = 200
    return jsonify({'status': status_code}), status_code
