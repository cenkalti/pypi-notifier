import xmlrpclib

from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

from cache import cache

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    github_id = db.Column(db.Integer, unique=True)
    github_token = db.Column(db.Integer)

    repos = db.relationship('Repo', backref='user')

    def __init__(self, github_token):
        self.github_token = github_token

    def update_from_github(self):
        r, user = current_app.github.get_resource('user')
        self.name = user['login']
        self.email = user['email']


class Repo(db.Model):
    __tablename__ = 'repos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    github_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(200))
    last_check = db.Column(db.DateTime)
    # last_hash = db.Column()
    # last_etag = db.Column()

    requirements = db.relationship('Package', secondary='requirements',
                                   backref='repos')

    def __init__(self, github_id, user_id):
        self.github_id = github_id
        self.user_id = user_id


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    latest_version = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)

    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')

    def __init__(self, name):
        self.name = name

    @classmethod
    @cache.cached(timeout=3600, key_prefix='all_packages')
    def get_all_names(cls):
        packages = cls.pypi.list_packages()
        packages = filter(None, packages)
        return {name.lower(): name for name in packages}

    @property
    def original_name(self):
        return self.get_all_names()[self.name.lower()]

    def find_latest_version(self):
        return self.pypi.package_releases(self.original_name)[0]


requirements = db.Table(
    'requirements',
    db.Column('repo_id', db.Integer, db.ForeignKey(Repo.id)),
    db.Column('package_id', db.Integer, db.ForeignKey(Package.id)),
    db.Column('required_version', db.String(20)),
)
