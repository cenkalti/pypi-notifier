#!/usr/bin/env python
import logging
from functools import wraps

import flask.ext.script
from flask import current_app

from pypi_notifier import create_app, db, models, cache, sentry


logging.basicConfig(level=logging.DEBUG)


class Manager(flask.ext.script.Manager):
    """Subclassed to send exception information to Senry on command errors."""
    def command(self, func):
        func = catch_exception(func)
        return super(Manager, self).command(func)


def catch_exception(f):
    """Sends exception information to Sentry and reraises it."""
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            if getattr(sentry, 'app', None):
                sentry.captureException()
            raise
    return inner


manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=True)


@manager.shell
def make_shell_context():
    return dict(app=current_app, db=db, models=models)


@manager.command
def init_db():
    db.create_all()


@manager.command
def fetch_package_list():
    models.Package.get_all_names()


@manager.command
def clear_cache():
    cache.clear()


@manager.command
def find_latest(name):
    print models.Package(name).find_latest_version()


@manager.command
def update_repos():
    models.Repo.update_all_repos()


@manager.command
def update_packages():
    models.Package.update_all_packages()


@manager.command
def send_emails():
    models.User.send_emails()


@manager.command
def hourly():
    update_repos()
    update_packages()
    send_emails()


if __name__ == '__main__':
    manager.run()
