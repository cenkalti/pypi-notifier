import operator

from flask import render_template, request, redirect, url_for, g

from pypi_notifier import db, github
from pypi_notifier.models import Repo

list_params = {'per_page': '100'}


def register_views(app):

    @app.route('/user')
    def get_user():
        return str(github.get('user'))

    @app.route('/repos')
    def get_repos():
        repos = github.get('user/repos', params=list_params)
        repos = with_organization_repos(repos)
        selected_ids = [r.github_id for r in g.user.repos]
        for repo in repos:
            repo['checked'] = (repo['id'] in selected_ids)
        # list only python projects
        repos = [r for r in repos if str(r.get('language')).lower() == 'python']
        return render_template('repos.html', repos=repos)

    def with_organization_repos(repos):
        all_repos = {r['id']: r for r in repos}  # index by id
        orgs = github.get('user/orgs')
        orgs_names = [o['login'] for o in orgs]
        for org_name in orgs_names:
            org_repos = github.get('orgs/%s/repos' % org_name,
                                   params=list_params)
            for repo in org_repos:
                all_repos[repo['id']] = repo  # add each repo for each org.

        all_repos = all_repos.values()
        all_repos.sort(key=operator.itemgetter('full_name'))
        return all_repos

    @app.route('/repos', methods=['POST'])
    def post_repos():
        # Add selected repos
        for name, github_id in request.form.iteritems():
            github_id = int(github_id)
            repo = Repo.query.filter(
                Repo.github_id == github_id,
                Repo.user_id == g.user.id).first()
            if repo is None:
                repo = Repo(github_id, g.user)
            repo.name = name
            db.session.add(repo)

        # Remove unselected repos
        ids = map(int, request.form.itervalues())
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
