import logging
from verlib import NormalizedVersion as Version, IrrationalVersionError
from pypi_notifier.extensions import db
from pypi_notifier.models.repo import Repo
from pypi_notifier.models.package import Package
from pypi_notifier.models.util import JSONType


logger = logging.getLogger(__name__)


class Requirement(db.Model):
    __tablename__ = 'requirements'

    repo_id = db.Column(db.Integer, db.ForeignKey(Repo.id), primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey(Package.id), primary_key=True)
    specs = db.Column(JSONType())

    package = db.relationship(Package, backref=db.backref('requirements', cascade='all, delete-orphan'))
    repo = db.relationship(Repo, backref=db.backref('requirements', cascade="all, delete-orphan"))

    def __init__(self, repo, package, specs=None):
        self.repo = repo
        self.package = package
        self.specs = specs

    def __repr__(self):
        return "<Requirement: %s requires %s with %s>" % (self.repo.name, self.package.name, self.specs)

    @property
    def required_version(self):
        logger.debug("Finding version of %s", self)
        for specifier, version in self.specs:
            logger.debug("specifier: %s, version: %s", specifier, version)
            if specifier == '==':
                return version

    @property
    def up_to_date(self):
        latest_version = self.package.latest_version
        if not latest_version:
            # Package not found in PyPI. Might be deleted.
            return False

        try:
            return Version(self.required_version) == Version(latest_version)
        except IrrationalVersionError:
            return poor_mans_version_compare(self.required_version, latest_version)


def poor_mans_version_compare(v1, v2):
    """Check for equality of two version strings that cannot be compared by
    verlib. Example: "0.3.2.RC1"""
    def to_list(v):
        parts = v.split('.')
        # Try to convert each part to int
        for i in range(len(parts)):
            try:
                parts[i] = int(parts[i])
            except Exception:
                pass
        return parts
    return to_list(v1) == to_list(v2)
