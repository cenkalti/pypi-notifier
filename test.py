import unittest

from mock import patch
from flask.ext.github import GitHub

from pypi_notifier import create_app, db
from pypi_notifier.models import User
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


if __name__ == '__main__':
    unittest.main()
