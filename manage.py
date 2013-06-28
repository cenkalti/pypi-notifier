#!/usr/bin/env python
import os
import errno
import logging

from flask import current_app
from flask.ext.script import Manager

from pypi_notifier import create_app, db, models, cache


logging.basicConfig(level=logging.DEBUG)

manager = Manager(create_app)

# Must be a class name from config.py
config = os.environ['PYPI_NOTIFIER_CONFIG']
manager.add_option('-c', '--config', dest='config', required=False,
                   default=config)


@manager.shell
def make_shell_context():
    return dict(app=current_app, db=db, models=models)


@manager.command
def init_db():
    db.create_all()


@manager.command
def drop_db():
    try:
        os.unlink('/tmp/pypi_notifier.db')
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


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
def update_users():
    models.User.update_all_users_from_github()


@manager.command
def update_repos():
    models.Repo.update_all_repos()


@manager.command
def update_packages():
    models.Package.update_all_packages()


@manager.command
def send_emails():
    models.User.send_emails()


if __name__ == '__main__':
    manager.run()
