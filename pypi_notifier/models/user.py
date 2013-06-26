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

    repos = db.relationship('Repo', backref='user',
                            cascade="all, delete-orphan")

    def __init__(self, github_token):
        self.github_token = github_token

    def __repr__(self):
        return "<User %s>" % self.name

    def update_from_github(self):
        """
        Updates the user's name and email by asking to GitHub.

        Name and email of the user may be changed so we should update
        these periodically.

        """
        user = github.get('user')
        self.name = user['login']
        self.email = user['email']

    def get_outdated_requirements(self):
        outdateds = []
        for repo in self.repos:
            for req in repo.requirements:
                if not req.up_to_date:
                    logger.debug("%s is outdated", req)
                    outdateds.append(req)

        return outdateds

    def send_email(self):
        outdateds = self.get_outdated_requirements()
        html = render_template('email.html', reqs=outdateds)
        message = pystmark.Message(
            sender='no-reply@pypi-notifier.org',
            to=self.email,
            subject="There are updated packages in PyPI",
            html=html)
        pystmark.send(message, current_app.config['POSTMARK_APIKEY'])

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
