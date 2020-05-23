from flask import render_template, request, redirect, url_for, g, abort

from pypi_notifier.extensions import db
from pypi_notifier.models import Repo


def register_views(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/robots.txt')
    def robots_txt():
        return 'User-agent: *\nAllow: /'

    @app.route('/select-email', methods=['GET', 'POST'])
    def select_email():
        emails = g.user.get_emails_from_github()
        if request.method == 'POST':
            selected = request.form['email']
            if selected not in [e['email'] for e in emails]:
                abort(400)

            g.user.email = selected
            db.session.commit()
            return redirect(url_for('get_repos'))
        return render_template("select-email.html", emails=emails)

    @app.route('/repos')
    def get_repos():
        user_repos = {r.github_id: r for r in g.user.repos}
        repos = g.user.get_repos_from_github()
        for repo in repos:
            user_repo = user_repos.get(repo['id'])
            if user_repo:
                repo['checked'] = True
                repo['requirements_path'] = user_repo.requirements_path
        return render_template('repos.html', repos=repos)

    @app.route('/repos', methods=['POST'])
    def post_repos():
        # Add selected repos
        repos = {}
        for name, value in request.form.items():
            prefix, name = name.split(':', 1)
            if prefix == 'repo':
                github_id = int(name)
                repo = Repo.query.filter(
                    Repo.github_id == github_id,
                    Repo.user_id == g.user.id).first()
                if repo is None:
                    repo = Repo(github_id, g.user)
                repo.name = value
                db.session.add(repo)
                repos[github_id] = repo

        # Set requirements.txt paths
        for name, value in request.form.items():
            prefix, name = name.split(':', 1)
            if prefix == 'path':
                github_id = int(name)
                repo = repos.get(github_id)
                if repo:
                    repo.requirements_path = value

        # Remove unselected repos
        ids = set(map(int, repos.keys()))
        for repo in g.user.repos:
            if repo.github_id not in ids:
                db.session.delete(repo)

        db.session.commit()
        return redirect(url_for('done'))

    @app.route('/done')
    def done():
        reqs = g.user.get_outdated_requirements()
        return render_template('done.html', reqs=reqs)

    @app.route('/unsubscribe', methods=['GET', 'POST'])
    def unsubscribe():
        if request.method == 'POST':
            if request.form['confirm'] == 'yes':
                if g.user:
                    db.session.delete(g.user)
                    db.session.commit()
                return render_template('unsubscribed.html')
            else:
                return redirect(url_for('index'))
        return render_template('unsubscribe-confirm.html')
