import os

from tempfile import gettempdir

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://'     # in memory


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    DATABASE_URI = 'sqlite://{0}/myapp.db'.format(gettempdir())
    SECRET_KEY = '@DEVKEY@'


class ProductionConfig(BaseConfig):
    SECRET_KEY = '@PRODKEY@'


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SECRET_KEY = '@TESTKEY@'


config = {
    'dev':  'myapp.config.DevelopmentConfig',
    'test': 'myapp.config.TestConfig',
    'prod': 'myapp.config.ProductionConfig',
    'default': 'myapp.config.DevelopmentConfig',
}


def configure_app(app):
    selected_config = os.getenv('MYAPP_CONFIG', 'default')
    app.config.from_object(config[selected_config])
    app.config.from_pyfile('settings.cfg', silent=True)
