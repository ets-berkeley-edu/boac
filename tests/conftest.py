import os
import pytest
import subprocess

os.environ['BOAC_ENV'] = 'test'

import boac.db
import boac.factory


# Because app and db fixtures are only created once per pytest run, individual tests
# are not able to modify application configuration values before the app is created.
# Per-test customizations could be supported via a fixture scope of 'function' and
# the @pytest.mark.parametrize annotation.

@pytest.fixture(scope='session')
def app(request):
    '''Fixture application object, shared by all tests.'''
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
    '''Fixture database object, shared by all tests.'''
    _db = boac.db.initialize_db(app)

    # The psycopg2 engine doesn't handle big pg_dump files well, so shell out to load the schema. Abort the
    # transaction and test suite if the schema contains errors.
    load_schema_cmd = 'psql -v ON_ERROR_STOP=ON --single-transaction boac_test < scripts/db/schema.sql'
    subprocess.check_output(load_schema_cmd, shell=True)

    # Drop all tables after running tests.
    def teardown():
        r = _db.engine.execute("SELECT tablename FROM pg_tables where schemaname='public'")
        table_names = [row[0] for row in r]
        _db.engine.execute('DROP TABLE IF EXISTS {} CASCADE'.format(', '.join(table_names)))
    request.addfinalizer(teardown)

    return _db


@pytest.fixture(scope='function')
def db_session(db, request):
    '''
    Fixture database session used for the scope of a single test. All executions are wrapped
    in a transaction and then rolled back to keep individual tests isolated.
    '''
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)
    db.session = _session

    # Roll back transaction and close connection when the test is complete.
    def teardown():
        transaction.rollback()
        connection.close()
        _session.remove()
    request.addfinalizer(teardown)

    return _session


def pytest_itemcollected(item):
    '''Print docstrings during test runs for more readable output.'''
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))
