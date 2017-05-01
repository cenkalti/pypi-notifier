from unittest import TestCase
from unittest.mock import patch

from flask_github import GitHub

from pypi_notifier.app import create_app
from pypi_notifier.extensions import db
from pypi_notifier.models import User, Repo, Requirement, Package


class PyPINotifierTestCase(TestCase):

    def setUp(self):
        self.app = create_app("testing")
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
        assert 'Login' in rv.data.decode()

    def test_login(self):
        rv = self.client.get('/login')
        assert rv.status_code == 302
        assert 'github.com' in rv.headers['Location']

    @patch.object(User, 'get_emails_from_github')
    @patch.object(GitHub, 'get')
    @patch.object(GitHub, '_handle_response')
    def test_github_callback(self, handle_response, get, get_emails_from_github):
        handle_response.return_value = 'asdf'
        get.return_value = {'id': 1, 'login': 'cenkalti', 'email': 'cenk@x.com'}
        get_emails_from_github.return_value = [{'email': 'cenk@x.com',
                                                'primary': True,
                                                'verified': True}]

        self.client.get('/github-callback?code=xxxx')

        user = User.query.get(1)
        assert user
        assert user.github_token == 'asdf'

    def fixture(self):
        u1 = User('u1')
        u1.email = 'test@test'
        u2 = User('u2')
        u2.email = 'test@test'
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

    @patch.object(Package, 'get_all_names')
    def test_update_requirements(self, get_all_names):
        get_all_names.return_value = {'a': 'a', 'b': 'b'}

        u = User('t')
        u.email = 'test@test'
        r = Repo(2, u)
        db.session.add(r)
        db.session.commit()

        with patch.object(Repo, 'fetch_requirements') as fetch_requirements:
            fetch_requirements.return_value = "a==1.0\nb==2.1"
            r.update_requirements()
            db.session.commit()

        reqs = Requirement.query.all()
        assert len(reqs) == 2, reqs
        assert (reqs[0].package.name, reqs[0].required_version) == ('a', '1.0')
        assert (reqs[1].package.name, reqs[1].required_version) == ('b', '2.1')

    def test_strip_index_url(self):
        s = "-i http://simple.crate.io/\ndjango\ncelery"
        from pypi_notifier.models.repo import strip_requirements
        s = strip_requirements(s)
        assert s == 'django\ncelery'
