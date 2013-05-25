from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    github_token = db.Column(db.Integer)

    def __init__(self, github_token):
        self.github_token = github_token


class Project(db.Model):

    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)


class Packages(db.Model):

    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)


# class Requirements(db.Model):
#
#     __tablename__ = 'requirements'
