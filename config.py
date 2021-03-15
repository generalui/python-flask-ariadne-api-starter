from os import environ, getenv, path
import logging


def get_database_uri(test=False):
    HOST = environ['POSTGRES_HOST_TEST'] if test else environ['POSTGRES_HOST']
    PORT = getenv('POSTGRES_PORT_TEST') if test else getenv('POSTGRES_PORT')
    if PORT and PORT != 'None':
        HOST = HOST + ':' + PORT
    POSTGRES = {
        'user': environ['POSTGRES_USER_TEST'] if test else environ['POSTGRES_USER'],
        'pw': environ['POSTGRES_PASSWORD_TEST'] if test else environ['POSTGRES_PASSWORD'],
        'db': environ['POSTGRES_DB_TEST'] if test else environ['POSTGRES_DB'],
        'host': HOST,
    }
    return 'postgresql://%(user)s:%(pw)s@%(host)s/%(db)s' % POSTGRES


BASE_PATH = path.dirname(path.abspath(__file__))


class Config(object):
    LOG_APP_NAME = getenv('LOG_APP_NAME') or 'api'
    LOG_COPIES = 10
    LOG_DIR = path.join(BASE_PATH, '.logs', 'development')
    LOG_FILE = path.join(LOG_DIR, 'server.log')
    LOG_INTERVAL = 1
    LOG_LEVEL = getenv('LOG_LEVEL') or logging.DEBUG
    LOG_TIME_INT = 'D'
    LOG_TYPE = getenv('LOG_TYPE') or 'TimedRotatingFile'
    LOG_WWW_NAME = getenv('LOG_WWW_NAME') or 'api-access'
    PROFILE = True
    PROFILE_PATH = path.join(BASE_PATH, '.profiles')
    SECRET_KEY = getenv('SECRET_KEY') or 'some_real_good_secret'
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SQLALCHEMY_ECHO = True


class TestConfig(Config):
    LOG_DIR = path.join(
        BASE_PATH, '.logs', 'test',
        environ['FLASK_ENV'] if environ['FLASK_ENV'] != 'test' else ''
    )
    LOG_LEVEL = getenv('LOG_LEVEL') or logging.INFO
    PROFILE = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = get_database_uri(test=True)
    TESTING = True


class ProdConfig(Config):
    LOG_DIR = path.join(BASE_PATH, '.logs', 'production')
    LOG_LEVEL = getenv('LOG_LEVEL') or logging.WARN
    LOG_TYPE = 'stream'
    PROFILE = False
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_ECHO = False


class StagingConfig(ProdConfig):
    LOG_DIR = path.join(BASE_PATH, '.logs', 'staging')
    LOG_LEVEL = getenv('LOG_LEVEL') or logging.INFO


def get_config(test=False):
    FLASK_ENV = environ['FLASK_ENV']
    if (test or FLASK_ENV == 'test'):
        return TestConfig
    if FLASK_ENV == 'development':
        return Config
    elif FLASK_ENV == 'staging':
        return StagingConfig
    else:
        return ProdConfig
