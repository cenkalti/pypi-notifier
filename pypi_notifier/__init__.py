from flask import Flask, g, session, request, url_for, redirect, flash, \
    render_template
from flask.ext.cache import Cache
from flask.ext.github import GitHub
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry


db = SQLAlchemy()
cache = Cache()
github = GitHub()


def create_app(config):
    from pypi_notifier.views import register_views
    from pypi_notifier.models import User

    app = Flask(__name__)
    load_config(app, config)

    db.init_app(app)
    cache.init_app(app)
    github.init_app(app)

    register_views(app)

    if app.config.get('SENTRY_DSN'):
        Sentry(app)

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
        next_url = request.args.get('next') or url_for('repos')

        if token is None:
            flash('You denied the request to sign in.')
            return redirect(next_url)

        user_response = github.get('user', params={'access_token': token})
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
        user.email = user_response.get('email') or github.get('user/emails')[0]
        db.session.commit()

        session['user_id'] = user.id
        return redirect(next_url)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        if session.get('user_id', None) is None or g.user is None:
            return github.authorize(scope='user:email')
        else:
            return redirect(url_for('index'))

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))

    return app


def load_config(app, object_or_str):
    from pypi_notifier import config
    if isinstance(object_or_str, basestring):
        object_or_str = getattr(config, object_or_str)
    app.config.from_object(object_or_str)
