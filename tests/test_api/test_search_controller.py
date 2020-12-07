"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import std_commit
from boac.externals import data_loch
from boac.lib import util
from boac.models.appointment import Appointment
from boac.models.authorized_user import AuthorizedUser
from boac.models.manually_added_advisee import ManuallyAddedAdvisee
from flask import current_app as app
import pytest
import simplejson as json
from tests.util import override_config

asc_advisor_uid = '1081940'


@pytest.fixture()
def admin_login(fake_auth):
    fake_auth.login('2040')


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login('1133399')


@pytest.fixture()
def coe_advisor_no_advising_data(fake_auth):
    fake_auth.login('1022796')


@pytest.fixture()
def coe_scheduler(fake_auth):
    fake_auth.login('6972201')


@pytest.fixture()
def ce3_advisor(fake_auth):
    fake_auth.login('2525')


@pytest.fixture()
def no_canvas_access_advisor(fake_auth):
    fake_auth.login('1')


@pytest.fixture(scope='session')
def asc_inactive_students():
    return data_loch.safe_execute_rds("""
        SELECT DISTINCT(sas.sid) FROM boac_advising_asc.students s
        JOIN student.student_academic_status sas ON sas.sid = s.sid
        WHERE s.active is FALSE
    """)


class TestStudentSearch:
    """Student search API."""

    def test_search_not_authenticated(self, client):
        """Search is not available to the world."""
        _api_search(client, 'Hack it!', expected_status_code=401)

    def test_scheduler_cannot_search(self, client, coe_scheduler):
        """Search is not available to scheduler."""
        _api_search(client, 'Hack it!', expected_status_code=401)

    def test_search_with_missing_input(self, client, fake_auth):
        """Student search is nothing without input."""
        fake_auth.login('2040')
        _api_search(client, ' \t  ', students=True, expected_status_code=400)

    def test_search_by_complete_email_address(self, client, fake_auth):
        fake_auth.login('2040')
        api_json = _api_search(client, 'debaser@berkeley.edu', students=True)
        students = api_json['students']
        assert len(students) == api_json['totalStudentCount'] == 1
        assert students[0]['lastName'] == 'Doolittle'

    def test_search_by_name_or_email_prefix(self, client, fake_auth):
        fake_auth.login('2040')
        api_json = _api_search(client, 'barn', students=True)
        students = api_json['students']
        assert len(students) == api_json['totalStudentCount'] == 2
        assert ['Barney', 'Davies'] == [s['lastName'] for s in students]

    def test_search_by_sid_snippet(self, client, fake_auth, asc_inactive_students):
        """Search by snippet of SID."""
        def _search_students_as_user(uid_, sid_snippet_):
            fake_auth.login(uid_)
            api_json = _api_search(client, sid_snippet_, students=True)
            return api_json['students'], api_json['totalStudentCount']

        sid_snippet = '89012'
        # Admin user and ASC advisor get same results
        for uid in ['2040', '1081940']:
            students, total_student_count = _search_students_as_user(uid, sid_snippet)
            assert len(students) == total_student_count == 2
            assert _get_common_sids(asc_inactive_students, students)

    def test_search_by_inactive_sid(self, client, fake_auth):
        """Falls back to inactive students when searching by SID."""
        fake_auth.login('2040')
        api_json = _api_search(client, '2718281828', students=True)
        assert api_json['totalStudentCount'] == 1
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['sid'] == '2718281828'
        assert students[0]['academicCareerStatus'] == 'Completed'
        assert students[0]['fullProfilePending'] is True
        assert students[0]['firstName'] == 'Ernest'
        assert students[0]['lastName'] == 'Pontifex'

    def test_search_by_inactive_sid_snippet(self, client, fake_auth):
        """Does not match on inactive SID snippets."""
        fake_auth.login('2040')
        api_json = _api_search(client, '271828', students=True)
        assert api_json['totalStudentCount'] == 0
        students = api_json['students']
        assert len(students) == 0

    def test_search_by_inactive_name(self, client, fake_auth):
        """Does not match on inactive student names."""
        fake_auth.login('2040')
        api_json = _api_search(client, 'Pontifex', students=True)
        assert api_json['totalStudentCount'] == 0
        students = api_json['students']
        assert len(students) == 0

    def test_inactive_sids_search_creates_manually_added_advisee(self, client, fake_auth):
        ManuallyAddedAdvisee.query.delete()
        assert len(ManuallyAddedAdvisee.query.all()) == 0
        fake_auth.login('2040')
        _api_search(client, '2718281828', students=True)
        manually_added_advisees = ManuallyAddedAdvisee.query.all()
        assert len(manually_added_advisees) == 1
        assert manually_added_advisees[0].sid == '2718281828'

    def test_alerts_in_search_results(self, client, create_alerts, fake_auth):
        """Search results include alert counts."""
        fake_auth.login('2040')
        api_json = _api_search(client, 'davies', students=True)
        assert api_json['students'][0]['alertCount'] == 4

    def test_summary_profiles_in_search_results(self, client, fake_auth):
        fake_auth.login('2040')
        api_json = _api_search(client, 'davies', students=True)
        students = api_json['students']
        assert students[0]['academicStanding'][0]['status'] == 'GST'
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert students[0]['level'] == 'Junior'
        assert students[0]['termGpa'][0]['gpa'] == 2.9

    def test_search_by_name_snippet(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        api_json = _api_search(client, 'dav', students=True)
        students = api_json['students']
        assert len(students) == api_json['totalStudentCount'] == 3
        assert ['Crossman', 'Davies', 'Doolittle'] == [s['lastName'] for s in students]

    def test_search_by_full_name_snippet(self, client, fake_auth):
        """Search by snippet of full name."""
        fake_auth.login('2040')
        permutations = ['david c', 'john  david cro', 'john    cross', ' crossman, j ']
        for phrase in permutations:
            api_json = _api_search(client, phrase, students=True)
            students = api_json['students']
            assert len(students) == api_json['totalStudentCount'] == 1
            assert students[0]['lastName'] == 'Crossman'

    def test_search_by_name_coe(self, coe_advisor, client):
        """A COE name search finds all Pauls, including COE-specific data for COE Pauls."""
        api_json = _api_search(client, 'Paul', students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and s['coeProfile']['isActiveCoe'] is True)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and s['coeProfile']['isActiveCoe'] is False)
        assert next(s for s in students if s['name'] == 'Paul Kerschen' and 'coeProfile' not in s)
        for s in students:
            assert 'inIntensiveCohort' not in s.get('athleticsProfile', {})

    def test_search_by_name_asc(self, asc_advisor, client):
        """An ASC advisor finds all Pauls, including ASC-specific data for ASC Pauls."""
        api_json = _api_search(client, 'Paul', students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Kerschen' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and 'athleticsProfile' not in s)
        for s in students:
            assert 'coeProfile' not in s

    def test_search_by_name_admin(self, admin_login, client):
        """An admin name search finds all Pauls, including both ASC and COE data."""
        api_json = _api_search(client, 'Paul', students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Kerschen' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and 'athleticsProfile' in s and 'coeProfile' in s)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and s['coeProfile']['isActiveCoe'] is False)

    def test_search_by_name_with_special_characters(self, admin_login, client):
        """Search by name where name has special characters: hyphen, etc."""
        api_json = _api_search(client, 'Pauli-O\'Rourke', students=True)
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['name'] == 'Wolfgang Pauli-O\'Rourke'

    def test_search_by_name_no_canvas_data_access(self, no_canvas_access_advisor, client):
        """A user with no access to Canvas data can still search for students."""
        api_json = _api_search(client, 'Paul', students=True)
        assert len(api_json['students']) == 3

    def test_search_order_by_offset_limit(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        api_json = _api_search(client, 'dav', students=True, order_by='major', offset=1, limit=1)
        assert api_json['totalStudentCount'] == 3
        assert len(api_json['students']) == 1
        assert 'Crossman' == api_json['students'][0]['lastName']


class TestCourseSearch:
    """Course search API."""

    @classmethod
    def _assert_finds_math_16a(cls, client, query):
        api_json = _api_search(client, query, courses=True, students=True)
        courses = api_json['courses']
        assert len(courses) == 2
        assert api_json['totalCourseCount'] == 2
        for course in courses:
            assert course['courseName'] == 'MATH 16A'

    def test_search_by_name_excludes_courses_unless_requested(self, coe_advisor, client):
        api_json = _api_search(client, 'da', students=True)
        assert 'courses' not in api_json
        assert 'totalCourseCount' not in api_json

    def test_search_with_missing_input(self, client, fake_auth):
        """Course search is nothing without input."""
        fake_auth.login('2040')
        _api_search(client, ' \t  ', courses=True, expected_status_code=400)

    def test_search_by_name_includes_courses_if_requested(self, coe_advisor, client):
        """A name search returns matching courses if any."""
        api_json = _api_search(client, 'paul', courses=True, students=True)
        assert api_json['courses'] == []

        api_json = _api_search(client, 'da', courses=True, students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Deborah Davies')
        courses = api_json['courses']
        assert len(courses) == 1
        assert api_json['totalCourseCount'] == 1
        assert courses[0] == {
            'termId': '2178',
            'sectionId': '21057',
            'courseName': 'DANISH 1A',
            'courseTitle': 'Beginning Danish',
            'instructionFormat': 'LEC',
            'sectionNum': '001',
            'instructors': 'Karen Blixen',
        }

    def test_search_by_name_normalizes_queries(self, coe_advisor, client):
        queries = ['MATH 16A', 'Math 16 A', 'math  16a']
        for query in queries:
            self._assert_finds_math_16a(client, query)

    def test_search_by_abbreviated_subject_area_returns_courses(self, coe_advisor, client):
        self._assert_finds_math_16a(client, 'Ma 16A')

    def test_search_by_catalog_id_alone_returns_courses(self, coe_advisor, client):
        api_json = _api_search(client, '1A', courses=True, students=True)
        courses = api_json['courses']
        assert len(courses) == 3
        assert api_json['totalCourseCount'] == 3
        assert len([c for c in courses if c['courseName'] == 'MATH 1A']) == 2
        assert len([c for c in courses if c['courseName'] == 'DANISH 1A']) == 1

    def test_search_courses_no_canvas_data_access(self, no_canvas_access_advisor, client):
        """A user with no access to Canvas data cannot search for courses."""
        _api_search(client, '1A', courses=True, students=True, expected_status_code=403)


class TestNoteSearch:
    """Notes search API."""

    @classmethod
    def _assert(cls, api_json, note_count=0, note_ids=()):
        assert 'notes' in api_json
        notes = api_json['notes']
        assert len(notes) == note_count
        for idx, note_id in enumerate(note_ids):
            assert notes[idx].get('id') == note_id

    def test_search_with_missing_input_no_options(self, coe_advisor, client):
        """Notes search is nothing without input when no additional options are set."""
        _api_search(client, ' \t  ', notes=True, expected_status_code=400)

    def test_search_notes(self, coe_advisor, client):
        """Search results include notes ordered by rank."""
        api_json = _api_search(client, 'life', notes=True)
        self._assert(api_json, note_count=1, note_ids=['11667051-00003'])

    def test_search_respects_date_filters(self, coe_advisor, client):
        """Search results include notes updated within provided date range."""
        api_json = _api_search(
            client,
            'making',
            notes=True,
            note_options={
                'dateFrom': '2017-10-31',
                'dateTo': '2017-11-01',
            },
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_note_search_validates_date_formatting(self, coe_advisor, client):
        api_json = _api_search(
            client,
            'Brigitte',
            notes=True,
            note_options={
                'dateFrom': '2017-11-01',
                'dateTo': 'rubbish',
            },
            expected_status_code=400,
        )
        assert api_json['message'] == 'Invalid dateTo value'

    def test_note_search_validates_date_ranges(self, coe_advisor, client):
        api_json = _api_search(
            client,
            'Brigitte',
            notes=True,
            note_options={
                'dateFrom': '2017-11-02',
                'dateTo': '2017-11-01',
            },
            expected_status_code=400,
        )
        assert api_json['message'] == 'dateFrom must be less than dateTo'

    def test_search_with_no_input_and_date(self, coe_advisor, client):
        """Notes search needs no input when date options are set."""
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'dateFrom': '2017-11-01', 'dateTo': '2017-11-02'},
        )
        self._assert(api_json, note_count=4)

    def test_search_with_midnight_creation(self, coe_advisor, client):
        """Notes search correctly returns legacy notes with midnight creation times."""
        def _single_date_search(date):
            api_json = _api_search(
                client,
                'confound',
                notes=True,
                note_options={'dateFrom': date, 'dateTo': date},
            )
            return api_json['notes']
        assert len(_single_date_search('2017-11-01')) == 0
        assert len(_single_date_search('2017-11-02')) == 1
        assert len(_single_date_search('2017-11-03')) == 0

    def test_search_excludes_notes_unless_requested(self, coe_advisor, client):
        """Excludes notes from search results if notes param is false."""
        api_json = _api_search(client, 'life', appointments=True, courses=True, students=True)
        assert 'notes' not in api_json

    def test_search_includes_notes_if_requested(self, coe_advisor, client):
        """Includes notes in search results if notes param is true."""
        api_json = _api_search(client, 'Brigitte', notes=True)
        self._assert(api_json, note_count=2, note_ids=['11667051-00001', '11667051-00002'])

    def test_search_note_with_null_body(self, asc_advisor, client):
        """Finds newly created BOA note when note body is null."""
        response = client.post(
            '/api/notes/create',
            data={
                'authorId': AuthorizedUser.get_id_per_uid(asc_advisor_uid),
                'sids': ['9000000000'],
                'subject': 'Patience is a conquering virtue',
            },
        )
        assert response.status_code == 200
        note = response.json

        api_json = _api_search(client, 'a conquering virtue', notes=True)
        self._assert(api_json, note_count=1, note_ids=[note['id']])

    def test_search_asc_notes(self, asc_advisor, client):
        """Includes ASC notes in search results."""
        api_json = _api_search(client, 'ginger', notes=True)
        self._assert(api_json, note_count=3, note_ids=['11667051-139379', '2345678901-139379', '8901234567-139379'])

    def test_search_notes_by_asc_topic(self, asc_advisor, client):
        """Includes ASC notes with advisor name match in search results."""
        api_json = _api_search(client, 'academic', notes=True)
        self._assert(api_json, note_count=1, note_ids=['11667051-139362'])

    def test_search_by_topic(self, coe_advisor, client):
        """Searches notes by topic if topics option is selected."""
        api_json = _api_search(
            client,
            'making',
            notes=True,
            note_options={'topic': 'Good Show'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_search_with_no_input_and_topic(self, coe_advisor, client):
        """Notes search needs no input when topic set."""
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'topic': 'Good Show'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_search_by_note_author_sis(self, coe_advisor, client):
        """Searches SIS notes by advisor CSID if posted by option is selected."""
        api_json = _api_search(
            client,
            'Brigitte',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_search_by_note_author_asc(self, coe_advisor, client):
        """Searches ASC notes by advisor CSID if posted by option is selected."""
        api_json = _api_search(
            client,
            'Academic',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-139362'])

    def test_search_by_note_author_data_science(self, coe_advisor, client):
        """Searches Data Science notes by advisor CSID if posted by option is selected."""
        api_json = _api_search(
            client,
            'Buyer beware',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-20190801112456'])

    def test_search_with_no_input_and_author(self, coe_advisor, client):
        """Notes search needs no input when author set."""
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=3)

    def test_search_by_student(self, coe_advisor, client):
        """Searches notes by student CSID."""
        api_json = _api_search(
            client,
            'life',
            notes=True,
            note_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00003'])

    def test_search_with_no_input_and_student(self, coe_advisor, client):
        """Notes search needs no input when student set."""
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, note_count=10)

    def test_note_search_limit(self, coe_advisor, client):
        """Limits search to the first n notes."""
        api_json = _api_search(
            client,
            'life',
            notes=True,
            note_options={'limit': '1'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00003'])

    def test_note_search_offset(self, coe_advisor, client):
        """Returns results beginning from the offset."""
        api_json = _api_search(
            client,
            'student',
            notes=True,
            note_options={'offset': '1'},
        )
        self._assert(api_json, note_count=2, note_ids=['9000000000-00002', '9100000000-00001'])

    def test_search_notes_no_canvas_data_access(self, client, no_canvas_access_advisor):
        """A user with no access to Canvas data can still search for notes."""
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, note_count=10)

    def test_search_notes_includes_inactive_students(self, coe_advisor, client):
        api_json = _api_search(client, 'vocation', notes=True)
        self._assert(api_json, note_count=1, note_ids=['2718281828-00001'])


class TestAppointmentSearch:
    """Appointments search API."""

    @classmethod
    def _assert(cls, api_json, appointment_count=0):
        assert 'appointments' in api_json
        appointments = api_json['appointments']
        assert len(api_json['appointments']) == appointment_count
        previous_id = None
        for appointment in appointments:
            if previous_id is not None:
                assert previous_id > appointment.get('id')
            assert appointment['details']
            assert appointment['detailsSnippet']
            assert appointment['student']
            assert appointment['student']['firstName']
            assert appointment['student']['lastName']
            assert appointment['studentSid']

    def test_search_with_missing_input_no_options(self, coe_advisor, client):
        """Appointments search is nothing without input when no additional options are set."""
        _api_search(client, ' \t  ', appointments=True, expected_status_code=400)

    def test_search_appointments(self, coe_advisor, client):
        """Search results include both legacy and BOA-generated appointments."""
        api_json = _api_search(client, 'life', appointments=True)
        self._assert(api_json, appointment_count=3)

    def test_search_by_appointment_cancel_reason(self, coe_advisor, client):
        """Appointments can be searched for by cancel reason and cancel reason explained."""
        appointment = Appointment.find_by_id(1)
        Appointment.cancel(
            appointment_id=appointment.id,
            cancelled_by=AuthorizedUser.get_id_per_uid('6972201'),
            cancel_reason='Sick cat',
            cancel_reason_explained='Student needed to attend to ailing feline.',
        )

        api_json = _api_search(client, 'cat', appointments=True)
        self._assert(api_json, appointment_count=1)

        api_json = _api_search(client, 'feline', appointments=True)
        self._assert(api_json, appointment_count=1)

    def test_search_respects_date_filters(self, app, coe_advisor, client):
        """Search results include appointments created within provided date range."""
        from boac import std_commit
        appointment = Appointment.find_by_id(2)
        appointment.created_at = util.localized_timestamp_to_utc('2017-10-31T00:00:00')
        std_commit(allow_test_environment=True)

        api_json = _api_search(
            client,
            'pick me',
            appointments=True,
            appointment_options={
                'dateFrom': '2017-10-31',
                'dateTo': '2017-11-01',
            },
        )
        self._assert(api_json, appointment_count=1)

    def test_appointment_search_validates_date_formatting(self, coe_advisor, client):
        api_json = _api_search(
            client,
            'Brigitte',
            appointments=True,
            appointment_options={
                'dateFrom': '2017-11-01',
                'dateTo': 'rubbish',
            },
            expected_status_code=400,
        )
        assert api_json['message'] == 'Invalid dateTo value'

    def test_appointment_search_validates_date_ranges(self, coe_advisor, client):
        api_json = _api_search(
            client,
            'Brigitte',
            appointments=True,
            appointment_options={
                'dateFrom': '2017-11-02',
                'dateTo': '2017-11-01',
            },
            expected_status_code=400,
        )
        assert api_json['message'] == 'dateFrom must be less than dateTo'

    def test_appointment_search_with_no_input_and_date(self, coe_advisor, client):
        """Appointments search needs no input when date options are set."""
        from boac import db, std_commit
        appointment = Appointment.find_by_id(2)
        appointment.created_at = util.localized_timestamp_to_utc('2017-11-01T00:00:00')
        std_commit()
        db.session.refresh(appointment)

        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'dateFrom': '2017-11-01', 'dateTo': '2017-11-02'},
        )
        self._assert(api_json, appointment_count=3)

    def test_search_excludes_appointments_unless_requested(self, coe_advisor, client):
        """Excludes appointments from search results if appointments param is false."""
        api_json = _api_search(client, 'life', courses=True, students=True, notes=True)
        assert 'appointments' not in api_json

    def test_search_appointments_by_topic(self, coe_advisor, client):
        """Searches appointments by topic if topics option is selected."""
        api_json = _api_search(
            client,
            'making',
            appointments=True,
            appointment_options={'topic': 'Good Show'},
        )
        self._assert(api_json, appointment_count=2)

    def test_search_appointments_with_no_input_and_topic(self, coe_advisor, client):
        """Appointments search needs no input when topic set."""
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'topic': 'Good Show'},
        )
        self._assert(api_json, appointment_count=3)

    def test_search_by_appointment_scheduler(self, coe_advisor, client):
        """Searches appointments by advisor UID if posted by option is selected."""
        api_json = _api_search(
            client,
            'making',
            appointments=True,
            appointment_options={'advisorUid': '90412'},
        )
        self._assert(api_json, appointment_count=1)

    def test_search_appointments_with_no_input_and_author(self, coe_advisor, client):
        """Appointments search needs no input when author set."""
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'advisorUid': '90412'},
        )
        self._assert(api_json, appointment_count=4)

    def test_search_appointments_by_student(self, coe_advisor, client):
        """Searches appointments by student CSID."""
        api_json = _api_search(
            client,
            'life',
            appointments=True,
            appointment_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=1)

    def test_search_appointments_with_no_input_and_student(self, coe_advisor, client):
        """Appointments search needs no input when student set."""
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=5)

    def test_appointments_search_limit(self, coe_advisor, client):
        """Limits search to the first n appointments."""
        api_json = _api_search(
            client,
            'life',
            appointments=True,
            appointment_options={'limit': '1'},
        )
        self._assert(api_json, appointment_count=1)

    def test_appointments_search_offset(self, coe_advisor, client):
        """Returns appointment results beginning from the offset."""
        api_json = _api_search(
            client,
            'life',
            appointments=True,
            appointment_options={'offset': '1'},
        )
        self._assert(api_json, appointment_count=2)

    def test_search_appointments_no_canvas_data_access(self, client, no_canvas_access_advisor):
        """A user with no access to Canvas data can still search for appointments."""
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=5)

    def test_search_appointments_includes_inactive_students(self, coe_advisor, client):
        api_json = _api_search(client, 'pez', appointments=True)
        self._assert(api_json, appointment_count=1)


