"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

import pytest
import simplejson as json

from boac import std_commit
from boac.externals import data_loch
from boac.models.authorized_user import AuthorizedUser
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from boac.models.note import Note

admin_uid = '2040'
asc_advisor_uid = '1081940'
ce3_advisor_uid = '2525'
coe_advisor_no_advising_data_uid = '1022796'
coe_advisor_uid = '1133399'


@pytest.fixture(scope='session')
def asc_inactive_students():
    return data_loch.safe_execute_rds("""
        SELECT DISTINCT(spi.sid) FROM boac_advising_asc.students s
        JOIN student.student_profile_index spi ON spi.sid = s.sid
        WHERE s.active is FALSE AND spi.academic_career_status = 'active'
    """)


class TestStudentSearch:
    """Student search API."""

    def test_search_not_authenticated(self, client):
        """Search is not available to the world."""
        _api_search(client, 'Hack it!', expected_status_code=401)

    def test_search_with_missing_input(self, client, fake_auth):
        """Student search is nothing without input."""
        fake_auth.login(admin_uid)
        _api_search(client, ' \t  ', students=True, expected_status_code=400)

    def test_search_by_complete_email_address(self, client, fake_auth):
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'debaser@berkeley.edu', students=True)
        students = api_json['students']
        assert len(students) == api_json['totalStudentCount'] == 1
        assert students[0]['lastName'] == 'Doolittle'

    def test_search_by_name_or_email_prefix(self, client, fake_auth):
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'barn', students=True)
        students = api_json['students']
        assert len(students) == api_json['totalStudentCount'] == 2
        assert [s['lastName'] for s in students] == ['Barney', 'Davies']

    def test_search_by_sid_snippet(self, client, fake_auth, asc_inactive_students):
        """Search by snippet of SID."""
        def _search_students_as_user(uid_, sid_snippet_):
            fake_auth.login(uid_)
            api_json = _api_search(client, sid_snippet_, students=True)
            return api_json['students'], api_json['totalStudentCount']

        sid_snippet = '89012'
        # Admin user and ASC advisor get same results
        for uid in ['1081940']:
            students, total_student_count = _search_students_as_user(uid, sid_snippet)
            assert len(students) == total_student_count == 2
            assert _get_common_sids(asc_inactive_students, students)

    def test_search_by_inactive_sid(self, client, fake_auth):
        """Falls back to inactive students when searching by SID."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, '2718281828', students=True)
        assert api_json['totalStudentCount'] == 1
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['sid'] == '2718281828'
        assert students[0]['academicCareerStatus'] == 'Completed'
        assert students[0]['firstName'] == 'Ernest'
        assert students[0]['lastName'] == 'Pontifex'

    def test_search_by_inactive_sid_snippet(self, client, fake_auth):
        """Does not match on inactive SID snippets."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, '271828', students=True)
        assert api_json['totalStudentCount'] == 0
        students = api_json['students']
        assert len(students) == 0

    def test_search_by_inactive_name(self, client, fake_auth):
        """Does not match on inactive student names."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'Pontifex', students=True)
        assert api_json['totalStudentCount'] == 0
        students = api_json['students']
        assert len(students) == 0

    def test_alerts_in_search_results(self, client, create_alerts, fake_auth):  # noqa: ARG002
        """Search results include alert counts."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'davies', students=True)
        assert api_json['students'][0]['alertCount'] == 4

    def test_summary_profiles_in_search_results(self, client, fake_auth):
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'davies', students=True)
        students = api_json['students']
        assert students[0]['academicStanding']['status'] == 'GST'
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert students[0]['level'] == 'Junior'
        assert students[0]['termGpa'][0]['gpa'] == 2.9

    def test_search_by_name_snippet(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'dav', students=True)
        students = api_json['students']
        assert len(students) == api_json['totalStudentCount'] == 3
        assert [s['lastName'] for s in students] == ['Crossman', 'Davies', 'Doolittle']

    def test_search_by_full_name_snippet(self, client, fake_auth):
        """Search by snippet of full name."""
        fake_auth.login(admin_uid)
        permutations = ['david c', 'john  david cro', 'john    cross', ' crossman, j ']
        for phrase in permutations:
            api_json = _api_search(client, phrase, students=True)
            students = api_json['students']
            assert len(students) == api_json['totalStudentCount'] == 1
            assert students[0]['lastName'] == 'Crossman'

    def test_search_by_name_coe(self, client, fake_auth):
        """A COE name search finds all Pauls, including COE-specific data for COE Pauls."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'Paul', students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and s['coeProfile']['isActiveCoe'] is True)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and s['coeProfile']['isActiveCoe'] is False)
        assert next(s for s in students if s['name'] == 'Pauline Kerschen' and 'coeProfile' not in s)
        for s in students:
            assert 'inIntensiveCohort' not in s.get('athleticsProfile', {})

    def test_search_by_name_asc(self, client, fake_auth):
        """An ASC advisor finds all Pauls, including ASC-specific data for ASC Pauls."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_search(client, 'Paul', students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Pauline Kerschen' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and 'athleticsProfile' not in s)
        for s in students:
            assert 'coeProfile' not in s

    def test_search_by_name_admin(self, client, fake_auth):
        """An admin name search finds all Pauls, including both ASC and COE data."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'Paul', students=True)
        students = api_json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Pauline Kerschen' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and 'athleticsProfile' in s and 'coeProfile' in s)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and s['coeProfile']['isActiveCoe'] is False)

    def test_search_by_name_with_special_characters(self, client, fake_auth):
        """Search by name where name has special characters: hyphen, etc."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'Pauli-O\'Rourke', students=True)
        students = api_json['students']
        assert len(students) == 1
        assert students[0]['name'] == 'Wolfgang Pauli-O\'Rourke'

    def test_search_by_name_no_canvas_data_access(self, user_factory, client, fake_auth):
        """A user with no access to Canvas data can still search for students."""
        advisor = user_factory(can_access_canvas_data=False)
        fake_auth.login(advisor.uid)
        api_json = _api_search(client, 'Paul', students=True)
        assert len(api_json['students']) == 3

    def test_search_order_by_offset_limit(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login(admin_uid)
        api_json = _api_search(client, 'dav', students=True, order_by='major', offset=1, limit=1)
        assert api_json['totalStudentCount'] == 3
        assert len(api_json['students']) == 1
        assert api_json['students'][0]['lastName'] == 'Crossman'


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

    def test_search_by_name_excludes_courses_unless_requested(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'da', students=True)
        assert 'courses' not in api_json
        assert 'totalCourseCount' not in api_json

    def test_search_with_missing_input(self, client, fake_auth):
        """Course search is nothing without input."""
        fake_auth.login(admin_uid)
        _api_search(client, ' \t  ', courses=True, expected_status_code=400)

    def test_search_by_name_includes_courses_if_requested(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
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

    def test_search_by_name_normalizes_queries(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        queries = ['MATH 16A', 'Math 16 A', 'math  16a']
        for query in queries:
            self._assert_finds_math_16a(client, query)

    def test_search_by_abbreviated_subject_area_returns_courses(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        self._assert_finds_math_16a(client, 'Ma 16A')

    def test_search_by_catalog_id_alone_returns_courses(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, '1A', courses=True, students=True)
        courses = api_json['courses']
        assert len(courses) == 3
        assert api_json['totalCourseCount'] == 3
        assert len([c for c in courses if c['courseName'] == 'MATH 1A']) == 2
        assert len([c for c in courses if c['courseName'] == 'DANISH 1A']) == 1

    def test_search_courses_no_canvas_data_access(self, user_factory, client, fake_auth):
        """A user with no access to Canvas data cannot search for courses."""
        advisor = user_factory(can_access_canvas_data=False)
        fake_auth.login(advisor.uid)
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

    def test_search_with_missing_input_no_options(self, client, fake_auth):
        """Notes search is nothing without input when no additional options are set."""
        fake_auth.login(coe_advisor_uid)
        _api_search(client, ' \t  ', notes=True, expected_status_code=400)

    def test_search_notes(self, client, fake_auth):
        """Search results include notes ordered by rank."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'life', notes=True)
        self._assert(api_json, note_count=1, note_ids=['11667051-00003'])

    def test_search_respects_date_filters(self, client, fake_auth):
        """Search results include notes updated within provided date range."""
        fake_auth.login(coe_advisor_uid)
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

    def test_note_search_validates_date_formatting(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
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

    def test_note_search_validates_date_ranges(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
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

    def test_note_search_validates_department_codes_are_present(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Independence',
            notes=True,
            note_options={
                'departmentCodes': [],
            },
            expected_status_code=400,
        )
        assert api_json['message'] == 'Department codes not specified'

    def test_note_search_validates_department_codes_are_valid(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Independence',
            notes=True,
            note_options={
                'departmentCodes': ['NOTVALIDDEPARTMENTCODE'],
            },
            expected_status_code=400,
        )
        assert api_json['message'] == 'Invalid department code'

    def test_note_search_matches_correct_department_codes(self, client, fake_auth, mock_advising_note):  # noqa: ARG002
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Independence',
            notes=True,
            note_options={
                'departmentCodes': ['UWASC'],
            },
        )
        assert len(api_json['notes']) == 1
        assert 'Independence' in api_json['notes'][0]['noteSnippet']

    def test_note_search_excludes_incorrect_department_codes(self, client, fake_auth, mock_advising_note):  # noqa: ARG002
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Independence',
            notes=True,
            note_options={
                'departmentCodes': ['ZCEEE'],
            },
        )
        assert len(api_json['notes']) == 0

    def test_note_data_loch_search_department_code(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'happen around us',
            notes=True,
            note_options={
                'departmentCodes': ['EGCEE'],
            },
        )
        assert len(api_json['notes']) == 1

    def test_search_with_no_input_and_date(self, client, fake_auth):
        """Notes search needs no input when date options are set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'dateFrom': '2017-11-01', 'dateTo': '2017-11-02'},
        )
        self._assert(api_json, note_count=4)

    def test_search_with_midnight_creation(self, client, fake_auth):
        """Notes search correctly returns legacy notes with midnight creation times."""
        def _single_date_search(date):
            api_json = _api_search(
                client,
                'confound',
                notes=True,
                note_options={'dateFrom': date, 'dateTo': date},
            )
            return api_json['notes']
        fake_auth.login(coe_advisor_uid)
        assert len(_single_date_search('2017-11-01')) == 0
        assert len(_single_date_search('2017-11-02')) == 1
        assert len(_single_date_search('2017-11-03')) == 0

    def test_search_excludes_notes_unless_requested(self, client, fake_auth):
        """Excludes notes from search results if notes param is false."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'life', appointments=True, courses=True, students=True)
        assert 'notes' not in api_json

    def test_search_includes_notes_if_requested(self, client, fake_auth):
        """Includes notes in search results if notes param is true."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'Brigitte', notes=True)
        self._assert(api_json, note_count=2, note_ids=['11667051-00002', '11667051-00001'])

    def test_search_note_with_null_body(self, client, fake_auth):
        """Finds newly created BOA note when note body is null."""
        fake_auth.login(asc_advisor_uid)
        response = client.post(
            '/api/note/create_draft',
            content_type='application/json',
            data=json.dumps({}),
        )
        assert response.status_code == 200
        note = response.json
        Note.update(
            is_draft=False,
            note_id=note['id'],
            sid='9000000000',
            subject='Patience is a conquering virtue',
        )
        Note.refresh_search_index()
        api_json = _api_search(client, 'a conquering virtue', notes=True)
        self._assert(api_json, note_count=1, note_ids=[note['id']])

    def test_search_asc_notes(self, client, fake_auth):
        """Includes ASC notes in search results."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_search(client, 'ginger', notes=True)
        self._assert(api_json, note_count=3, note_ids=['11667051-139379', '2345678901-139379', '8901234567-139379'])

    def test_search_notes_by_asc_topic(self, client, fake_auth):
        """Includes ASC notes with advisor name match in search results."""
        fake_auth.login(asc_advisor_uid)
        api_json = _api_search(client, 'academic', notes=True)
        self._assert(api_json, note_count=1, note_ids=['11667051-139362'])

    def test_search_by_topic(self, client, fake_auth):
        """Searches notes by topic if topics option is selected."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'making',
            notes=True,
            note_options={'topic': 'Good Show'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_search_with_no_input_and_topic(self, client, fake_auth):
        """Notes search needs no input when topic set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'topic': 'Good Show'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_search_by_note_author_sis(self, client, fake_auth):
        """Searches SIS notes by advisor CSID if posted by option is selected."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Brigitte',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00001'])

    def test_search_by_note_author_asc(self, client, fake_auth):
        """Searches ASC notes by advisor CSID if posted by option is selected."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Academic',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-139362'])

    def test_search_by_note_author_data_science(self, client, fake_auth):
        """Searches Data Science notes by advisor CSID if posted by option is selected."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Buyer beware',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-20190801112456'])

    def test_search_with_no_input_and_author(self, client, fake_auth):
        """Notes search needs no input when author set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'advisorCsid': '800700600'},
        )
        self._assert(api_json, note_count=3)

    def test_search_by_student(self, client, fake_auth):
        """Searches notes by student CSID."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'life',
            notes=True,
            note_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00003'])

    def test_search_with_no_input_and_student(self, client, fake_auth):
        """Notes search needs no input when student set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'studentCsid': '11667051'},
        )
        assert 'notes' in api_json
        notes = api_json['notes']
        assert len(notes) >= 12

    def test_note_search_limit(self, client, fake_auth):
        """Limits search to the first n notes."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'life',
            notes=True,
            note_options={'limit': '1'},
        )
        self._assert(api_json, note_count=1, note_ids=['11667051-00003'])

    def test_note_search_offset(self, client, fake_auth):
        """Returns results beginning from the offset."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'student',
            notes=True,
            note_options={'offset': '1'},
        )
        self._assert(api_json, note_count=2, note_ids=['9100000000-00001', '9000000000-00002'])

    def test_search_notes_no_canvas_data_access(self, user_factory, client, fake_auth):
        """A user with no access to Canvas data can still search for notes."""
        advisor = user_factory(can_access_canvas_data=False)
        fake_auth.login(advisor.uid)
        api_json = _api_search(
            client,
            '',
            notes=True,
            note_options={'studentCsid': '11667051'},
        )
        assert 'notes' in api_json
        notes = api_json['notes']
        assert len(notes) >= 12

    def test_search_notes_includes_inactive_students(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'vocation', notes=True)
        self._assert(api_json, note_count=1, note_ids=['2718281828-00001'])

    def test_search_finds_note_comment_match(self, client, fake_auth, mock_advising_note_with_comments):
        """Note search returns a result with parentNoteId when a comment body matches the query."""
        parent_note = mock_advising_note_with_comments
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'note author', notes=True)
        notes = api_json['notes']
        comment_results = [n for n in notes if n.get('parentNoteId') == parent_note.id]
        assert len(comment_results) >= 1
        assert comment_results[0]['studentSid'] == parent_note.sid


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

    def test_search_with_missing_input_no_options(self, client, fake_auth):
        """Appointments search is nothing without input when no additional options are set."""
        fake_auth.login(coe_advisor_uid)
        _api_search(client, ' \t  ', appointments=True, expected_status_code=400)

    def test_search_appointments(self, client, fake_auth):
        """Search results include legacy appointments."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'life', appointments=True)
        self._assert(api_json, appointment_count=1)

    def test_search_respects_date_filters(self, client, fake_auth):
        """Search results include appointments created within provided date range."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'art',
            appointments=True,
            appointment_options={
                'dateFrom': '2017-11-01',
                'dateTo': '2017-11-02',
            },
        )
        self._assert(api_json, appointment_count=1)

    def test_appointment_search_validates_date_formatting(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
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

    def test_appointment_search_validates_date_ranges(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
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

    def test_appointment_search_with_no_input_and_date(self, client, fake_auth):
        """Appointments search needs no input when date options are set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'dateFrom': '2017-11-01', 'dateTo': '2017-11-06'},
        )
        self._assert(api_json, appointment_count=3)

    def test_search_excludes_appointments_unless_requested(self, client, fake_auth):
        """Excludes appointments from search results if appointments param is false."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'life', courses=True, students=True, notes=True)
        assert 'appointments' not in api_json

    def test_search_by_appointment_scheduler(self, client, fake_auth):
        """Searches appointments by advisor UID if posted by option is selected."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'union',
            appointments=True,
            appointment_options={'advisorUid': '1081940'},
        )
        self._assert(api_json, appointment_count=1)

    def test_search_appointments_with_no_input_and_author(self, client, fake_auth):
        """Appointments search needs no input when author set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'advisorUid': '1081940'},
        )
        self._assert(api_json, appointment_count=2)

    def test_search_appointments_by_student(self, client, fake_auth):
        """Searches appointments by student CSID."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'wingspan',
            appointments=True,
            appointment_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=1)

    def test_search_appointments_with_no_input_and_student(self, client, fake_auth):
        """Appointments search needs no input when student set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=3)

    def test_appointments_search_limit(self, client, fake_auth):
        """Limits search to the first n appointments."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'limit': '1', 'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=1)

    def test_appointments_search_offset(self, client, fake_auth):
        """Returns appointment results beginning from the offset."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'offset': '1', 'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=2)

    def test_search_appointments_no_canvas_data_access(self, user_factory, client, fake_auth):
        """A user with no access to Canvas data can still search for appointments."""
        advisor = user_factory(can_access_canvas_data=False)
        fake_auth.login(advisor.uid)
        api_json = _api_search(
            client,
            '',
            appointments=True,
            appointment_options={'studentCsid': '11667051'},
        )
        self._assert(api_json, appointment_count=3)

    def test_search_appointments_includes_inactive_students(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'pez', appointments=True)
        self._assert(api_json, appointment_count=1)

    def test_search_appointments_by_dept_code(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'perfect union',
            appointments=True,
            appointment_options={'departmentCodes': ['EGCEE']},
        )
        self._assert(api_json, appointment_count=1)

    def test_search_finds_appointment_comment(self, client, fake_auth):
        """Search finds an appointment via comment body text, returned as kind=commentOnAppointment."""
        comment_parent = CommentParent.find_or_create('appointment', '11667051-00010')
        comment = Comment.create(
            comment_parent_id=comment_parent.id,
            author_uid=coe_advisor_uid,
            author_name='COE Advisor',
            author_role='advisor',
            author_dept_codes=['COENG'],
            body='A pterodactyl has exceptional wingspan.',
        )
        try:
            fake_auth.login(coe_advisor_uid)
            api_json = _api_search(client, 'pterodactyl', appointments=True)
            appointments = api_json['appointments']
            comment_results = [a for a in appointments if a.get('kind') == 'commentOnAppointment']
            assert len(comment_results) == 1
            result = comment_results[0]
            assert result['studentSid'] == '11667051'
            assert result['parentType'] == 'appointment'
            assert result['parentId'] == '11667051-00010'
            assert 'pterodactyl' in result['snippet']
        finally:
            comment.soft_delete()


class TestEformSearch:
    """eForm search API."""

    def test_search_eforms_excluded_unless_requested(self, client, fake_auth):
        """Excludes eForms from results when neither notes nor eForms param is set."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'Unit Change', students=True)
        assert 'eforms' not in api_json

    def test_search_eforms_included_when_notes_requested(self, client, fake_auth):
        """Includes eForms in results when notes param is true."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'Unit Change', notes=True)
        assert 'eforms' in api_json

    def test_search_eforms_body(self, client, fake_auth):
        """Finds a late-drop eForm by body content."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(client, 'Unit Change', eforms=True)
        eforms = api_json['eforms']
        assert len(eforms) >= 1
        assert api_json['totalEformCount'] >= 1
        eform = next((e for e in eforms if e.get('studentSid') == '11667051'), None)
        assert eform is not None
        assert eform['kind'] == 'eform'
        assert eform['parentType'] == 'late_drop_eform'
        assert eform['student']['sid'] == '11667051'

    def test_search_eforms_by_student_csid(self, client, fake_auth):
        """Filters eForm results by student SID."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_search(
            client,
            'Late Grading Basis Change',
            eforms=True,
            note_options={'studentCsid': '9000000000'},
        )
        eforms = api_json['eforms']
        assert len(eforms) == 1
        assert eforms[0]['studentSid'] == '9000000000'
        assert eforms[0]['kind'] == 'eform'

    def test_search_eforms_comment(self, client, fake_auth):
        """Finds an eForm via comment body text, returned as kind=commentOnEform."""
        comment_parent = CommentParent.find_or_create('late_drop_eform', 'eform-10096')
        comment = Comment.create(
            comment_parent_id=comment_parent.id,
            author_uid=coe_advisor_uid,
            author_name='COE Advisor',
            author_role='advisor',
            author_dept_codes=['COENG'],
            body='A bougainvillea grows along the fence.',
        )
        try:
            fake_auth.login(coe_advisor_uid)
            api_json = _api_search(client, 'bougainvillea', eforms=True)
            eforms = api_json['eforms']
            assert len(eforms) == 1
            result = eforms[0]
            assert result['kind'] == 'commentOnEform'
            assert result['studentSid'] == '11667051'
            assert result['parentType'] == 'late_drop_eform'
            assert result['parentId'] == 'eform-10096'
            assert 'bougainvillea' in result['snippet']
        finally:
            comment.soft_delete()

    def test_search_eforms_comment_excludes_other_student(self, client, fake_auth):
        """Eform comment search filtered by student SID excludes comments on other students' eForms."""
        comment_parent = CommentParent.find_or_create('late_drop_eform', 'eform-10096')
        comment = Comment.create(
            comment_parent_id=comment_parent.id,
            author_uid=coe_advisor_uid,
            author_name='COE Advisor',
            author_role='advisor',
            author_dept_codes=['COENG'],
            body='A frangipani blooms in summer.',
        )
        try:
            fake_auth.login(coe_advisor_uid)
            # eform-10096 belongs to student 11667051; filtering for 9000000000 should return nothing
            api_json = _api_search(
                client,
                'frangipani',
                eforms=True,
                note_options={'studentCsid': '9000000000'},
            )
            assert api_json['eforms'] == []
        finally:
            comment.soft_delete()


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

    def test_search_admits_performed_by_non_ce3_advisor(self, client, fake_auth):
        """Excludes admit results if user is a non-CE3 advisor."""
        fake_auth.login(coe_advisor_uid)
        api_json = self._api_search_admits(client, '0000', expected_status_code=401)
        assert 'admits' not in api_json

    def test_search_admits_by_sid(self, client, fake_auth):
        """Search by SID yields admit results."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_search_admits(client, '0000')
        self._assert(api_json, admit_count=1)

    def test_search_admits_by_name(self, client, fake_auth):
        """Search by first, last, and/or middle name yields admits."""
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_search_admits(client, 'da')
        self._assert(api_json, admit_count=2)

        api_json = self._api_search_admits(client, 'da de')
        self._assert(api_json, admit_count=1)

        api_json = self._api_search_admits(client, 'j ly')
        self._assert(api_json, admit_count=1)

    def test_search_admits_ordering(self, client, fake_auth):
        fake_auth.login(ce3_advisor_uid)
        api_json = self._api_search_admits(client, 'da', order_by='first_name')
        self._assert(api_json, admit_count=2)
        assert api_json['admits'][0]['firstName'] == 'Daniel'
        assert api_json['admits'][1]['firstName'] == 'Deborah'

        api_json = self._api_search_admits(client, 'da', order_by='last_name')
        self._assert(api_json, admit_count=2)
        assert api_json['admits'][0]['lastName'] == 'Davies'
        assert api_json['admits'][1]['lastName'] == 'Mcknight'


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

    def test_empty_search_history(self, client, fake_auth):
        """Returns empty array if user has no search history."""
        fake_auth.login(coe_advisor_uid)
        assert self._api_my_search_history(client) == []

    def test_blank_input(self, client, fake_auth):
        """Blank search phrase is not added to search history."""
        fake_auth.login(asc_advisor_uid)
        self._api_add_to_my_search_history(client, '    ', expected_status_code=400)
        assert self._api_my_search_history(client=client) == ['Moe', 'Larry', 'Curly']

    def test_search_history(self, client, fake_auth):
        """Returns search history."""
        fake_auth.login(asc_advisor_uid)
        api_json = self._api_my_search_history(client)
        expected_history = ['Moe', 'Larry', 'Curly']
        assert api_json == expected_history
        # Searching for same phrase twice should cause no change in search history
        self._api_add_to_my_search_history(client, 'Moe')
        assert self._api_my_search_history(client=client) == expected_history

    def test_search_history_truncate(self, client, fake_auth):
        # The string expected in search history will be shorter than MAX_LENGTH
        fake_auth.login(coe_advisor_uid)
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

    def test_search_history_truncate_when_no_whitespace(self, client, fake_auth):
        fake_auth.login(coe_advisor_uid)
        expected_search_history_string = 's' * AuthorizedUser.SEARCH_HISTORY_ITEM_MAX_LENGTH
        no_whitespace_in_search_string = f'{expected_search_history_string}truncate_me'
        self._api_add_to_my_search_history(client, f'  {no_whitespace_in_search_string}   ')
        assert self._api_my_search_history(client)[0] == expected_search_history_string

    def test_manage_search_history(self, client, fake_auth):
        """Properly manages search history."""
        fake_auth.login(admin_uid)
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
        polythene_pam_upper = polythene_pam.upper()
        self._api_add_to_my_search_history(client, polythene_pam_upper)
        std_commit(allow_test_environment=True)

        search_history = self._api_my_search_history(client)
        assert search_history == [
            polythene_pam_upper,
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
            polythene_pam_upper,
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

    def test_user_without_advising_data_access(self, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_search_advisors(client, 'Vis', expected_status_code=401)

    def test_find_advisors_by_name(self, client, fake_auth):
        """Finds matches including appointment advisors."""
        fake_auth.login(coe_advisor_uid)
        response = self._api_search_advisors(client, 'Lor')
        assert len(response) == 1
        labels = [s['label'] for s in response]
        assert 'Loramps Glub' in labels

    def test_find_note_authors_by_name(self, client, fake_auth, mock_advising_note):  # noqa: ARG002
        """Finds matches including authors of legacy and non-legacy notes."""
        fake_auth.login(coe_advisor_uid)
        Note.refresh_search_index()
        response = self._api_search_advisors(client, 'Jo')
        assert len(response) >= 4
        labels = set([s['label'] for s in response])
        for label in ('John Deleted-in-BOA', 'Joni Mitchell', 'Joni Mitchell CC', 'Robert Johnson'):
            assert label in labels


def _api_search(
        client,
        phrase,
        appointments=False,
        courses=False,
        eforms=False,
        notes=False,
        students=False,
        appointment_options=None,
        note_options=None,
        order_by=None,
        offset=None,
        limit=None,
        expected_status_code=200,
):
    payload = {
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
    }
    if eforms:
        payload['eForms'] = True
    response = client.post(
        '/api/search',
        content_type='application/json',
        data=json.dumps(payload),
    )
    assert response.status_code == expected_status_code
    return response.json


def _get_common_sids(student_list_1, student_list_2):
    sid_list_1 = [s['sid'] for s in student_list_1]
    sid_list_2 = [s['sid'] for s in student_list_2]
    return list(set(sid_list_1) & set(sid_list_2))
