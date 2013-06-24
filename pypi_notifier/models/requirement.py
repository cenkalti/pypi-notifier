import logging
from pypi_notifier import db
from pypi_notifier.models.repo import Repo
from pypi_notifier.models.package import Package
from pypi_notifier.models.mixin import ModelMixin
from pypi_notifier.models.util import JSONType


logger = logging.getLogger(__name__)


class Requirement(db.Model, ModelMixin):
    __tablename__ = 'requirements'

    repo_id = db.Column(db.Integer,
                        db.ForeignKey(Repo.id),
                        primary_key=True)
    package_id = db.Column(db.Integer,
                           db.ForeignKey(Package.id),
                           primary_key=True)
    specs = db.Column(JSONType())

    package = db.relationship(
        Package,
        backref=db.backref('repos', cascade='all, delete-orphan'))
    repo = db.relationship(
        Repo,
        backref=db.backref('requirements', cascade="all, delete-orphan"))

    def __init__(self, repo, package, specs=None):
        self.repo = repo
        self.package = package
        self.specs = specs

    def __repr__(self):
        return "<Requirement: %s requires %s with %s>" % (
            self.repo.name, self.package.name, self.specs)

    @property
    def version(self):
        logger.debug("Finding version of %s", self)
        for specifier, version in self.specs:
            logger.debug("specifier: %s, version: %s", specifier, version)
            if specifier in ('==', '>='):
                return version
