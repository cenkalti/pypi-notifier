from pypi_notifier import db
from pypi_notifier.models.repo import Repo
from pypi_notifier.models.package import Package


class Requirement(db.Model):
    __tablename__ = 'requirements'

    repo_id = db.Column(db.Integer, db.ForeignKey(Repo.id),
                        primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey(Package.id),
                           primary_key=True)
    version = db.Column(db.String(20))

    package = db.relationship(
        Package,
        backref=db.backref('repos', cascade='all, delete-orphan'))
    repo = db.relationship(
        Repo,
        backref=db.backref('requirements', cascade="all, delete-orphan"))

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
