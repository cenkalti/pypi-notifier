import logging
from datetime import datetime, timedelta
import pystmark
from flask import render_template, current_app
from sqlalchemy import or_
from pypi_notifier import db, github
from pypi_notifier.models.mixin import ModelMixin


logger = logging.getLogger(__name__)


class User(db.Model, ModelMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    github_id = db.Column(db.Integer, unique=True)
    github_token = db.Column(db.Integer, unique=True)
    email_sent_at = db.Column(db.DateTime)
    last_check = db.Column(db.DateTime)
    last_modified = db.Column(db.String(40))

    repos = db.relationship('Repo', backref='user',
                            cascade="all, delete-orphan")

    def __init__(self, github_token):
        self.github_token = github_token

    def __repr__(self):
        return "<User %s>" % self.name

    @classmethod
    def update_all_users_from_github(cls):
        for user in cls.query.all():
            user.update_from_github()
            db.session.commit()

    def update_from_github(self):
        """
        Updates the user's name and email by asking to GitHub.

        Name and email of the user may be changed so we should update
        these periodically.

        """
        headers = None
        if self.last_modified:
            headers = {'If-Modified-Since': self.last_modified}

        response = github.raw_request('GET', 'user', headers=headers)
        logger.debug("Response: %s", response)
        if response.status_code == 200:
            self.last_modified = response.headers['Last-Modified']
            response = response.json()
            self.name = response['login']
            self.email = response['email']
            self.last_check = datetime.utcnow()
        elif response.status_code == 304:
            self.last_check = datetime.utcnow()
        else:
            raise Exception("Unknown status code: %s", response.status_code)

    def get_outdated_requirements(self):
        outdateds = []
        for repo in self.repos:
            for req in repo.requirements:
                if not req.up_to_date:
                    logger.debug("%s is outdated", req)
                    outdateds.append(req)

        return outdateds

    @classmethod
    def send_emails(cls):
        users = cls.query.filter(
            or_(
                cls.email_sent_at <= datetime.utcnow() - timedelta(days=7),
                cls.email_sent_at == None
            )
        ).all()
        for user in users:
            logger.info(user)
            user.send_email()
            user.email_sent_at = datetime.utcnow()
            db.session.commit()

    def send_email(self):
        outdateds = self.get_outdated_requirements()
        html = render_template('email.html', reqs=outdateds)
        message = pystmark.Message(
            sender='no-reply@pypi-notifier.org',
            to=self.email,
            subject="There are updated packages in PyPI",
            html=html)
        pystmark.send(message, current_app.config['POSTMARK_APIKEY'])
