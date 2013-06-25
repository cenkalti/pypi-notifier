import unittest

from mock import patch
from flask.ext.github import GitHub

from pypi_notifier import create_app, db
from pypi_notifier.models import User, Repo, Requirement, Package
from pypi_notifier.config import TestingConfig


class PyPINotifierTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self._ctx.pop()

    def test_index(self):
        rv = self.client.get('/')
        assert 'Login' in rv.data

    def test_login(self):
        rv = self.client.get('/login')
        assert rv.status_code == 302
        assert 'github.com' in rv.headers['Location']

    @patch.object(GitHub, 'get')
    @patch.object(GitHub, 'handle_response')
    def test_github_callback(self, handle_response, get):
        handle_response.return_value = {'access_token': 'asdf'}
        get.return_value = {'id': 1, 'login': 'cenkalti', 'email': 'cenk@x.com'}

        self.client.get('/github-callback?code=xxxx')

        user = User.query.get(1)
        assert user
        assert user.github_token == 'asdf'

    def fixture(self):
        u1 = User('u1')
        u2 = User('u2')
        r1 = Repo('r1', u1)
        r2 = Repo('r2', u2)
        p1 = Package('p1')
        p2 = Package('p2')
        req1 = Requirement(r1, p1)
        req2 = Requirement(r2, p1)
        req3 = Requirement(r2, p2)
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(req1)
        db.session.add(req2)
        db.session.add(req3)
        db.session.commit()
        return locals()

    def test_remove_user(self):
        """Tests SQLAlchemy relationships.

        When a User deletes his account all of the records should be deleted
        except Packages.

        """
        f = self.fixture()

        db.session.delete(f['u2'])
        db.session.commit()

        assert User.query.all() == [f['u1']]
        assert Repo.query.all() == [f['r1']]
        assert Requirement.query.all() == [f['req1']]
        assert Package.query.all() == [f['p1'], f['p2']]


if __name__ == '__main__':
    unittest.main()
