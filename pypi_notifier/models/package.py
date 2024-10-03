import logging
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from sqlalchemy import or_
from sqlalchemy.ext.associationproxy import association_proxy

from pypi_notifier.extensions import cache, db
from pypi_notifier.models.util import commit_or_rollback

logger = logging.getLogger(__name__)


class Package(db.Model):
    __tablename__ = "packages"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    latest_version = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)

    repos = association_proxy("requirements", "repo")

    def __init__(self, name):
        self.name = name.lower()

    def __repr__(self):
        return "<Package %s>" % self.name

    @property
    def url(self):
        return "https://pypi.python.org/pypi/%s" % self.original_name

    @classmethod
    def update_all_packages(cls):
        packages = cls.query.filter(
            or_(
                cls.last_check <= datetime.utcnow() - timedelta(days=1),
                cls.last_check.is_(None),
            )
        ).all()
        logger.info("Number of packages to be processed: %s", len(packages))
        total = 0
        for package in packages:
            with commit_or_rollback():
                package.update_from_pypi()

        logger.info("Number of packages processed: %s", total)

    @classmethod
    @cache.cached(timeout=3600, key_prefix="all_packages")
    def get_all_names(cls):
        packages = pypi_get_project_names()
        return {name.lower(): name for name in packages if name}

    @property
    def original_name(self):
        try:
            return self.get_all_names()[self.name.lower()]
        except KeyError:
            return self.name

    def find_latest_version(self):
        latest_version = pypi_get_latest_version(self.original_name)
        if not latest_version:
            return
        logger.info("Latest version of %s is %s", self.original_name, latest_version)
        return latest_version

    def update_from_pypi(self):
        """
        Updates the latest version of the package by asking PyPI.

        """
        latest = self.find_latest_version()
        self.last_check = datetime.utcnow()
        if self.latest_version != latest:
            self.latest_version = latest
            self.updated_at = datetime.utcnow()


def pypi_get_project_names() -> List[str]:
    headers = {"Accept": "application/vnd.pypi.simple.v1+json"}
    response = requests.get("https://pypi.org/simple/", headers=headers)
    response.raise_for_status()
    return [project["name"] for project in response.json()["projects"]]


def pypi_get_latest_version(project: str) -> Optional[str]:
    headers = {"Accept": "application/vnd.pypi.simple.v1+json"}
    response = requests.get(f"https://pypi.org/simple/{project}/", headers=headers)
    response.raise_for_status()
    try:
        return response.json()["versions"][-1]
    except IndexError:
        return
