from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    github_id = db.Column(db.Integer, unique=True)
    github_token = db.Column(db.Integer)

    repos = db.relationship('Repo', backref='user')

    def __init__(self, github_token):
        self.github_token = github_token


class Repo(db.Model):
    __tablename__ = 'repos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    github_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(200))
    last_check = db.Column(db.DateTime)
    # last_hash = db.Column()
    # last_etag = db.Column()

    requirements = db.relationship('Package', secondary='requirements',
                                   backref='repos')

    def __init__(self, github_id, user_id):
        self.github_id = github_id
        self.user_id = user_id


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    latest_version = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)

    def __init__(self, name):
        self.name = name


requirements = db.Table(
    'requirements',
    db.Column('repo_id', db.Integer, db.ForeignKey(Repo.id)),
    db.Column('package_id', db.Integer, db.ForeignKey(Package.id)),
    db.Column('required_version', db.String(20)),
)
