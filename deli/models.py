from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    github_id = db.Column(db.Integer)
    github_token = db.Column(db.Integer)

    projects = db.relationship('Project', backref='user')

    def __init__(self, github_token):
        self.github_token = github_token


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer)
    name = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_check = db.Column(db.DateTime)
    # last_hash = db.Column()
    # last_etag = db.Column()

    requirements = db.relationship('Package', secondary='requirements',
                                   backref='projects')

    def __init__(self, name, user_id, github_id):
        self.name = name
        self.user_id = user_id
        self.github_id = github_id


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    latest_version = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)

    def __init__(self, name):
        self.name = name


requirements = db.Table(
    'requirements',
    db.Column('project_id', db.Integer, db.ForeignKey(Project.id)),
    db.Column('package_id', db.Integer, db.ForeignKey(Package.id)),
    db.Column('required_version', db.String(20)),
)