class TestAdmittedStudentSearch:
    """Admitted students search API."""

    @classmethod
    def _api_search_admits(cls, client, search_phrase, order_by='cs_empl_id', expected_status_code=200):
        response = client.post(
            '/api/search/admits',
            content_type='application/json',
            data=json.dumps({
                'searchPhrase': search_phrase,
                'orderBy': order_by,
            }),
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _assert(cls, api_json, admit_count=0):
        assert 'admits' in api_json
        assert 'totalAdmitCount' in api_json
        admits = api_json['admits']
        assert len(admits) == admit_count
        assert api_json['totalAdmitCount'] == admit_count
        for admit in admits:
            assert admit['csEmplId']
            assert admit['firstName']
            assert admit['lastName']
            assert 'currentSir' in admit
            assert 'specialProgramCep' in admit
            assert 'reentryStatus' in admit
            assert 'firstGenerationCollege' in admit
            assert 'residencyCategory' in admit
            assert 'urem' in admit
            assert 'applicationFeeWaiverFlag' in admit
            assert 'freshmanOrTransfer' in admit

    def test_search_admits_when_feature_flag_false(self, client, ce3_advisor):
        """Excludes admit results if feature flag is false."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            api_json = self._api_search_admits(client, '0000', expected_status_code=401)
            assert 'admits' not in api_json

    def test_search_admits_performed_by_non_ce3_advisor(self, client, coe_advisor):
        """Excludes admit results if user is a non-CE3 advisor."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            api_json = self._api_search_admits(client, '0000', expected_status_code=401)
            assert 'admits' not in api_json

    def test_search_admits_by_sid(self, client, ce3_advisor):
        """Search by SID yields admit results."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            api_json = self._api_search_admits(client, '0000')
            self._assert(api_json, admit_count=1)

    def test_search_admits_by_name(self, client, ce3_advisor):
        """Search by first, last, and/or middle name yields admits."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            api_json = self._api_search_admits(client, 'da')
            self._assert(api_json, admit_count=2)

            api_json = self._api_search_admits(client, 'da de')
            self._assert(api_json, admit_count=1)

            api_json = self._api_search_admits(client, 'j ly')
            self._assert(api_json, admit_count=1)

    def test_search_admits_ordering(self, client, ce3_advisor):
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            api_json = self._api_search_admits(client, 'da', order_by='first_name')
            self._assert(api_json, admit_count=2)
            assert(api_json['admits'][0]['firstName']) == 'Daniel'
            assert(api_json['admits'][1]['firstName']) == 'Deborah'

            api_json = self._api_search_admits(client, 'da', order_by='last_name')
            self._assert(api_json, admit_count=2)
            assert(api_json['admits'][0]['lastName']) == 'Davies'
            assert(api_json['admits'][1]['lastName']) == 'Mcknight'


class TestSearchHistory:
    """Search history API."""

    @classmethod
    def _api_my_search_history(cls, client, expected_status_code=200):
        response = client.get('/api/search/my_search_history')
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_add_to_my_search_history(cls, client, phrase, expected_status_code=200):
        response = client.post(
            '/api/search/add_to_search_history',
            content_type='application/json',
            data=json.dumps({
                'phrase': phrase,
            }),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_my_search_history(client, expected_status_code=401)

    def test_not_authenticated_update_search_history(self, client):
        """/add_to_search_history returns 401 if not authenticated."""
        self._api_add_to_my_search_history(client, 'I want it all', expected_status_code=401)

    def test_empty_search_history(self, client, coe_advisor):
        """Returns empty array if user has no search history."""
        assert self._api_my_search_history(client) == []

    def test_blank_input(self, asc_advisor, client):
        """Blank search phrase is not added to search history."""
        self._api_add_to_my_search_history(client, '    ', expected_status_code=400)
        assert self._api_my_search_history(client=client) == ['Moe', 'Larry', 'Curly']

    def test_search_history(self, asc_advisor, client):
        """Returns search history."""
        api_json = self._api_my_search_history(client)
        expected_history = ['Moe', 'Larry', 'Curly']
        assert api_json == expected_history
        # Searching for same phrase twice should cause no change in search history
        self._api_add_to_my_search_history(client, 'Moe')
        assert self._api_my_search_history(client=client) == expected_history

    def test_search_history_truncate(self, client, coe_scheduler):
        # The string expected in search history will be shorter than MAX_LENGTH
        expected_length = AuthorizedUser.SEARCH_HISTORY_ITEM_MAX_LENGTH - 20
        expected_search_history_string = 's' * expected_length
        search_string = f'  {expected_search_history_string}  this_suffix_has_no_whitespace_and_will_be_dropped  '
        self._api_add_to_my_search_history(client, search_string)
        assert self._api_my_search_history(client)[0] == expected_search_history_string

        # A whole lot of whitespace in search string
        search_string = '       aa       bbb     c  ' * AuthorizedUser.SEARCH_HISTORY_ITEM_MAX_LENGTH
        self._api_add_to_my_search_history(client, search_string)
        actual_search_history_string = self._api_my_search_history(client)[0]
        assert actual_search_history_string[0] in 'abc'
        assert actual_search_history_string[-1] in 'abc'
        for snippet in (' aa ', ' bbb ', ' c '):
            assert snippet in actual_search_history_string
        assert '  ' not in actual_search_history_string

    def test_search_history_truncate_when_no_whitespace(self, client, coe_scheduler):
        expected_search_history_string = 's' * AuthorizedUser.SEARCH_HISTORY_ITEM_MAX_LENGTH
        no_whitespace_in_search_string = f'{expected_search_history_string}truncate_me'
        self._api_add_to_my_search_history(client, f'  {no_whitespace_in_search_string}   ')
        assert self._api_my_search_history(client)[0] == expected_search_history_string

    def test_manage_search_history(self, admin_login, client):
        """Properly manages search history."""
        assert self._api_my_search_history(client) == []
        polythene_pam = 'Polythene Pam'
        phrases = [
            'Sun King',
            'Mean Mr. Mustard',
            polythene_pam,
            'She Came In Through the Bathroom Window',
            'Golden Slumbers',
        ]
        for phrase in phrases:
            self._api_add_to_my_search_history(client, phrase)
        std_commit(allow_test_environment=True)
        # Expect list above, in reverse order
        search_history = phrases[::-1]
        assert self._api_my_search_history(client) == search_history
        # Search for phrase a second time and it will move to start of list
        self._api_add_to_my_search_history(client, polythene_pam)
        std_commit(allow_test_environment=True)

        search_history = self._api_my_search_history(client)
        assert search_history == [
            polythene_pam,
            'Golden Slumbers',
            'She Came In Through the Bathroom Window',
            'Mean Mr. Mustard',
            'Sun King',
        ]
        # Finally, verify USER_SEARCH_HISTORY_MAX_SIZE setting
        self._api_add_to_my_search_history(client, 'Carry That Weight')
        self._api_add_to_my_search_history(client, 'The End')
        search_history = self._api_my_search_history(client)
        assert search_history == [
            'The End',
            'Carry That Weight',
            polythene_pam,
            'Golden Slumbers',
            'She Came In Through the Bathroom Window',
        ]


class TestFindAdvisorsByName:
    """Advisors by name API."""

    @classmethod
    def _api_search_advisors(cls, client, query, expected_status_code=200):
        response = client.get(f'/api/search/advisors/find_by_name?q={query}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        self._api_search_advisors(client, 'Vis', expected_status_code=401)

    def test_user_without_advising_data_access(self, client, coe_advisor_no_advising_data):
        """Denies access to a user who cannot access notes and appointments."""
        self._api_search_advisors(client, 'Vis', expected_status_code=401)

    def test_find_advisors_by_name(self, client, coe_advisor):
        """Finds matches including appointment advisors."""
        response = self._api_search_advisors(client, 'Vis')
        assert len(response) == 1
        labels = [s['label'] for s in response]
        assert 'COE Add Visor' in labels

    def test_find_note_authors_by_name(self, client, coe_advisor, mock_advising_note):
        """Finds matches including authors of legacy and non-legacy notes."""
        response = self._api_search_advisors(client, 'Jo')
        assert len(response) == 4
        labels = set([s['label'] for s in response])
        assert labels == {'John Deleted-in-BOA', 'Joni Mitchell', 'Joni Mitchell CC', 'Robert Johnson'}


def _api_search(
        client,
        phrase,
        appointments=False,
        courses=False,
        notes=False,
        students=False,
        appointment_options=None,
        note_options=None,
        order_by=None,
        offset=None,
        limit=None,
        expected_status_code=200,
):
    response = client.post(
        '/api/search',
        content_type='application/json',
        data=json.dumps({
            'appointments': appointments,
            'courses': courses,
            'notes': notes,
            'students': students,
            'searchPhrase': phrase,
            'appointmentOptions': appointment_options,
            'noteOptions': note_options,
            'orderBy': order_by,
            'offset': offset,
            'limit': limit,
        }),
    )
    assert response.status_code == expected_status_code
    return response.json


def _get_common_sids(student_list_1, student_list_2):
    sid_list_1 = [s['sid'] for s in student_list_1]
    sid_list_2 = [s['sid'] for s in student_list_2]
    return list(set(sid_list_1) & set(sid_list_2))
