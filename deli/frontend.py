import json

from flask import Blueprint, render_template, request, current_app

frontend = Blueprint('frontend', __name__)


@frontend.route('/user')
def user():
    return str(current_app.github.get_resource('user'))


@frontend.route('/repos')
def repos():
    content = current_app.github.get_resource('user/repos')[1]
    repos = json.loads(content)
    repos = [r['full_name'] for r in repos]
    return render_template('repos.html', repos=repos)


@frontend.route('/repo/<path:name>', methods=['GET', 'POST'])
def repo(name):
    if request.method == 'POST':
        return 'yes'
    return """Enter path of requirements.txt<br>
    <form method=post>
    <input type=text value=requirements.txt>
    <input type=submit>
    </form>"""


@frontend.route('/content')
def content():
    return current_app.github.get_resource(
        'repos/cenkalti/kuyruk/contents/setup.py')[1]
