# -*- coding: utf-8 -*-
from flask import (Flask, g, session, request, url_for, redirect, flash,
                   render_template)
from flask.ext.github import GithubAuth

import deli.config
from cache import cache
from views import register_views
from models import db, User


class Deli(Flask):

    def __init__(self, import_name, config):
        super(Deli, self).__init__(import_name)
        self.load_config(config)
        self.github = GithubAuth(
            client_id=self.config['GITHUB_CLIENT_ID'],
            client_secret=self.config['GITHUB_CLIENT_SECRET'],
            session_key='user_id')

        @self.before_request
        def set_user():
            g.user = None
            if session.get('user_id', None):
                g.user = User.query.get(session['user_id'])

        @self.after_request
        def remove_session(response):
            db.session.remove()
            return response

        @self.github.access_token_getter
        def get_github_token():
            user = g.user
            if user is not None:
                return user.github_token

        @self.route('/github-callback')
        @self.github.authorized_handler
        def oauth_authorized(resp):
            next_url = request.args.get('next') or url_for('repos')

            if resp is None:
                flash(u'You denied the request to sign in.')
                return redirect(next_url)

            token = resp['access_token']
            user_response = self.github.get_resource(
                'user', access_token=token)[1]
            github_id = user_response['id']
            user = User.query.filter_by(github_token=token).first()
            if user is None:
                user = User.query.filter_by(github_id=github_id).first()
            if user is None:
                user = User(token)
                db.session.add(user)

            user.github_token = token
            user.github_id = github_id
            user.name = user_response['login']
            user.email = user_response['email']
            db.session.commit()
            session['user_id'] = user.id
            return redirect(next_url)

        @self.route('/')
        def index():
            return render_template('index.html')

        @self.route('/login')
        def login():
            if session.get('user_id', None) is None or g.user is None:
                return self.github.authorize(
                    callback_url=self.config['CALLBACK_URL'],
                    scope='user:email, public_repo')
            else:
                return redirect(url_for('index'))

        @self.route('/logout')
        def logout():
            session.pop('user_id', None)
            return redirect(url_for('index'))

    def load_config(self, config):
        if isinstance(config, basestring):
            config = getattr(deli.config, config)
        self.config.from_object(config)


def create_app(config):
    app = Deli(__name__, config)
    db.init_app(app)
    cache.init_app(app)
    register_views(app)
    return app
