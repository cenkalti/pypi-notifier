#!/usr/bin/env python
import os
import errno

from flask import g, current_app
from flask.ext.script import Manager, Shell
from flask.ext.github import GitHubError
 
from deli import create_app, db
from deli import models

manager = Manager(create_app)

# Must be a class name from config.py
config = os.environ['DELI_CONFIG']
manager.add_option('-c', '--config', dest='config', required=False,
                   default=config)


def _make_context():
    return dict(app=current_app, db=db, models=models)
manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def init_db():
    from deli.models import db
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
    from deli.models import Package
    Package.get_all_names()


@manager.command
def clear_cache():
    from deli.cache import cache
    cache.clear()


@manager.command
def find_latest(name):
    from deli.models import Package
    print Package(name).find_latest_version()


@manager.command
def iter_users():
    from deli.models import db, User
    for user in User.query.all():
        g.user = user
        user.update_from_github()
        db.session.add(user)
    db.session.commit()


@manager.command
def iter_repos():
    from deli.models import db, Repo
    for repo in Repo.query.all():
        g.user = repo.user
        try:
            repo.update_requirements()
            db.session.add(repo)
        except GitHubError as e:
            print e
    db.session.commit()


@manager.command
def iter_packages():
    from deli.models import db, Package
    for package in Package.query.all():
        package.update_from_pypi()
        db.session.add(package)
    db.session.commit()


@manager.command
def iter_requirements():
    pass


if __name__ == '__main__':
    manager.run()
