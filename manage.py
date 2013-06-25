#!/usr/bin/env python
import os
import errno
import logging

from flask import g, current_app
from flask.ext.script import Manager

from pypi_notifier import create_app, db, models, cache
from pypi_notifier.models import User, Repo, Requirement, Package


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
    Package.get_all_names()


@manager.command
def clear_cache():
    cache.clear()


@manager.command
def find_latest(name):
    print Package(name).find_latest_version()


@manager.command
def iter_users():
    for user in User.query.all():
        g.user = user
        user.update_from_github()
    db.session.commit()


@manager.command
def iter_repos():
    for repo in Repo.query.all():
        g.user = repo.user
        repo.update_requirements()
    db.session.commit()


@manager.command
def iter_packages():
    for package in Package.query.all():
        package.update_from_pypi()
    db.session.commit()


@manager.command
def send_emails():
    models.User.send_emails()


if __name__ == '__main__':
    manager.run()
