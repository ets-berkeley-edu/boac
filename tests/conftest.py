"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
import random
import string
import time

from boac import std_commit
import boac.factory
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_template import NoteTemplate
from flask_login import logout_user
from moto import mock_sts
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tests.util import mock_advising_note_s3_bucket, override_config

os.environ['BOAC_ENV'] = 'test'  # noqa
os.environ['EC2_INSTANCE_ID'] = 'test: EC2_INSTANCE_ID'  # noqa

DATA_LOCH_TEST_DATA_BY_DEPT = {
    'COENG': {
        'advisor_attributes': {
            'dept_code': 'EDDNO',
        },
        'advisor_role': {
            'academic_program_code': 'UCOE',
            'academic_program_description': 'Undergraduate Engineering',
            'advisor_type_code': 'DNDS',
            'cs_permissions': 'UC_CS_AA_CURRICULAR_ADVISOR',
        },
    },
    'GUEST': {
        'advisor_attributes': {
            'dept_code': None,
        },
        'advisor_role': {
            'academic_program_code': 'UBUS',
            'academic_program_description': 'Undergrad Business',
            'advisor_type_code': None,
            'cs_permissions': 'UC_CS_AA_CO_CURRICULAR_ADVISOR',
        },
    },
    'QCADV': {
        'advisor_attributes': {
            'dept_code': 'HENGL',
        },
        'advisor_role': {
            'academic_program_code': 'COLL',
            'academic_program_description': 'Undergrad Letters & Science',
            'advisor_type_code': 'ADVD',
            'cs_permissions': 'UC_CS_AA_CURRICULAR_ADVISOR',
        },
    },
    'QCADVMAJ': {
        'advisor_attributes': {
            'dept_code': 'HFREN',
        },
        'advisor_role': {
            'academic_program_code': 'UCLS',
            'academic_program_description': 'Letters & Science Major Advisors',
            'advisor_type_code': 'MAJ',
            'cs_permissions': 'UC_CS_AA_CURRICULAR_ADVISOR',
        },
    },
    'ZZZZZ': {
        'advisor_attributes': {
            'dept_code': 'EDESS',
        },
        'advisor_role': {
            'academic_program_code': None,
            'academic_program_description': 'Graduate Affairs Advisor',
            'advisor_type_code': None,
            'cs_permissions': 'UC_CS_AA_CURRICULAR_ADVISOR',
        },

    },
}


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
def db(app):
    """Fixture database object, shared by all tests."""
    from boac.models import development_db
    # Drop all tables before re-loading the schemas.
    # If we dropped at teardown instead, an interrupted test run would block the next test run.
    development_db.clear()
    return development_db.load(load_test_data=True)


@pytest.fixture(autouse=True, scope='function')
def logout():
    logout_user()


@pytest.fixture(scope='function', autouse=True)
def db_session(db):
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
        bind = db.session.get_bind()
        if isinstance(bind, Engine):
            bind.dispose()
        else:
            bind.close()
    # The session bind will close only if it was provided a specific connection via this fixture.
    except TypeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    _session = scoped_session(sessionmaker(bind=connection))
    db.session = _session

    return _session


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """Shortcut to start an authenticated session."""
    yield FakeAuth(app, client)
    logout_user()


@pytest.fixture(scope='session', autouse=True)
def fake_loch(app):
    """Mimic data loch schemas and tables in a local Postgres database."""
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text
    fixture_path = f"{app.config['BASE_DIR']}/fixtures"
    with open(f'{fixture_path}/loch/loch.sql', 'r') as ddlfile:
        ddltext = ddlfile.read()
    params = {}
    for fixture in glob.glob(f'{fixture_path}/loch/student_*.json'):
        key = fixture.replace(f'{fixture_path}/loch/student_', '').replace('.json', '')
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
    note = _create_mock_note(
        app=app,
        attachment='fixtures/mock_advising_note_attachment_1.txt',
        author_dept_codes=['UWASC'],
        author_uid='90412',
        db=db,
    )
    yield note
    Note.delete(note_id=note.id)
    std_commit(allow_test_environment=True)


