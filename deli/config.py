class BaseConfig(object):
    SECRET_KEY = 'Seninle kim kalacak, isiklar kapaninca?'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/deli.db'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/deli.db'
    GITHUB_CLIENT_ID = '18939ccf4d67ee469348'
    GITHUB_CLIENT_SECRET = '9dc292057d3ded1ef801b1a38922cb3f2170fa1d'
    CALLBACK_URL = 'http://localhost:5000/github-callback'


class TestingConfig(BaseConfig):
    TESTING = True
    CSRF_ENABLED = False
    DEBUG_TB_ENABLED = False


class ProductionConfig(BaseConfig):
    GITHUB_CLIENT_ID = 'a64036373119cc126aab'
    GITHUB_CLIENT_SECRET = 'd59137d90c3f3d062b2f32509f9e258a3af6a65a'
    CALLBACK_URL = 'http://deli.cenkalti.net/github-callback'
