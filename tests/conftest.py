"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from datetime import datetime
import glob
import json
import os
os.environ['BOAC_ENV'] = 'test'  # noqa

from boac import std_commit
import boac.factory
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_template import NoteTemplate
from moto import mock_sts
import pytest
from tests.util import mock_advising_note_s3_bucket, override_config


class FakeAuth(object):
    def __init__(self, the_app, the_client):
        self.app = the_app
        self.client = the_client

    def login(self, uid):
        with override_config(self.app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {
                'uid': uid,
                'password': self.app.config['DEVELOPER_AUTH_PASSWORD'],
            }
            self.client.post(
                '/api/auth/dev_auth_login',
                data=json.dumps(params),
                content_type='application/json',
            )


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
    _db = development_db.load(cohort_test_data=True)

    return _db


@pytest.fixture(scope='function', autouse=True)
def db_session(db, request):
    """Fixture database session used for the scope of a single test.

    All executions are wrapped in a session and then rolled back to keep individual tests isolated.
    """
    # Mixing SQL-using test fixtures with SQL-using decorators seems to cause timing issues with pytest's
    # fixture finalizers. Instead of using a finalizer to roll back the session and close connections,
    # we begin by cleaning up any previous invocations.
    # This fixture is marked 'autouse' to ensure that cleanup happens at the start of every test, whether
    # or not it has an explicit database dependency.
    db.session.rollback()
    try:
        db.session.get_bind().close()
    # The session bind will close only if it was provided a specific connection via this fixture.
    except AttributeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)
    db.session = _session

    return _session


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """Shortcut to start an authenticated session."""
    return FakeAuth(app, client)


@pytest.fixture(scope='session', autouse=True)
def fake_loch(app):
    """Mimic data loch schemas and tables in a local Postgres database."""
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text
    fixture_path = f"{app.config['BASE_DIR']}/fixtures"
    with open(f'{fixture_path}/loch.sql', 'r') as ddlfile:
        ddltext = ddlfile.read()
    params = {}
    for fixture in glob.glob(f'{fixture_path}/loch_student_*.json'):
        key = fixture.replace(f'{fixture_path}/loch_student_', '').replace('.json', '')
        with open(fixture, 'r') as f:
            params[key] = f.read()
    data_loch_db = create_engine(app.config['DATA_LOCH_RDS_URI'])
    data_loch_db.execute(text(ddltext), params)


@pytest.fixture(scope='session', autouse=True)
def fake_sts(app):
    """Fake the AWS security token service that BOA relies on to deliver S3 content (photos, note attachments)."""
    mock_sts().start()
    yield
    mock_sts().stop()


@pytest.fixture()
def create_alerts(client, db_session):
    """Create assignment and midterm grade alerts."""
    # Create three canned alerts for the current term and one for the previous term.
    from boac.models.alert import Alert
    Alert.create(
        sid='11667051',
        alert_type='late_assignment',
        key='2172_100900300',
        message='Week 5 homework in LATIN 100 is late.',
    )
    Alert.create(
        sid='11667051',
        alert_type='late_assignment',
        key='2178_800900300',
        message='Week 5 homework in RUSSIAN 13 is late.',
    )
    Alert.create(
        sid='11667051',
        alert_type='missing_assignment',
        key='2178_500600700',
        message='Week 6 homework in PORTUGUESE 12 is missing.',
    )
    Alert.create(
        sid='2345678901',
        alert_type='late_assignment',
        key='2178_100200300',
        message='Week 5 homework in BOSCRSR 27B is late.',
    )
    # Load our usual student of interest into the cache and generate midterm alerts from fixture data.
    client.get('/api/student/by_uid/61889')
    Alert.update_all_for_term(2178)


@pytest.fixture()
def mock_advising_note(app, db):
    """Create advising note with attachment (mock s3)."""
    with mock_advising_note_s3_bucket(app):
        note_author_uid = '90412'
        base_dir = app.config['BASE_DIR']
        path_to_file = f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'
        with open(path_to_file, 'r') as file:
            note = Note.create(
                author_uid=note_author_uid,
                author_name='Joni Mitchell CC',
                author_role='Director',
                author_dept_codes=['UWASC'],
                sid='11667051',
                subject='In France they kiss on main street',
                body="""
                    My darling dime store thief, in the War of Independence
                    Rock 'n Roll rang sweet as victory, under neon signs
                """,
                attachments=[
                    {
                        'name': path_to_file.rsplit('/', 1)[-1],
                        'byte_stream': file.read(),
                    },
                ],
            )
            db.session.add(note)
            std_commit(allow_test_environment=True)
    yield note
    Note.delete(note_id=note.id)
    std_commit(allow_test_environment=True)


@pytest.fixture()
def mock_note_template(app, db):
    """Create advising note template with attachment (mock s3)."""
    with mock_advising_note_s3_bucket(app):
        base_dir = app.config['BASE_DIR']
        path_to_file = f'{base_dir}/fixtures/mock_note_template_attachment_1.txt'
        timestamp = datetime.now().timestamp()
        with open(path_to_file, 'r') as file:
            note_template = NoteTemplate.create(
                creator_id=AuthorizedUser.get_id_per_uid('242881'),
                title=f'Potholes in my lawn ({timestamp})',
                subject=f'It\'s unwise to leave my garden untended ({timestamp})',
                body=f"""
                    See, I've found that everyone's sayin'
                    What to do when suckers are preyin'
                """,
                topics=['Three Feet High', 'Rising'],
                attachments=[
                    {
                        'name': path_to_file.rsplit('/', 1)[-1],
                        'byte_stream': file.read(),
                    },
                ],
            )
            std_commit(allow_test_environment=True)
            return note_template


def pytest_itemcollected(item):
    """Print docstrings during test runs for more readable output."""
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))
