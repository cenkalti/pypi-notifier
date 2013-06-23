from datetime import datetime
import xmlrpclib
from pypi_notifier import db, cache


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

    def update_from_pypi(self):
        latest = self.find_latest_version()
        self.last_check = datetime.utcnow()
        if self.latest_version != latest:
            self.latest_version = latest
            self.updated_at = datetime.utcnow()
