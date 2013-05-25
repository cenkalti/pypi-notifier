# -*- coding: utf-8 -*-
from flask import (Flask, g, session, request, url_for, redirect, flash,
                   render_template)
from flask.ext.github import GithubAuth

import tasks
from models import db, User
from config import DevelopmentConfig
from frontend import frontend


class Deli(Flask):

    def __init__(self, import_name, config_object):
        super(Deli, self).__init__(import_name)
        self.config.from_object(config_object)
        self.github = GithubAuth(
            client_id=self.config['GITHUB_CLIENT_ID'],
            client_secret=self.config['GITHUB_CLIENT_SECRET'],
            session_key='user_id')

        @self.before_request
        def set_user():
            g.user = None
            if 'user_id' in session:
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
            next_url = request.args.get('next') or url_for('frontend.repos')

            if resp is None:
                flash(u'You denied the request to sign in.')
                return redirect(next_url)

            token = resp['access_token']
            user = User.query.filter_by(github_token=token).first()
            if user is None:
                user = User(token)
                db.session.add(user)
            user.github_token = token
            db.session.commit()

            session['user_id'] = user.id
            set_user()
            tasks.update_user(user)
            return redirect(next_url)

        @self.route('/')
        def index():
            return render_template('index.html')

        @self.route('/login')
        def login():
            if session.get('user_id', None) is None or g.user is None:
                return self.github.authorize(
                    callback_url=self.config['CALLBACK_URL'],
                    scope='user:email')
            else:
                return redirect(url_for('index'))

        @self.route('/logout')
        def logout():
            session.pop('user_id', None)
            return redirect(url_for('index'))


def create_app(config_object):
    app = Deli(__name__, config_object)
    db.init_app(app)
    app.register_blueprint(frontend)
    return app


if __name__ == '__main__':
    app = create_app(DevelopmentConfig)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
