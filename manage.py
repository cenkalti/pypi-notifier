#!/usr/bin/env python
from flask.ext.script import Manager
 
from deli import create_app

manager = Manager(create_app)

# Must be a class name from config.py
manager.add_option('-c', '--config', dest='config', required=False)


@manager.command
def init_db():
    from deli.models import db
    db.create_all()


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
        user.update_from_github()
        db.session.add(user)
    db.session.commit()


@manager.command
def iter_repos():
    from deli.models import db, Repo
    for repo in Repo.query.all():
        repo.update_from_github()
        db.session.add(repo)
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
