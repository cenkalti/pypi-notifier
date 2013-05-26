import base64
import xmlrpclib
from pkg_resources import parse_requirements

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

from cache import cache
from github import github

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

    def __str__(self):
        return self.name

    def __repr__(self):
        return "User(%r)" % self.github_token

    def update_from_github(self):
        user = github.get('user')
        self.name = user['login']
        self.email = user['email']


class Repo(db.Model):
    __tablename__ = 'repos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    github_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(200))
    last_check = db.Column(db.DateTime)
    last_modified = db.Column(db.String(40))

    packages = association_proxy('requirements', 'package')

    def __init__(self, github_id, user_id):
        self.github_id = github_id
        self.user_id = user_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Repo(%r, %r)" % (self.github_id, self.user_id)

    @staticmethod
    def find_version(requirement):
        for specifier, version in requirement.specs:
            if specifier in ('==', '>='):
                return version

    def update_requirements(self):
        for poject_name, version in self.parse_changed_requirements():
            self.add_new_project(poject_name, version)

    def add_new_project(self, name, version):
        package = Package.get_or_create(name)
        requirement = Requirement.get_or_create(self, package, version)
        requirement.version = version
        self.requirements.append = requirement

    def parse_changed_requirements(self):
        contents = self.fetch_changed_requirements()
        if contents:
            requirements = parse_requirements(contents)
            for each in requirements:
                name = each.project_name.lower()
                version = Repo.find_version(each)
                yield name, version

    def fetch_changed_requirements(self):
        path = 'repos/%s/contents/requirements.txt' % self.name
        headers = {}
        # if self.last_modified:
        #     headers['If-Modified-Since'] = self.last_modified
        response = github.raw_request('GET', path, headers=headers)
        if response.status_code == 200:
            self.last_modified = response.headers['Last-Modified']
            response = response.json()
            if response['encoding'] == 'base64':
                return base64.b64decode(response['content'])
            else:
                raise Exception("Unknown encoding: %s" % response['encoding'])


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    latest_version = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)

    pypi = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')

    def __init__(self, name):
        self.name = name.lower()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Package(%r)" % self.name

    @classmethod
    def get_or_create(cls, name):
        return cls.query.filter(cls.name == name).first() or cls(name)

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


class Requirement(db.Model):
    __tablename__ = 'requirements'

    repo_id = db.Column(db.Integer, db.ForeignKey(Repo.id),
                        primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey(Package.id),
                           primary_key=True)
    version = db.Column(db.String(20))

    # bidirectional attribute/collection of "repo"/"repo_requirements"
    repo = db.relationship(
        Repo,
        backref=db.backref('requirements', cascade="all, delete-orphan")
    )

    # reference to the "Package" object
    package = db.relationship('Package')

    def __init__(self, repo, package, version):
        self.repo = repo
        self.package = package
        self.version = version

    def __str__(self):
        return "<Requirement repo=%s package=%s version=%s>" % (
            self.repo, self.package, self.version)

    def __repr__(self):
        return "Package(%r, %r, %r)" % (
            self.repo, self.package, self.version)

    @classmethod
    def get_or_create(cls, repo, package, version):
        req = cls.query.filter(
            cls.repo_id == repo.id,
            cls.package_id == package.id).first()
        if req is None:
            req = cls(repo, package, version)

        req.version = version
        return req
