import os


class development(object):
    def __init__(self):
        self.DEBUG = True
        self.DEBUG_TB_INTERCEPT_REDIRECTS = False
        self.SECRET_KEY = 'insecure'
        self.CACHE_TYPE = 'filesystem'
        self.CACHE_DIR = 'cache'
        self.GITHUB_CLIENT_ID = ''
        self.GITHUB_CLIENT_SECRET = ''
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///pypi_notifier.db'
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False


class testing(object):
    def __init__(self):
        self.TESTING = True
        self.CSRF_ENABLED = False
        self.DEBUG_TB_ENABLED = False
        self.SECRET_KEY = 'insecure'
        self.CACHE_TYPE = 'simple'
        self.GITHUB_CLIENT_ID = 'a'
        self.GITHUB_CLIENT_SECRET = 'b'
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/pypi_notifier.db'
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False


class heroku(object):
    def __init__(self):
        self.SECRET_KEY = os.environ['SECRET_KEY']
        self.CACHE_TYPE = 'redis'
        self.CACHE_REDIS_URL = os.environ['REDIS_URL']
        self.SQLALCHEMY_DATABASE_URI = os.environ['HEROKU_POSTGRESQL_COPPER_URL']
        self.SQLALCHEMY_DATABASE_URI = self.SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
        self.GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']
        self.SENTRY_DSN = os.environ['SENTRY_DSN']
        self.POSTMARK_APIKEY = os.environ['POSTMARK_APIKEY']


def load_config(config_object, object_or_str):
    if isinstance(object_or_str, str):
        object_or_str = globals()[object_or_str]()
    config_object.from_object(object_or_str)
