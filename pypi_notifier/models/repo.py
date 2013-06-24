import base64
import logging
from datetime import datetime
from pkg_resources import parse_requirements
from sqlalchemy.ext.associationproxy import association_proxy
from pypi_notifier import db, github
from pypi_notifier.models.user import User
from pypi_notifier.models.package import Package
from pypi_notifier.models.mixin import ModelMixin


logger = logging.getLogger(__name__)


class Repo(db.Model, ModelMixin):
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

    def __repr__(self):
        return "<Repo %s>" % self.name

    def update_requirements(self):
        for poject_name, specs in self.parse_requirements_file():
            self.add_new_requirement(poject_name, specs)

        self.last_check = datetime.utcnow()

    def add_new_requirement(self, name, specs):
        from pypi_notifier.models.requirement import Requirement
        package = Package.get_or_create(name=name)
        requirement = Requirement.get_or_create(repo=self, package=package)
        requirement.specs = specs
        self.requirements.append = requirement

    def parse_requirements_file(self):
        contents = self.fetch_changed_requirements()
        if contents:
            requirements = parse_requirements(contents)
            for each in requirements:
                name = each.project_name.lower()
                yield name, each.specs

    def fetch_changed_requirements(self):
        headers = {'If-Modified-Since': self.last_modified}
        return self.fetch_requirements(headers)

    def fetch_requirements(self, headers=None):
        logger.info("Fetching requirements of repo: %s", self)
        path = 'repos/%s/contents/requirements.txt' % self.name
        response = github.raw_request('GET', path, headers=headers)
        logger.debug("Response: %s", response)
        if response.status_code == 200:
            self.last_modified = response.headers['Last-Modified']
            response = response.json()
            if response['encoding'] == 'base64':
                return base64.b64decode(response['content'])
            else:
                raise Exception("Unknown encoding: %s" % response['encoding'])
        elif response.status_code == 304:
            return None
        else:
            raise Exception("Unknown status code: %s", response.status_code)
