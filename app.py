import os

from pypi_notifier import models
from pypi_notifier.app import create_app

app = create_app(os.environ['PYPI_NOTIFIER_CONFIG'])


def update_repos():
    with app.app_context():
        models.Repo.update_all_repos()


def update_packages():
    with app.app_context():
        models.Package.update_all_packages()


def send_emails():
    with app.app_context():
        models.User.send_emails()
