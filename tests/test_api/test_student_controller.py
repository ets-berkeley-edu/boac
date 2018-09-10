"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


class TestFindStudents:
    """Generic student API calls."""

    def test_all_students(self, asc_advisor, asc_inactive_students, client):
        """Returns a list of students."""
        data = {
            'levels': ['Freshmen', 'Sophomore', 'Junior', 'Senior'],
        }
        response = client.post('/api/students', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 4
        assert not _get_common_sids(asc_inactive_students, students)

    def test_last_name_range(self, client, admin_login):
        """For now, only COE users can access gender data."""
        response = client.post('/api/students', data=json.dumps({'lastNameRange': ['d', 'J']}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 4
        assert students[0]['lastName'] == 'Davies'
        assert students[1]['lastName'] == 'Doolittle'
        assert students[2]['lastName'] == 'Farestveit'
        assert students[3]['lastName'] == 'Jayaprakash'


class TestCollegeOfEngineering:
    """COE-specific API calls."""

    def test_unauthorized_request_for_coe_data(self, client, asc_advisor):
        """In order to access PREP, etc. the user must be either COE or Admin."""
        response = client.post('/api/students', data=json.dumps({'coePrepStatuses': ['did_prep']}), content_type='application/json')
        assert response.status_code == 403

    def test_authorized_request_for_coe_data(self, client, coe_advisor):
        """In order to access PREP, etc. the user must be either COE or Admin."""
        response = client.post('/api/students', data=json.dumps({'coePrepStatuses': ['did_prep']}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 1
        assert students[0]['sid'] == '11667051'

    def test_authorized_request_for_gender(self, client, coe_advisor):
        """For now, only COE users can access gender data."""
        response = client.post('/api/students', data=json.dumps({'genders': ['f']}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 2
        assert students[0]['sid'] == '7890123456'
        assert students[1]['sid'] == '9000000000'

    def test_authorized_request_for_ethnicity(self, client, coe_advisor):
        """For now, only COE users can access ethnicity data."""
        response = client.post('/api/students', data=json.dumps({'ethnicities': ['B', 'H']}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 3
        for index, sid in enumerate(['11667051', '7890123456', '9000000000']):
            assert students[index]['sid'] == sid

    def test_coe_search_by_admin_with_asc_order_by(self, client, admin_login):
        """Admin user can order COE results by ASC criteria."""
        data = {
            'ethnicities': ['B', 'H'],
            'orderBy': 'group_name',
        }
        response = client.post('/api/students', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert ['Men\'s Baseball', 'Women\'s Field Hockey'] == [s['athleticsProfile']['athletics'][0]['groupName'] for s in students]


class TestAthleticsStudyCenter:
    """ASC-specific API calls."""

    def test_multiple_teams(self, asc_advisor, asc_inactive_students, client):
        """Includes multiple team memberships."""
        response = client.post('/api/students', data=json.dumps({'groupCodes': ['MFB-DB', 'MFB-DL']}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert not _get_common_sids(asc_inactive_students, students)
        athletics = next(s['athleticsProfile']['athletics'] for s in students if s['uid'] == '98765')
        assert len(athletics) == 2
        group_codes = [a['groupCode'] for a in athletics]
        assert 'MFB-DB' in group_codes
        assert 'MFB-DL' in group_codes

    def test_get_intensive_cohort(self, asc_advisor, asc_inactive_students, client):
        """Returns the canned 'intensive' cohort, available to all authenticated users."""
        response = client.post('/api/students', data=json.dumps({'inIntensiveCohort': True}), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' in cohort
        students = cohort['students']
        inactive_intensive_sid = '890127492'
        assert inactive_intensive_sid not in [s['sid'] for s in students]
        assert len(_get_common_sids(asc_inactive_students, students)) == 0
        assert cohort['totalStudentCount'] == len(students) == 4
        assert 'teamGroups' not in cohort
        for student in students:
            assert student['athleticsProfile']['inIntensiveCohort']

    def test_unauthorized_request_for_athletic_study_center_data(self, client, fake_auth):
        """In order to access intensive_cohort, inactive status, etc. the user must be either ASC or Admin."""
        fake_auth.login('1022796')
        response = client.post('/api/students', data=json.dumps({'inIntensiveCohort': True}), content_type='application/json')
        assert response.status_code == 403

    def test_order_by_with_intensive_cohort(self, asc_advisor, client):
        """Returns students marked as 'intensive' by ASC."""
        all_expected_order = {
            'first_name': ['61889', '123456', '1049291', '242881'],
            'gpa': ['61889', '123456', '242881', '1049291'],
            'group_name': ['123456', '242881', '1049291', '61889'],
            'last_name': ['123456', '61889', '1049291', '242881'],
            'level': ['61889', '123456', '242881', '1049291'],
            'major': ['123456', '61889', '242881', '1049291'],
            'units': ['61889', '123456', '242881', '1049291'],
        }
        for order_by, expected_uid_list in all_expected_order.items():
            args = {
                'inIntensiveCohort': True,
                'orderBy': order_by,
            }
            response = client.post('/api/students', data=json.dumps(args), content_type='application/json')
            assert response.status_code == 200, f'Non-200 response where order_by={order_by}'
            cohort = json.loads(response.data)
            assert cohort['totalStudentCount'] == 4, f'Wrong count where order_by={order_by}'
            uid_list = [s['uid'] for s in cohort['students']]
            assert uid_list == expected_uid_list, f'Unmet expectation where order_by={order_by}'

    def test_forbidden_order_by(self, client, coe_advisor):
        """COE advisor cannot order results by ASC criteria."""
        data = {
            'ethnicities': ['B', 'H'],
            'orderBy': 'group_name',
        }
        response = client.post('/api/students', data=json.dumps(data), content_type='application/json')
        assert 403 == response.status_code

    def test_get_inactive_cohort(self, asc_advisor, client):
        response = client.post('/api/students', data=json.dumps({'isInactiveAsc': True}), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' in cohort
        assert cohort['totalStudentCount'] == len(cohort['students']) == 1
        assert 'teamGroups' not in cohort
        inactive_student = response.json['students'][0]
        assert not inactive_student['athleticsProfile']['isActiveAsc']
        assert inactive_student['athleticsProfile']['statusAsc'] == 'Trouble'


class TestSearch:
    """Student Search API."""

    sample_search = {
        'gpaRanges': ['numrange(3, 3.5, \'[)\')', 'numrange(3.5, 4, \'[]\')'],
        'groupCodes': ['MFB-DB', 'MFB-DL'],
        'levels': ['Junior', 'Senior'],
        'majors': [
            'Chemistry BS',
            'English BA',
            'Nuclear Engineering BS',
            'Letters & Sci Undeclared UG',
        ],
        'unitRanges': [],
        'inIntensiveCohort': None,
        'orderBy': 'last_name',
        'offset': 1,
        'limit': 50,
    }

    asc_search = json.dumps(sample_search)

    sample_search['groupCodes'] = []
    sample_search['gpaRanges'] = []
    sample_search['levels'] = []
    coe_search = json.dumps(sample_search)

    def test_search_not_authenticated(self, client):
        """Search is not available to the world."""
        response = client.post('/api/students/search')
        assert response.status_code == 401

    def test_unauthorized_request_for_athletic_study_center_data(self, client, fake_auth):
        """In order to access intensive_cohort, inactive status, etc. the user must be either ASC or Admin."""
        fake_auth.login('1022796')
        args = {'searchPhrase': 'John', 'isInactiveAsc': False}
        response = client.post('/api/students/search', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 403

    def test_search_with_missing_input(self, client, fake_auth):
        """Search is nothing without input."""
        fake_auth.login('2040')
        response = client.post('/api/students/search', data=json.dumps({'searchPhrase': ' \t  '}), content_type='application/json')
        assert response.status_code == 400

    def test_search_by_sid_snippet(self, client, fake_auth, asc_inactive_students):
        """Search by snippet of SID."""
        def _search_students_as_user(uid, sid_snippet):
            fake_auth.login(uid)
            response = client.post(
                '/api/students/search',
                data=json.dumps({'searchPhrase': sid_snippet}),
                content_type='application/json',
            )
            assert response.status_code == 200
            return response.json['students'], response.json['totalStudentCount']

        sid_snippet = '89012'
        # Admin user performs search
        students, total_student_count = _search_students_as_user('2040', sid_snippet)
        assert len(students) == total_student_count == 2
        assert _get_common_sids(asc_inactive_students, students)
        # ASC advisor performs the same search
        students, total_student_count = _search_students_as_user('1081940', sid_snippet)
        assert len(students) == total_student_count == 1
        assert not _get_common_sids(asc_inactive_students, students)

    def test_alerts_in_search_results(self, client, create_alerts, fake_auth):
        """Search results include alert counts."""
        fake_auth.login('2040')
        response = client.post('/api/students/search', data=json.dumps({'searchPhrase': 'davies'}), content_type='application/json')
        assert response.status_code == 200
        assert response.json['students'][0]['alertCount'] == 3

    def test_search_by_name_snippet(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        response = client.post('/api/students/search', data=json.dumps({'searchPhrase': 'dav'}), content_type='application/json')
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
                '/api/students/search',
                data=json.dumps({'searchPhrase': phrase}),
                content_type='application/json',
            )
            message_if_fail = f'Unexpected result(s) when search phrase={phrase}'
            assert response.status_code == 200, message_if_fail
            students = response.json['students']
            assert len(students) == response.json['totalStudentCount'] == 1, message_if_fail
            assert students[0]['lastName'] == 'Crossman', message_if_fail

    def test_search_by_name_asc_limited(self, asc_advisor, client):
        """An ASC name search finds ASC Pauls."""
        response = client.post('/api/students/search', data='{"searchPhrase": "paul"}', content_type='application/json')
        students = response.json['students']
        assert len(students) == 2
        assert next(s for s in students if s['name'] == 'Paul Kerschen')
        assert next(s for s in students if s['name'] == 'Paul Farestveit')

    def test_search_by_name_coe_limited(self, coe_advisor, client):
        """A COE name search finds COE Pauls."""
        response = client.post('/api/students/search', data='{"searchPhrase": "paul"}', content_type='application/json')
        students = response.json['students']
        assert len(students) == 2
        assert next(s for s in students if s['name'] == 'Paul Farestveit')
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli')

    def test_search_by_name_admin_unlimited(self, admin_login, client):
        """An admin name search finds all Pauls."""
        response = client.post('/api/students/search', data='{"searchPhrase": "paul"}', content_type='application/json')
        students = response.json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Paul Kerschen')
        assert next(s for s in students if s['name'] == 'Paul Farestveit')
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli')

    def test_search_order_by_offset_limit(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        args = {
            'searchPhrase': 'dav',
            'orderBy': 'major',
            'offset': 1,
            'limit': 1,
        }
        response = client.post('/api/students/search', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 200
        assert response.json['totalStudentCount'] == 3
        assert len(response.json['students']) == 1
        assert 'Crossman' == response.json['students'][0]['lastName']

    def test_get_students(self, asc_advisor, asc_inactive_students, client):
        response = client.post('/api/students', data=self.asc_search, content_type='application/json')
        assert response.status_code == 200
        assert 'students' in response.json
        students = response.json['students']
        assert 2 == len(students)
        assert not _get_common_sids(students, asc_inactive_students)
        # Offset of 1, ordered by lastName
        assert ['9933311', '242881'] == [student['uid'] for student in students]

    def test_get_students_includes_athletics_asc(self, asc_advisor, client):
        response = client.post('/api/students', data=self.asc_search, content_type='application/json')
        students = response.json['students']
        group_codes_1133399 = [a['groupCode'] for a in students[0]['athleticsProfile']['athletics']]
        assert len(group_codes_1133399) == 3
        assert 'MFB-DB' in group_codes_1133399
        assert 'MFB-DL' in group_codes_1133399
        assert 'MTE' in group_codes_1133399
        group_codes_242881 = [a['groupCode'] for a in students[1]['athleticsProfile']['athletics']]
        assert group_codes_242881 == ['MFB-DL']

    def test_coe_unauthorized_request_for_asc_data(self, coe_advisor, client):
        response = client.post('/api/students', data=self.coe_search, content_type='application/json')
        assert 403 == response.status_code

    def test_get_active_asc_students(self, asc_advisor, asc_inactive_students, client):
        """An ASC cohort search finds ASC sophomores."""
        args = {'levels': ['Sophomore']}
        response = client.post('/api/students', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert not _get_common_sids(students, asc_inactive_students)
        assert not len(students)

    def test_get_inactive_asc_students(self, asc_advisor, asc_inactive_students, client):
        """An ASC cohort search finds ASC sophomores."""
        args = {
            'levels': ['Sophomore'],
            'isInactiveAsc': True,
        }
        response = client.post('/api/students', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == 1
        assert len(_get_common_sids(students, asc_inactive_students)) == 1
        assert next(s for s in students if s['name'] == 'Siegfried Schlemiel')

    def test_get_students_coe_limited(self, coe_advisor, client):
        """A COE cohort search finds COE sophomores."""
        response = client.post('/api/students', data='{"levels": ["Sophomore"]}', content_type='application/json')
        students = response.json['students']
        assert len(students) == 2
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli')
        assert next(s for s in students if s['name'] == 'Nora Stanton Barney')

    def test_get_students_admin_unlimited(self, admin_login, client):
        """An admin cohort search finds all sophomores."""
        response = client.post('/api/students', data='{"levels": ["Sophomore"]}', content_type='application/json')
        students = response.json['students']
        assert len(students) == 3
        assert next(s for s in students if s['name'] == 'Siegfried Schlemiel')
        assert next(s for s in students if s['name'] == 'Wolfgang Pauli')
        assert next(s for s in students if s['name'] == 'Nora Stanton Barney')


class TestAthletics:
    """Athletics API."""

    def test_teams_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 401

    def test_team_groups_not_authorized(self, client, coe_advisor):
        """Returns 404 if not authorized."""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 404

    def test_get_all_team_groups(self, asc_advisor, client):
        """Returns all team-groups if authenticated."""
        response = client.get('/api/team_groups/all')
        assert response.status_code == 200
        team_groups = response.json
        group_codes = [team_group['groupCode'] for team_group in team_groups]
        group_names = [team_group['groupName'] for team_group in team_groups]
        assert ['MFB-DB', 'MFB-DL', 'MBB', 'MBB-AA', 'MTE', 'WFH', 'WTE'] == group_codes
        assert [
            'Football, Defensive Backs',
            'Football, Defensive Line',
            'Men\'s Baseball',
            'Men\'s Baseball (AA)',
            'Men\'s Tennis',
            'Women\'s Field Hockey',
            'Women\'s Tennis',
        ] == group_names
        total_student_counts = [team_group['totalStudentCount'] for team_group in team_groups]
        assert [3, 4, 1, 1, 2, 2, 2] == total_student_counts

    def test_team_with_athletes_in_multiple_groups(self, asc_advisor, client):
        """Returns a well-formed response on a valid code if authenticated."""
        response = client.get('/api/team_groups/all?orderBy=last_name')
        team_groups = list(filter(lambda t: t['teamCode'] == 'FBM', response.json))
        assert response.status_code == 200
        group_codes = [team_group['groupCode'] for team_group in team_groups]
        assert ['MFB-DB', 'MFB-DL'] == group_codes
        assert team_groups[0]['totalStudentCount'] == 3
        assert team_groups[1]['totalStudentCount'] == 4


@pytest.mark.usefixtures('db_session')
class TestStudentAnalytics:
    """Student Analytics API."""

    api_path = '/api/student/{}/analytics'
    coe_student = api_path.format(1049291)
    dave = api_path.format(98765)
    deborah = api_path.format(61889)
    non_student_uid = '2040'
    non_student = api_path.format(non_student_uid)
    unknown_uid = 9999999
    unknown = api_path.format(unknown_uid)

    @pytest.fixture()
    def coe_advisor(self, fake_auth):
        fake_auth.login('1133399')

    @pytest.fixture()
    def authenticated_response(self, coe_advisor, client):
        response = client.get(TestStudentAnalytics.deborah)
        assert response.status_code == 200
        return response

    @pytest.fixture()
    def asc_advisor(self, fake_auth):
        fake_auth.login('1081940')

    @pytest.fixture()
    def asc_authenticated_response(self, asc_advisor, client):
        response = client.get(TestStudentAnalytics.deborah)
        assert response.status_code == 200
        return response

    @pytest.fixture()
    def coe_authenticated_response(self, coe_advisor, client):
        response = client.get(TestStudentAnalytics.coe_student)
        assert response.status_code == 200
        return response

    @pytest.fixture()
    def admin_auth(self, fake_auth):
        fake_auth.login('2040')

    @pytest.fixture()
    def admin_authenticated_response(self, admin_auth, client):
        response = client.get(TestStudentAnalytics.deborah)
        assert response.status_code == 200
        return response

    @staticmethod
    def get_course_for_code(response, term_id, code):
        term = next((term for term in response.json['enrollmentTerms'] if term['termId'] == term_id), None)
        if term:
            return next((course for course in term['enrollments'] if course['displayName'] == code), None)

    def test_user_analytics_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        response = client.get(TestStudentAnalytics.deborah)
        assert response.status_code == 401

    def test_user_with_no_enrollments_in_current_term(self, asc_advisor, client):
        """Identifies user with no enrollments in current term."""
        response = client.get(TestStudentAnalytics.dave)
        assert response.status_code == 200
        enrollment_terms = response.json['enrollmentTerms']
        assert len(enrollment_terms) == 1
        assert enrollment_terms[0]['termName'] == 'Spring 2017'
        assert response.json['hasCurrentTermEnrollments'] is False

    def test_user_analytics_authenticated(self, authenticated_response):
        """Returns a well-formed response if authenticated."""
        assert authenticated_response.status_code == 200
        assert authenticated_response.json['uid'] == '61889'
        assert authenticated_response.json['canvasUserId'] == '9000100'
        assert authenticated_response.json['hasCurrentTermEnrollments'] is True
        assert len(authenticated_response.json['enrollmentTerms']) > 0
        for term in authenticated_response.json['enrollmentTerms']:
            assert len(term['enrollments']) > 0
            for course in term['enrollments']:
                for canvasSite in course['canvasSites']:
                    assert canvasSite['canvasCourseId']
                    assert canvasSite['courseCode']
                    assert canvasSite['courseTerm']
                    assert canvasSite['courseCode']
                    assert canvasSite['analytics']

    def test_user_analytics_multiple_terms(self, authenticated_response):
        """Returns all terms with enrollment data in reverse order."""
        assert len(authenticated_response.json['enrollmentTerms']) == 2
        assert authenticated_response.json['enrollmentTerms'][0]['termName'] == 'Fall 2017'
        assert authenticated_response.json['enrollmentTerms'][0]['enrolledUnits'] == 12.5
        assert len(authenticated_response.json['enrollmentTerms'][0]['enrollments']) == 4
        assert authenticated_response.json['enrollmentTerms'][1]['termName'] == 'Spring 2017'
        assert authenticated_response.json['enrollmentTerms'][1]['enrolledUnits'] == 10
        assert len(authenticated_response.json['enrollmentTerms'][1]['enrollments']) == 3

    def test_user_analytics_earliest_term_cutoff(self, authenticated_response):
        """Ignores terms before the configured earliest term."""
        for term in authenticated_response.json['enrollmentTerms']:
            assert term['termName'] != 'Spring 2016'

    def test_user_analytics_current_term_cutoff(self, authenticated_response):
        """Ignores terms after the configured current term."""
        for term in authenticated_response.json['enrollmentTerms']:
            assert term['termName'] != 'Spring 2018'

    def test_enrollment_without_course_site(self, authenticated_response):
        """Returns enrollments with no associated course sites."""
        enrollment_without_site = TestStudentAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert enrollment_without_site['title'] == 'Private Carillon Lessons for Advanced Students'
        assert enrollment_without_site['canvasSites'] == []

    def test_enrollment_with_multiple_course_sites(self, authenticated_response):
        """Returns multiple course sites associated with an enrollment, sorted by site id."""
        enrollment_with_multiple_sites = TestStudentAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        canvas_sites = enrollment_with_multiple_sites['canvasSites']
        assert len(canvas_sites) == 2
        assert canvas_sites[0]['courseName'] == 'Radioactive Waste Management'
        assert canvas_sites[1]['courseName'] == 'Optional Friday Night Radioactivity Group'

    def test_multiple_primary_section_enrollments(self, authenticated_response):
        """Disambiguates multiple primary sections under a single course display name."""
        classics_first = TestStudentAnalytics.get_course_for_code(authenticated_response, '2172', 'CLASSIC 130 LEC 001')
        classics_second = TestStudentAnalytics.get_course_for_code(authenticated_response, '2172', 'CLASSIC 130 LEC 002')
        assert len(classics_first['sections']) == 1
        assert classics_first['sections'][0]['units'] == 4
        assert classics_first['sections'][0]['gradingBasis'] == 'P/NP'
        assert classics_first['sections'][0]['grade'] == 'P'
        assert classics_first['units'] == 4
        assert classics_first['gradingBasis'] == 'P/NP'
        assert classics_first['grade'] == 'P'

        assert len(classics_second['sections']) == 1
        assert classics_second['sections'][0]['units'] == 4
        assert classics_second['sections'][0]['gradingBasis'] == 'Letter'
        assert classics_second['sections'][0]['grade'] == 'B-'
        assert classics_second['units'] == 4
        assert classics_second['gradingBasis'] == 'Letter'
        assert classics_second['grade'] == 'B-'

    def test_enrollments_sorted(self, authenticated_response):
        """Sorts enrollments by course display name."""
        spring_2017_enrollments = authenticated_response.json['enrollmentTerms'][1]['enrollments']
        assert(spring_2017_enrollments[0]['displayName'] == 'CLASSIC 130 LEC 001')
        assert(spring_2017_enrollments[1]['displayName'] == 'CLASSIC 130 LEC 002')
        assert(spring_2017_enrollments[2]['displayName'] == 'MUSIC 41C')

    def test_course_site_without_enrollment(self, authenticated_response):
        """Returns course sites with no associated enrollments."""
        assert len(authenticated_response.json['enrollmentTerms'][0]['unmatchedCanvasSites']) == 0
        assert len(authenticated_response.json['enrollmentTerms'][1]['unmatchedCanvasSites']) == 1
        unmatched_site = authenticated_response.json['enrollmentTerms'][1]['unmatchedCanvasSites'][0]
        assert unmatched_site['courseCode'] == 'STAT 154'
        assert unmatched_site['courseName'] == 'Modern Statistical Prediction and Machine Learning'
        assert unmatched_site['analytics']

    def test_course_site_without_membership(self, authenticated_response):
        """Returns a graceful error if the expected membership is not found in the course site."""
        course_without_membership = TestStudentAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        for metric in ['assignmentsSubmitted', 'currentScore', 'lastActivity']:
            assert course_without_membership['canvasSites'][0]['analytics'][metric]['error']

    def test_course_site_with_enrollment(self, authenticated_response):
        """Returns sensible data if the expected enrollment is found in the course site."""
        course_with_enrollment = TestStudentAnalytics.get_course_for_code(authenticated_response, '2178', 'MED ST 205')
        analytics = course_with_enrollment['canvasSites'][0]['analytics']

        assert analytics['assignmentsSubmitted']['student']['raw'] == 8
        assert analytics['assignmentsSubmitted']['student']['percentile'] == 64
        assert analytics['assignmentsSubmitted']['courseDeciles'][0] == 0
        assert analytics['assignmentsSubmitted']['courseDeciles'][9] == 10
        assert analytics['assignmentsSubmitted']['courseDeciles'][10] == 17

        assert analytics['currentScore']['student']['raw'] == 84

        assert analytics['lastActivity']['boxPlottable'] is True
        assert analytics['lastActivity']['student']['raw'] == 1535275620
        assert analytics['lastActivity']['student']['percentile'] == 93
        assert analytics['lastActivity']['displayPercentile'] == '90th'

    def test_student_not_found(self, coe_advisor, client):
        """Returns 404 if no viewable student."""
        response = client.get(TestStudentAnalytics.unknown)
        assert response.status_code == 404
        assert response.json['message'] == 'Unknown student'

    def test_user_analytics_not_department_authorized(self, coe_advisor, client):
        """Returns 404 if attempting to view a user outside one's own department."""
        response = client.get(TestStudentAnalytics.dave)
        assert response.status_code == 404

    def test_sis_enrollment_merge(self, authenticated_response):
        """Merges sorted SIS enrollment data."""
        burmese = TestStudentAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        assert burmese['displayName'] == 'BURMESE 1A'
        assert burmese['title'] == 'Introductory Burmese'
        assert len(burmese['sections']) == 1
        assert burmese['sections'][0]['ccn'] == 90100
        assert burmese['sections'][0]['sectionNumber'] == '001'
        assert burmese['sections'][0]['enrollmentStatus'] == 'E'
        assert burmese['sections'][0]['units'] == 4
        assert burmese['sections'][0]['gradingBasis'] == 'Letter'
        assert burmese['sections'][0]['midtermGrade'] == 'D+'
        assert burmese['sections'][0]['primary'] is True
        assert not burmese['sections'][0]['grade']
        assert burmese['units'] == 4
        assert burmese['gradingBasis'] == 'Letter'
        assert burmese['midtermGrade'] == 'D+'
        assert not burmese['grade']

        medieval = TestStudentAnalytics.get_course_for_code(authenticated_response, '2178', 'MED ST 205')
        assert medieval['displayName'] == 'MED ST 205'
        assert medieval['title'] == 'Medieval Manuscripts as Primary Sources'
        assert len(medieval['sections']) == 1
        assert medieval['sections'][0]['ccn'] == 90200
        assert medieval['sections'][0]['sectionNumber'] == '001'
        assert medieval['sections'][0]['enrollmentStatus'] == 'E'
        assert medieval['sections'][0]['units'] == 5
        assert medieval['sections'][0]['gradingBasis'] == 'Letter'
        assert medieval['sections'][0]['primary'] is True
        assert not medieval['sections'][0]['grade']

        nuclear = TestStudentAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert nuclear['displayName'] == 'NUC ENG 124'
        assert nuclear['title'] == 'Radioactive Waste Management'
        assert len(nuclear['sections']) == 2
        assert nuclear['sections'][0]['ccn'] == 90300
        assert nuclear['sections'][0]['sectionNumber'] == '002'
        assert nuclear['sections'][0]['enrollmentStatus'] == 'E'
        assert nuclear['sections'][0]['units'] == 3
        assert nuclear['sections'][0]['gradingBasis'] == 'P/NP'
        assert nuclear['sections'][0]['grade'] == 'P'
        assert nuclear['sections'][0]['primary'] is True
        assert nuclear['sections'][1]['ccn'] == 90301
        assert nuclear['sections'][1]['sectionNumber'] == '201'
        assert nuclear['sections'][1]['enrollmentStatus'] == 'E'
        assert nuclear['sections'][1]['units'] == 0
        assert nuclear['sections'][1]['gradingBasis'] == 'NON'
        assert nuclear['sections'][1]['primary'] is False
        assert not nuclear['sections'][1]['grade']

        music = TestStudentAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert music['displayName'] == 'MUSIC 41C'
        assert music['title'] == 'Private Carillon Lessons for Advanced Students'
        assert len(music['sections']) == 1
        assert music['sections'][0]['ccn'] == 80100
        assert music['sections'][0]['sectionNumber'] == '001'
        assert music['sections'][0]['enrollmentStatus'] == 'E'
        assert music['sections'][0]['units'] == 2
        assert music['sections'][0]['gradingBasis'] == 'Letter'
        assert music['sections'][0]['grade'] == 'A-'
        assert music['sections'][0]['primary'] is True
        assert music['units'] == 2
        assert music['gradingBasis'] == 'Letter'
        assert music['grade'] == 'A-'

    def test_dropped_sections(self, authenticated_response):
        """Collects dropped sections in a separate feed."""
        dropped_sections = authenticated_response.json['enrollmentTerms'][0]['droppedSections']
        assert len(dropped_sections) == 1
        assert dropped_sections[0]['displayName'] == 'MUSIC 41C'
        assert dropped_sections[0]['component'] == 'TUT'
        assert dropped_sections[0]['sectionNumber'] == '002'

    def test_sis_profile(self, authenticated_response):
        """Provides SIS profile data."""
        sis_profile = authenticated_response.json['sisProfile']
        assert sis_profile['academicCareer'] == 'UGRD'
        assert sis_profile['cumulativeGPA'] == 3.8
        assert sis_profile['cumulativeUnits'] == 101.3
        assert sis_profile['degreeProgress']['requirements']['americanCultures']['status'] == 'In Progress'
        assert sis_profile['degreeProgress']['requirements']['americanHistory']['status'] == 'Not Satisfied'
        assert sis_profile['degreeProgress']['requirements']['americanInstitutions']['status'] == 'Not Satisfied'
        assert sis_profile['degreeProgress']['requirements']['entryLevelWriting']['status'] == 'Satisfied'
        assert sis_profile['emailAddress'] == 'oski@berkeley.edu'
        assert sis_profile['level']['code'] == '30'
        assert sis_profile['level']['description'] == 'Junior'
        assert sis_profile['phoneNumber'] == '415/123-4567'
        assert len(sis_profile['plans']) == 2
        assert sis_profile['plans'][0]['description'] == 'English BA'
        assert sis_profile['plans'][0]['program'] == 'Undergrad Letters & Science'
        assert sis_profile['plans'][0]['degreeProgramUrl'] == 'http://guide.berkeley.edu/undergraduate/degree-programs/english/'
        assert sis_profile['plans'][1]['description'] == 'Nuclear Engineering BS'
        assert sis_profile['plans'][1]['program'] == 'Engineering'
        assert sis_profile['plans'][1]['degreeProgramUrl'] == 'http://guide.berkeley.edu/undergraduate/degree-programs/nuclear-engineering/'
        assert sis_profile['preferredName'] == 'Osk Bear'
        assert sis_profile['primaryName'] == 'Oski Bear'
        assert sis_profile['termsInAttendance'] == 5

    def test_sis_profile_expected_graduation_term(self, authenticated_response):
        """Provides the last of any expected graduation terms listed in SIS profile."""
        sis_profile = authenticated_response.json['sisProfile']
        assert sis_profile['expectedGraduationTerm']['id'] == '2198'
        assert sis_profile['expectedGraduationTerm']['name'] == 'Fall 2019'

    def test_student_overview_link(self, authenticated_response):
        """Provides a link to official data about the student."""
        assert authenticated_response.json['studentProfileLink']

    def test_athletics_profile_non_asc(self, authenticated_response):
        """Does not include athletics profile for non-ASC users."""
        assert 'athleticsProfile' not in authenticated_response.json

    def test_athletics_profile_asc(self, asc_authenticated_response):
        """Includes athletics profile for ASC users."""
        response = asc_authenticated_response.json
        assert 'coeProfile' not in response
        athletics_profile = response['athleticsProfile']
        assert athletics_profile['inIntensiveCohort'] is True
        assert len(athletics_profile['athletics']) == 2
        hockey = next(a for a in athletics_profile['athletics'] if a['groupCode'] == 'WFH')
        assert hockey['groupName'] == 'Women\'s Field Hockey'
        assert hockey['teamCode'] == 'FHW'
        assert hockey['teamName'] == 'Women\'s Field Hockey'
        tennis = next(a for a in athletics_profile['athletics'] if a['groupCode'] == 'WTE')
        assert tennis['groupName'] == 'Women\'s Tennis'
        assert tennis['teamCode'] == 'TNW'
        assert tennis['teamName'] == 'Women\'s Tennis'

    def test_college_of_engineering_profile(self, coe_advisor, coe_authenticated_response):
        """Includes COE profile (eg, PREP) for COE students."""
        response = coe_authenticated_response.json
        assert 'athleticsProfile' not in response
        assert 'coeProfile' in response
        coe_profile = response['coeProfile']
        assert coe_profile == {
            'advisorUid': '1133399',
            'gender': 'w',
            'ethnicity': 'B',
            'minority': True,
            'didPrep': False,
            'prepEligible': True,
            'didTprep': False,
            'tprepEligible': False,
        }

    def test_athletics_profile_admin(self, admin_authenticated_response):
        """Includes athletics profile for admins."""
        athletics_profile = admin_authenticated_response.json['athleticsProfile']
        assert athletics_profile['inIntensiveCohort'] is True
        assert len(athletics_profile['athletics']) == 2


class TestStudentPhoto:
    """User Photo API."""

    def test_photo_not_authenticated(self, client):
        """Requires authentication."""
        response = client.get('/api/student/61889/photo')
        assert response.status_code == 401

    def test_photo_authenticated(self, client, fake_auth):
        """Returns a photo when authenticated."""
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/student/61889/photo')
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'image/jpeg'
        assert response.headers.get('Content-Length') == '3559'

    def test_photo_not_found(self, client, fake_auth):
        """Returns an empty response when photo not found."""
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/student/242881/photo')
        assert response.status_code == 204
        assert response.headers.get('Content-Length') == '0'


def _get_common_sids(student_list_1, student_list_2):
    sid_list_1 = [s['sid'] for s in student_list_1]
    sid_list_2 = [s['sid'] for s in student_list_2]
    return list(set(sid_list_1) & set(sid_list_2))
