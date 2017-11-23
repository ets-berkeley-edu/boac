import json
import os
import boac.factory
import pytest

from tests.fixtures.cohorts import fixture_team_members # noqa
from tests.fixtures.cohorts import fixture_custom_cohorts # noqa


os.environ['BOAC_ENV'] = 'test'


class FakeAuth(object):
    def __init__(self, the_app, the_client):
        self.app = the_app
        self.client = the_client

    def login(self, uid):
        self.app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {
            'uid': uid,
            'password': self.app.config['DEVELOPER_AUTH_PASSWORD'],
        }
        self.client.post('/devauth/login', data=json.dumps(params), content_type='application/json')


# Because app and db fixtures are only created once per pytest run, individual tests
# are not able to modify application configuration values before the app is created.
# Per-test customizations could be supported via a fixture scope of 'function' and
# the @pytest.mark.parametrize annotation.

@pytest.fixture(scope='session')
def app(request):
    """Fixture application object, shared by all tests."""
    _app = boac.factory.create_app()

    # Create app context before running tests.
    ctx = _app.app_context()
    ctx.push()

    # Pop the context after running tests.
    def teardown():
        ctx.pop()
    request.addfinalizer(teardown)

    return _app


# TODO Perform DB schema creation and deletion outside an app context, enabling test-specific app configurations.
@pytest.fixture(scope='session')
def db(app, request):
    """Fixture database object, shared by all tests."""

    from boac.models import development_db
    # Drop all tables before re-loading the schemas.
    # If we dropped at teardown instead, an interrupted test run would block the next test run.
    development_db.clear()
    _db = development_db.load()

    return _db


@pytest.fixture(scope='function')
def db_session(db, request):
    """
    Fixture database session used for the scope of a single test. All executions are wrapped
    in a transaction and then rolled back to keep individual tests isolated.
    """
    # Mixing SQL-using test fixtures with SQL-using decorators can trigger not-yet-diagnosed
    # freezes in Flask-SQLAlchemy due to DB session debris.
    db.session.rollback()
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)
    db.session = _session

    # Roll back transaction when the test is complete.
    def teardown():
        transaction.rollback()
        _session.remove()
    request.addfinalizer(teardown)

    return _session


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """
    Shortcut to start an authenticated session.
    """
    return FakeAuth(app, client)


def pytest_itemcollected(item):
    """Print docstrings during test runs for more readable output."""
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))
