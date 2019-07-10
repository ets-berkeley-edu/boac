"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.externals import data_loch
import pytest
import simplejson as json


@pytest.fixture()
def admin_login(fake_auth):
    fake_auth.login('2040')


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login('1081940')


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login('1133399')


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
        response = client.post('/api/search')
        assert response.status_code == 401

    def test_unauthorized_request_for_athletic_study_center_data(self, client, fake_auth):
        """In order to access intensive_cohort, inactive status, etc. the user must be either ASC or Admin."""
        fake_auth.login('1022796')
        args = {'students': True, 'searchPhrase': 'John', 'isInactiveAsc': False}
        response = client.post('/api/search', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 403

    def test_search_with_missing_input(self, client, fake_auth):
        """Search is nothing without input."""
        fake_auth.login('2040')
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': ' \t  '}), content_type='application/json')
        assert response.status_code == 400

    def test_search_by_sid_snippet(self, client, fake_auth, asc_inactive_students):
        """Search by snippet of SID."""
        def _search_students_as_user(uid, sid_snippet):
            fake_auth.login(uid)
            response = client.post(
                '/api/search',
                data=json.dumps({'students': True, 'searchPhrase': sid_snippet}),
                content_type='application/json',
            )
            assert response.status_code == 200
            return response.json['students'], response.json['totalStudentCount']

        sid_snippet = '89012'
        # Admin user and ASC advisor get same results
        for uid in ['2040', '1081940']:
            students, total_student_count = _search_students_as_user(uid, sid_snippet)
            assert len(students) == total_student_count == 2
            assert _get_common_sids(asc_inactive_students, students)

    def test_alerts_in_search_results(self, client, create_alerts, fake_auth):
        """Search results include alert counts."""
        fake_auth.login('2040')
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'davies'}), content_type='application/json')
        assert response.status_code == 200
        assert response.json['students'][0]['alertCount'] == 3

    def test_summary_profiles_in_search_results(self, client, fake_auth):
        fake_auth.login('2040')
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'davies'}), content_type='application/json')
        assert response.json['students'][0]['cumulativeGPA'] == 3.8
        assert response.json['students'][0]['cumulativeUnits'] == 101.3
        assert response.json['students'][0]['expectedGraduationTerm']['name'] == 'Fall 2019'
        assert response.json['students'][0]['level'] == 'Junior'
        assert response.json['students'][0]['termGpa'][0]['gpa'] == 2.9

    def test_search_by_name_snippet(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'dav'}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == response.json['totalStudentCount'] == 3
        assert ['Crossman', 'Davies', 'Doolittle'] == [s['lastName'] for s in students]

    def test_search_by_full_name_snippet(self, client, fake_auth):
        """Search by snippet of full name."""
        fake_auth.login('2040')
        permutations = ['david c', 'john  david cro', 'john    cross', ' crossman, j ']
        for phrase in permutations:
            response = client.post(
                '/api/search',
                data=json.dumps({'students': True, 'searchPhrase': phrase}),
                content_type='application/json',
            )
            message_if_fail = f'Unexpected result(s) when search phrase={phrase}'
            assert response.status_code == 200, message_if_fail
            students = response.json['students']
            assert len(students) == response.json['totalStudentCount'] == 1, message_if_fail
            assert students[0]['lastName'] == 'Crossman', message_if_fail

    def test_search_by_name_coe(self, coe_advisor, client):
        """A COE name search finds all Pauls, including COE-specific data for COE Pauls."""
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'Paul'}), content_type='application/json')
        students = response.json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and s['coeProfile']['isActiveCoe'] is True)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and s['coeProfile']['isActiveCoe'] is False)
        assert next(s for s in students if s['name'] == 'Paul Kerschen' and 'coeProfile' not in s)
        for s in students:
            assert 'athleticsProfile' not in s

    def test_search_by_name_asc(self, asc_advisor, client):
        """An ASC advisor finds all Pauls, including ASC-specific data for ASC Pauls."""
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'Paul'}), content_type='application/json')
        students = response.json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Kerschen' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and 'athleticsProfile' not in s)
        for s in students:
            assert 'coeProfile' not in s

    def test_search_by_name_admin(self, admin_login, client):
        """An admin name search finds all Pauls, including both ASC and COE data."""
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'Paul'}), content_type='application/json')
        students = response.json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Kerschen' and s['athleticsProfile']['inIntensiveCohort'] is True)
        assert next(s for s in students if s['name'] == 'Paul Farestveit' and 'athleticsProfile' in s and 'coeProfile' in s)
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli-O\'Rourke' and s['coeProfile']['isActiveCoe'] is False)

    def test_search_by_name_with_special_characters(self, admin_login, client):
        """Search by name where name has special characters: hyphen, etc."""
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'Pauli-O\'Rourke'}), content_type='application/json')
        students = response.json['students']
        assert len(students) == 1
        assert students[0]['name'] == 'Wolfgang Pauli-O\'Rourke'

    def test_search_order_by_offset_limit(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        args = {
            'students': True,
            'searchPhrase': 'dav',
            'orderBy': 'major',
            'offset': 1,
            'limit': 1,
        }
        response = client.post('/api/search', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 200
        assert response.json['totalStudentCount'] == 3
        assert len(response.json['students']) == 1
        assert 'Crossman' == response.json['students'][0]['lastName']


class TestCourseSearch:
    """Course search API."""

    def test_search_by_name_excludes_courses_unless_requested(self, coe_advisor, client):
        response = client.post('/api/search', data=json.dumps({'students': True, 'searchPhrase': 'da'}), content_type='application/json')
        assert 'courses' not in response.json
        assert 'totalCourseCount' not in response.json

    def test_search_by_name_includes_courses_if_requested(self, coe_advisor, client):
        """A name search returns matching courses if any."""
        response = client.post(
            '/api/search',
            data=json.dumps({'students': True, 'courses': True, 'searchPhrase': 'paul'}),
            content_type='application/json',
        )
        assert response.json['courses'] == []
        response = client.post(
            '/api/search',
            data=json.dumps({'students': True, 'courses': True, 'searchPhrase': 'da'}),
            content_type='application/json',
        )
        students = response.json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Deborah Davies')
        courses = response.json['courses']
        assert len(courses) == 1
        assert response.json['totalCourseCount'] == 1
        assert courses[0] == {
            'termId': '2178',
            'sectionId': '21057',
            'courseName': 'DANISH 1A',
            'courseTitle': 'Beginning Danish',
            'instructionFormat': 'LEC',
            'sectionNum': '001',
            'instructors': 'Karen Blixen',
        }

    def _assert_finds_math_16a(self, client, query):
        response = client.post(
            '/api/search',
            data=json.dumps({'students': True, 'courses': True, 'searchPhrase': query}),
            content_type='application/json',
        )
        courses = response.json['courses']
        assert len(courses) == 2
        assert response.json['totalCourseCount'] == 2
        for course in courses:
            assert course['courseName'] == 'MATH 16A'

    def test_search_by_name_normalizes_queries(self, coe_advisor, client):
        queries = ['MATH 16A', 'Math 16 A', 'math  16a']
        for query in queries:
            self._assert_finds_math_16a(client, query)

    def test_search_by_abbreviated_subject_area_returns_courses(self, coe_advisor, client):
        self._assert_finds_math_16a(client, 'Ma 16A')

    def test_search_by_catalog_id_alone_returns_courses(self, coe_advisor, client):
        response = client.post(
            '/api/search',
            data=json.dumps({'students': True, 'courses': True, 'searchPhrase': '1A'}),
            content_type='application/json',
        )
        courses = response.json['courses']
        assert len(courses) == 3
        assert response.json['totalCourseCount'] == 3
        assert len([c for c in courses if c['courseName'] == 'MATH 1A']) == 2
        assert len([c for c in courses if c['courseName'] == 'DANISH 1A']) == 1


class TestNoteSearch:
    """Note search API."""

    def test_note_search_respects_date_filters(self, coe_advisor, client):
        response = client.post(
            '/api/search',
            data=json.dumps({
                'notes': True,
                'searchPhrase': 'Brigitte',
                'noteOptions': {
                    'dateFrom': '2017-11-01',
                    'dateTo': '2017-11-02',
                },
            }),
            content_type='application/json',
        )
        notes = response.json['notes']
        assert len(notes) == 1

    def test_note_search_validates_date_formatting(self, coe_advisor, client):
        response = client.post(
            '/api/search',
            data=json.dumps({
                'notes': True,
                'searchPhrase': 'Brigitte',
                'noteOptions': {
                    'dateFrom': '2017-11-01',
                    'dateTo': 'rubbish',
                },
            }),
            content_type='application/json',
        )
        assert response.status_code == 400
        assert response.json['message'] == 'Invalid dateTo value'

    def test_note_search_validates_date_ranges(self, coe_advisor, client):
        response = client.post(
            '/api/search',
            data=json.dumps({
                'notes': True,
                'searchPhrase': 'Brigitte',
                'noteOptions': {
                    'dateFrom': '2017-11-02',
                    'dateTo': '2017-11-01',
                },
            }),
            content_type='application/json',
        )
        assert response.status_code == 400
        assert response.json['message'] == 'dateFrom must be less than dateTo'

    def test_search_excludes_notes_unless_requested(self, coe_advisor, client):
        """Excludes notes from search results if notes param is false."""
        response = client.post(
            '/api/search',
            data=json.dumps({'students': True, 'courses': True, 'searchPhrase': 'Brigitte'}),
            content_type='application/json',
        )
        assert 'notes' not in response.json

    def test_search_includes_notes_if_requested(self, coe_advisor, client):
        """Includes notes in search results if notes param is true."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'Brigitte'}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 2
        assert notes[0].get('id') == '11667051-00001'
        assert notes[1].get('id') == '11667051-00002'

    def test_search_notes_by_asc_advisor_name(self, asc_advisor, client):
        """Includes ASC notes with advisor name match in search results."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'ginger'}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 3
        assert notes[0].get('id') == '11667051-139379'
        assert notes[1].get('id') == '2345678901-139379'
        assert notes[2].get('id') == '8901234567-139379'

    def test_search_notes_by_asc_topic(self, asc_advisor, client):
        """Includes ASC notes with advisor name match in search results."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'academic'}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 1
        assert notes[0].get('id') == '11667051-139362'

    def test_search_by_note_topic(self, coe_advisor, client):
        """Searches notes by topic if topics option is selected."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'Brigitte', 'noteOptions': {'topic': 'Good Show'}}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 1
        assert notes[0].get('id') == '11667051-00001'

    def test_search_by_note_author_sis(self, coe_advisor, client):
        """Searches notes by SIS advisor name if posted by option is selected."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'Brigitte', 'noteOptions': {'authorCsid': '800700600'}}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 1
        assert notes[0].get('id') == '11667051-00001'

    def test_search_by_note_author_asc(self, coe_advisor, client):
        """Searches notes by ASC advisor name if posted by option is selected."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'Academic', 'noteOptions': {'authorCsid': '800700600'}}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 1
        assert notes[0].get('id') == '11667051-139362'

    def test_search_by_note_student(self, coe_advisor, client):
        """Searches notes by student if posted by option is selected."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'student', 'noteOptions': {'studentCsid': '9100000000'}}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 1
        assert notes[0].get('id') == '9100000000-00001'

    def test_note_search_limit(self, coe_advisor, client):
        """Limits search to the first n results."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'student', 'noteOptions': {'limit': '2'}}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 2
        assert notes[0].get('id') == '9000000000-00001'
        assert notes[1].get('id') == '9000000000-00002'

    def test_note_search_offset(self, coe_advisor, client):
        """Limits search to the first n results."""
        response = client.post(
            '/api/search',
            data=json.dumps({'notes': True, 'searchPhrase': 'student', 'noteOptions': {'offset': '1'}}),
            content_type='application/json',
        )
        assert 'notes' in response.json
        notes = response.json['notes']
        assert len(notes) == 2
        assert notes[0].get('id') == '9000000000-00002'
        assert notes[1].get('id') == '9100000000-00001'


def _get_common_sids(student_list_1, student_list_2):
    sid_list_1 = [s['sid'] for s in student_list_1]
    sid_list_2 = [s['sid'] for s in student_list_2]
    return list(set(sid_list_1) & set(sid_list_2))
