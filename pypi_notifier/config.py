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
        self.WARNINGS = 'error'


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
        self.WARNINGS = 'error'


class heroku(object):
    def __init__(self):
        self.SECRET_KEY = os.environ['SECRET_KEY']
        self.CACHE_TYPE = "memcached"
        self.CACHE_MEMCACHED_SERVERS = (os.environ['MEMCACHEDCLOUD_SERVERS'], )
        self.CACHE_MEMCACHED_USERNAME = os.environ['MEMCACHEDCLOUD_USERNAME']
        self.CACHE_MEMCACHED_PASSWORD = os.environ['MEMCACHEDCLOUD_PASSWORD']
        self.SQLALCHEMY_DATABASE_URI = os.environ['HEROKU_POSTGRESQL_COPPER_URL']
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
        self.GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']
        self.SENTRY_DSN = os.environ['SENTRY_DSN']
        self.POSTMARK_APIKEY = os.environ['POSTMARK_APIKEY']
        self.WARNINGS = 'default'
