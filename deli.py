# -*- coding: utf-8 -*-
import json
from pprint import pformat
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort, render_template_string
from flaskext.github import GithubAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# setup flask
app = Flask(__name__)
app.config.update(
    DATABASE_URI='sqlite:////tmp/flask-github.db',
    SECRET_KEY='Seninle kim kalacak, isiklar kapaninca?',
    DEBUG=True
)

# setup flask-github
github = GithubAuth(
    client_id='a64036373119cc126aab',
    client_secret='d59137d90c3f3d062b2f32509f9e258a3af6a65a',
    session_key='user_id'
)

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
init_db()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(Integer)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/')
def index():
    if g.user:
        t = """<a href={{ url_for('logout') }}>Logout</a>"""
    else:
        t = """<a href={{ url_for('login') }}>Login with you GitHub account</a>"""
    return render_template_string(t)


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/github-callback')
@github.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    token = resp['access_token']
    user = User.query.filter_by(github_access_token=token).first()
    if user is None:
        user = User(token)
        db_session.add(user)
    user.github_access_token = token
    db_session.commit()

    session['user_id'] = user.id
    before_request()
    return github.get_resource('user')[1]
    return redirect(url_for('repos'))


@app.route('/user')
def user():
    return github.get_resource('user')[1]


@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(
            callback_url='http://deli.cenkalti.net/github-callback',
            scope='user:email')
    else:
        return redirect(url_for('repos'))


@app.route('/repos')
def repos():
    content = github.get_resource('user/repos')[1]
    repos = json.loads(content)
    repos = [r['full_name'] for r in repos]
    t = """Select repository
    <ul>
    {% for repo in repos %}
    <li><a href={{ url_for('repo', name=repo) }}>{{repo}}</a></li>
    {% endfor %}
    </ul>"""
    return render_template_string(t, repos=repos)


@app.route('/repo/<path:name>', methods=['GET', 'POST'])
def repo(name):
    if request.method == 'POST':
        return 'yes'
    return """Enter path of requirements.txt<br>
    <form method=post>
    <input type=text value=requirements.txt>
    <input type=submit>
    </form>"""


@app.route('/content')
def content():
    return github.get_resource('repos/cenkalti/kuyruk/contents/setup.py')[1]


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
