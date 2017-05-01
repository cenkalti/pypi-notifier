from flask import Flask, g, session, request, url_for, redirect, flash, render_template
from flask_github import GitHubError

from .extensions import db, cache, github, sentry
from .config import load_config
from .views import register_views
from .cli import register_commands
from .models import User


def create_app(config):
    app = Flask(__name__)
    load_config(app.config, config)

    db.init_app(app)
    cache.init_app(app)
    github.init_app(app)
    if app.config.get('SENTRY_DSN'):
        sentry.init_app(app)

    register_views(app)
    register_commands(app)

    @app.before_request
    def set_user():
        g.user = None
        if session.get('user_id', None):
            g.user = User.query.get(session['user_id'])

    @app.after_request
    def remove_session(response):
        db.session.remove()
        return response

    @github.access_token_getter
    def get_github_token():
        user = g.user
        if user is not None:
            return user.github_token

    @app.route('/github-callback')
    @github.authorized_handler
    def oauth_authorized(token):
        if token is None:
            flash('You denied the request to sign in.')
            return redirect(url_for('index'))

        user_response = github.get('user', access_token=token)
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
        g.user = user

        emails = user.get_emails_from_github()
        user.email = [e['email'] for e in emails if e['primary']][0]
        db.session.commit()
        session['user_id'] = user.id

        if len(emails) > 1:
            return redirect(url_for('select_email'))
        else:
            return redirect(url_for('get_repos'))

    @app.route('/login')
    def login():
        if g.user and session.get('user_id'):
            return redirect(url_for('index'))

        if request.args.get('private') == 'True':
            scope = 'user:email,repo'
        else:
            scope = 'user:email'

        return github.authorize(scope=scope)

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))

    @app.errorhandler(GitHubError)
    def handle_github_error(error):
        if error.response.status_code == 401:
            session.pop('user_id', None)
            return render_template('github-401.html')
        else:
            return "Github returned: %s" % error

    return app