@pytest.fixture()
def mock_note_draft(app, db):
    """Create advising note draft with attachment (mock s3)."""
    note = _create_mock_note(
        app=app,
        attachment='fixtures/mock_advising_note_attachment_1.txt',
        author_dept_codes=['UWASC'],
        author_uid='90412',
        db=db,
        is_draft=True,
    )
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
                body="""
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


@pytest.fixture(scope='session')
def admin_user_uid(app, db):
    from boac.models.cohort_filter import CohortFilter
    from boac.models.curated_group import CuratedGroup

    admin_user = _create_user(
        app=app,
        automate_degree_progress_permission=False,
        can_access_canvas_data=True,
        db=db,
        degree_progress_permission=None,
        has_calnet_record=True,
        is_admin=True,
    )
    CuratedGroup.create(admin_user.id, 'My Students')
    for name, group_codes in {
        'All sports': ['MFB-DL', 'WFH'],
        'Football, Defense': ['MFB-DB', 'MFB-DL'],
        'Field Hockey': ['WFH'],
    }.items():
        CohortFilter.create(uid=admin_user.uid, name=name, filter_criteria={'groupCodes': group_codes})
    std_commit(allow_test_environment=True)
    return admin_user.uid


@pytest.fixture()
def user_factory(app, db):
    def _user_factory(
            automate_degree_progress_permission=None,
            can_access_canvas_data=True,
            dept_codes=['COENG'],
            degree_progress_permission=None,
            has_calnet_record=True,
            is_admin=False,
    ):
        return _create_user(
            app=app,
            automate_degree_progress_permission=automate_degree_progress_permission,
            can_access_canvas_data=can_access_canvas_data,
            db=db,
            degree_progress_permission=degree_progress_permission,
            dept_codes=dept_codes,
            has_calnet_record=has_calnet_record,
            is_admin=is_admin,
        )
    return _user_factory


def pytest_itemcollected(item):
    """Print docstrings during test runs for more readable output."""
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))


def _create_mock_note(
        app,
        attachment,
        author_dept_codes,
        author_uid,
        db,
        is_draft=False,
):
    with mock_advising_note_s3_bucket(app):
        base_dir = app.config['BASE_DIR']
        attachment = f'{base_dir}/{attachment}'
        with open(attachment, 'r') as file:
            note = Note.create(
                attachments=[
                    {
                        'name': attachment.rsplit('/', 1)[-1],
                        'byte_stream': file.read(),
                    },
                ],
                author_uid=author_uid,
                author_name='Joni Mitchell CC',
                author_role='Director',
                author_dept_codes=author_dept_codes,
                body="""
                    My darling dime store thief, in the War of Independence
                    Rock 'n Roll rang sweet as victory, under neon signs
                """,
                is_draft=is_draft,
                sid='11667051',
                subject='In France they kiss on main street',
            )
            db.session.add(note)
            std_commit(allow_test_environment=True)
            return note


def _create_user(
        app,
        automate_degree_progress_permission,
        can_access_canvas_data,
        db,
        degree_progress_permission,
        has_calnet_record,
        is_admin,
        dept_codes=[],
):
    from boac.models.json_cache import insert_row as insert_in_json_cache
    from boac.models.university_dept import UniversityDept
    from boac.models.university_dept_member import UniversityDeptMember
    from sqlalchemy import create_engine
    from sqlalchemy.sql import text

    uid = str(round(time.time() * 1000))
    csid = datetime.now().strftime('%H%M%S%f')
    data_loch_test_data = [DATA_LOCH_TEST_DATA_BY_DEPT[dept_code] for dept_code in dept_codes]
    first_name = ''.join(random.choices(string.ascii_uppercase, k=6))
    last_name = ''.join(random.choices(string.ascii_uppercase, k=6))

    if data_loch_test_data:
        sql = ''
        for data_loch_row in data_loch_test_data:
            def _to_sql_value(value):
                return 'NULL' if value is None else f"'{value}'"

            advisor_attributes = data_loch_row['advisor_attributes']
            advisor_role = data_loch_row['advisor_role']
            sql += f"""
                INSERT INTO boac_advisor.advisor_attributes
                (sid, uid, first_name, last_name, title, dept_code, email, campus_email)
                VALUES
                (
                    '{csid}', '{uid}', '{first_name}', '{last_name}', 'Academic Advisor',
                    {_to_sql_value(advisor_attributes['dept_code'])}, NULL, '{uid}@berkeley.edu'
                );
                INSERT INTO boac_advisor.advisor_roles
                (sid, uid, advisor_type_code, advisor_type, instructor_type_code, instructor_type, academic_program_code, academic_program, cs_permissions)
                VALUES
                (
                    '{csid}', '{uid}', {_to_sql_value(advisor_role['advisor_type_code'])}, 'College Advisor', 'ADV', 'Advisor Only',
                    {_to_sql_value(advisor_role['academic_program_code'])},
                    {_to_sql_value(advisor_role['academic_program_description'])},
                    {_to_sql_value(advisor_role['cs_permissions'])}
                );
            """  # noqa: E501
        create_engine(app.config['DATA_LOCH_RDS_URI']).execute(text(sql))

    if has_calnet_record:
        insert_in_json_cache(
            f'calnet_user_for_uid_{uid}',
            {
                'uid': uid,
                'csid': csid,
                'firstName': first_name,
                'lastName': last_name,
                'name': f'{first_name} {last_name}',
            },
        )
    is_coe = 'COENG' in dept_codes
    authorized_user = AuthorizedUser(
        automate_degree_progress_permission=is_coe if automate_degree_progress_permission is None else automate_degree_progress_permission,  # noqa: E501
        can_access_canvas_data=can_access_canvas_data,
        created_by='0',
        degree_progress_permission=degree_progress_permission,
        is_admin=is_admin,
        uid=uid,
    )
    db.session.add(authorized_user)
    for dept_code in dept_codes:
        university_dept = UniversityDept.find_by_dept_code(dept_code)
        UniversityDeptMember.create_or_update_membership(
            university_dept_id=university_dept.id,
            authorized_user_id=authorized_user.id,
            role='advisor',
            automate_membership=True,
        )

    std_commit(allow_test_environment=True)
    return authorized_user
