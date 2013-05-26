from flask import render_template, request, redirect, url_for, g

from models import db, Repo
from github import github


def register_views(app):

    @app.route('/user')
    def user():
        return str(github.get('user'))

    @app.route('/repos')
    def repos():
        repos = github.get('user/repos')
        selected_ids = [r.github_id for r in g.user.repos]
        for repo in repos:
            repo['checked'] = (repo['id'] in selected_ids)
        return render_template('repos.html', repos=repos)

    @app.route('/repos', methods=['POST'])
    def post_repos():
        # Add selected repos
        for name, github_id in request.form.iteritems():
            github_id = int(github_id)
            repo = Repo.query.filter(
                Repo.github_id == github_id,
                Repo.user_id == g.user.id).first()
            if repo is None:
                repo = Repo(github_id, g.user.id)
            repo.name = name
            db.session.add(repo)

        # Remove unselected repos
        ids = map(int, request.form.itervalues())
        for repo in g.user.repos:
            if repo.github_id not in ids:
                db.session.delete(repo)

        db.session.commit()
        return redirect(url_for('thanks'))

    @app.route('/thanks')
    def thanks():
        return render_template('thanks.html')

    @app.route('/repo/<path:name>', methods=['GET', 'POST'])
    def repo(name):
        if request.method == 'POST':
            return 'yes'
        return """Enter path of requirements.txt<br>
        <form method=post>
        <input type=text value=requirements.txt>
        <input type=submit>
        </form>"""
