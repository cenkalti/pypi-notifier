import os
import time
import signal
import traceback

from pypi_notifier import models
from pypi_notifier.app import create_app

app = create_app(os.environ["PYPI_NOTIFIER_CONFIG"])


def update_repos():
    with app.app_context():
        models.Repo.update_all_repos()


def update_packages():
    with app.app_context():
        models.Package.update_all_packages()


def send_emails():
    with app.app_context():
        models.User.send_emails()


def handler(signum, stack):
    print("Alarm: ", time.ctime())
    traceback.print_stack()


signal.signal(signal.SIGALRM, handler)
signal.alarm(850)
