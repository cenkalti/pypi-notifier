import json

from flask import current_app

from models import db


def update_user(user):
    r = current_app.github.get_resource('user')
    r = json.loads(r[1])
    user.name = r['login']
    user.github_id = r['id']
    db.session.add(user)
    db.session.commit()
