import base64
import logging
from datetime import datetime
from pkg_resources import parse_requirements
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from pypi_notifier import db, github
from pypi_notifier.models.user import User
from pypi_notifier.models.package import Package
from pypi_notifier.models.mixin import ModelMixin


logger = logging.getLogger(__name__)


class Repo(db.Model, ModelMixin):
    __tablename__ = 'repos'
    __table_args__ = (
        UniqueConstraint('user_id', 'github_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    github_id = db.Column(db.Integer)
    name = db.Column(db.String(200))
    last_check = db.Column(db.DateTime)
    last_modified = db.Column(db.String(40))

    packages = association_proxy('requirements', 'package')

    def __init__(self, github_id, user):
        self.github_id = github_id
        self.user = user

    def __repr__(self):
        return "<Repo %s>" % self.name

    @classmethod
    def update_all_repos(cls):
        for repo in cls.query.all():
            repo.update_requirements()
            db.session.commit()

    def update_requirements(self):
        """
        Fetches the content of the requirements.txt files from GitHub,
        parses the file and adds each requirement to the repo.

        """
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
        contents = self.fetch_requirements()
        if contents:
            contents = strip_index_url(contents)
            if contents:
                for req in parse_requirements(contents):
                    yield req.project_name.lower(), req.specs

    def fetch_requirements(self):
        logger.info("Fetching requirements of repo: %s", self)
        path = 'repos/%s/contents/requirements.txt' % self.name
        headers = None
        if self.last_modified:
            headers = {'If-Modified-Since': self.last_modified}

        params = {'access_token': self.user.github_token}
        response = github.raw_request('GET', path,
                                      headers=headers, params=params)
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
        elif response.status_code == 404:
            # requirements.txt file is not found.
            # Remove the repo so we won't check it again.
            db.session.delete(self)
        else:
            raise Exception("Unknown status code: %s" % response.status_code)


def strip_index_url(s):
    """
    Returns a new str without the --index-url opiton line.

    pkg_resources.parse_requirements() cannot parse the file if it contains
    an option for index url. Example: "-i http://simple.crate.io/"

    """
    is_index_url_line = lambda x: x.startswith(('-i', '--index-url'))
    return '\n'.join(l for l in s.splitlines() if not is_index_url_line(l))
