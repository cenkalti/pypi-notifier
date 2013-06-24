from pypi_notifier import db, github
from pypi_notifier.models.mixin import ModelMixin


class User(db.Model, ModelMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    github_id = db.Column(db.Integer, unique=True)
    github_token = db.Column(db.Integer)

    repos = db.relationship('Repo', backref='user')

    def __init__(self, github_token):
        self.github_token = github_token

    def __repr__(self):
        return "<User %s>" % self.name

    def update_from_github(self):
        user = github.get('user')
        self.name = user['login']
        self.email = user['email']
