import logging
from os import getenv
from app import app

environment = getenv('FLASK_ENV') or 'development'
print(f'Starting server with {environment} config')

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    HOST = '0.0.0.0'
    PORT = getenv('FLASK_RUN_PORT') or '5000'
    DEBUG = getenv('FLASK_DEBUG_MODE') or None
    SSL_ENABLED = getenv('SSL_ENABLED') or False
    SSL_CONTEXT = 'adhoc'

    if SSL_ENABLED:
        try:
            print(
                f'Available at https://localhost:{PORT}/graphiql and https://localhost:{PORT}/api')
            app.run(host=HOST, port=PORT, debug=DEBUG, ssl_context=SSL_CONTEXT)
        except Exception as e:
            logger.error(f'Error: {e}')
            logger.info(f'SSL Context: {SSL_CONTEXT}')
    else:
        print(
            f'Available at http://localhost:{PORT}/graphiql and http://localhost:{PORT}/api')
        app.run(host=HOST, port=PORT, debug=DEBUG)
