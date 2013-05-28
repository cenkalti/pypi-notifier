class BaseConfig(object):
    SECRET_KEY = 'insecure'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/deli.db'
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = '/tmp'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/deli.db'
    GITHUB_CLIENT_ID = ''
    GITHUB_CLIENT_SECRET = ''
    GITHUB_CALLBACK_URL = 'http://localhost:5000/github-callback'


class TestingConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False
    DEBUG_TB_ENABLED = False


class ProductionConfig(BaseConfig):
    SECRET_KEY = ''
    GITHUB_CLIENT_ID = ''
    GITHUB_CLIENT_SECRET = ''
    GITHUB_CALLBACK_URL = 'http://www.pypi-notifier.org/github-callback'
