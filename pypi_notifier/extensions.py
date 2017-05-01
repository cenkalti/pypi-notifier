from flask_caching import Cache
from flask_github import GitHub
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

db = SQLAlchemy()
cache = Cache()
github = GitHub()
sentry = Sentry()
