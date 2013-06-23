import base64
from pkg_resources import parse_requirements
from sqlalchemy.ext.associationproxy import association_proxy
from pypi_notifier import db, github
from pypi_notifier.models.user import User
from pypi_notifier.models.package import Package


class Repo(db.Model):
    __tablename__ = 'repos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    github_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(200))
    last_check = db.Column(db.DateTime)
    last_modified = db.Column(db.String(40))

    packages = association_proxy('requirements', 'package')

    def __init__(self, github_id, user):
        self.github_id = github_id
        self.user = user

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Repo(%r, %r)" % (self.github_id, self.user)

    @staticmethod
    def find_version(requirement):
        for specifier, version in requirement.specs:
            if specifier in ('==', '>='):
                return version

    def update_requirements(self):
        for poject_name, version in self.parse_changed_requirements():
            self.add_new_project(poject_name, version)

    def add_new_project(self, name, version):
        from pypi_notifier.models.requirement import Requirement
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
                if version:
                    yield name, version

    def fetch_changed_requirements(self):
        headers = {'If-Modified-Since': self.last_modified}
        return self.fetch_requirements(headers)

    def fetch_requirements(self, headers=None):
        path = 'repos/%s/contents/requirements.txt' % self.name
        response = github.raw_request('GET', path, headers=headers)
        if response.status_code == 200:
            self.last_modified = response.headers['Last-Modified']
            response = response.json()
            if response['encoding'] == 'base64':
                return base64.b64decode(response['content'])
            else:
                raise Exception("Unknown encoding: %s" % response['encoding'])
