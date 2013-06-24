import unittest

import pypi_notifier
from pypi_notifier.config import TestingConfig


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = pypi_notifier.create_app(TestingConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            pypi_notifier.db.create_all()

    def test_index(self):
        rv = self.client.get('/')
        assert 'Login' in rv.data

    def test_login(self):
        rv = self.client.get('/login')
        assert rv.status_code == 302
        assert 'github.com' in rv.headers['Location']


if __name__ == '__main__':
    unittest.main()
