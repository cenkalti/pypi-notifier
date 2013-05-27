#!/usr/bin/env python
import os
import errno

from flask import g, current_app
from flask.ext.script import Manager

from deli import create_app
from deli import models
from deli.cache import cache
from deli.models import db, User, Repo, Requirement, Package

manager = Manager(create_app)

# Must be a class name from config.py
config = os.environ['DELI_CONFIG']
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
        os.unlink('/tmp/deli.db')
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
def iter_requirements():
    for requirement in Requirement.query.all():
        requirement.check_for_update()
    db.session.commit()


if __name__ == '__main__':
    manager.run()
