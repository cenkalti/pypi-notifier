from pypi_notifier import models
from pypi_notifier.extensions import db, cache


def register_commands(app):

    @app.cli.command()
    def init_db():
        db.create_all()

    @app.cli.command()
    def fetch_package_list():
        models.Package.get_all_names()

    @app.cli.command()
    def clear_cache():
        cache.clear()

    @app.cli.command()
    def find_latest(name):
        print(models.Package(name).find_latest_version())

    @app.cli.command()
    def update_repos():
        models.Repo.update_all_repos()

    @app.cli.command()
    def update_packages():
        models.Package.update_all_packages()

    @app.cli.command()
    def send_emails():
        models.User.send_emails()

    @app.cli.command()
    def hourly():
        models.Repo.update_all_repos()
        models.Package.update_all_packages()
        models.User.send_emails()
