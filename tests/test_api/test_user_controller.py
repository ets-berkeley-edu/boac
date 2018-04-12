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


from boac.externals import sis_enrollments_api, sis_student_api
from boac.lib.mockingbird import MockResponse, register_mock
import pytest
import simplejson as json


class TestStudents:
    """Students API."""

    def test_all_students(self, client):
        """Returns a list of students."""
        response = client.get('/api/students/all')
        assert response.status_code == 200
        # We have one student not on a team
        assert len(response.json) == 6

    def test_multiple_teams(self, client):
        """Includes multiple team memberships."""
        response = client.get('/api/students/all')
        assert response.status_code == 200
        athletics = next(user['athletics'] for user in response.json if user['uid'] == '98765')
        assert len(athletics) == 2
        group_codes = [a['groupCode'] for a in athletics]
        assert 'MFB-DB' in group_codes
        assert 'MFB-DL' in group_codes


class TestUserProfile:
    """User Profile API."""

    def test_profile_not_authenticated(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/profile')
        assert response.status_code == 200
        assert not response.json['uid']

    def test_profile_auto_create_primary_group(self, client, fake_auth):
        uid = '6446'
        fake_auth.login(uid)
        response = client.get('/api/profile')
        assert response.status_code == 200
        profile = response.json
        assert profile['uid'] == uid
        assert 'firstName' in profile
        assert 'lastName' in profile
        assert profile['myPrimaryGroup']

    def test_includes_canvas_profile_if_available(self, client, fake_auth):
        test_uid = '2040'
        fake_auth.login(test_uid)
        response = client.get('/api/profile')
        assert response.json['uid'] == test_uid
        assert 'firstName' in response.json
        assert 'lastName' in response.json


class TestUserPhoto:
    """User Photo API."""

    def test_photo_not_authenticated(self, client):
        """Requires authentication."""
        response = client.get('/api/user/61889/photo')
        assert response.status_code == 401

    def test_photo_authenticated(self, client, fake_auth):
        """Returns a photo when authenticated."""
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/user/61889/photo')
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'image/jpeg'
        assert response.headers.get('Content-Length') == '3559'

    def test_photo_not_found(self, client, fake_auth):
        """Returns 404 when photo not found."""
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/user/242881/photo')
        assert response.status_code == 404
        assert response.json['message'] == 'No photo was found for the requested id.'

    def test_student_not_found(self, client, fake_auth):
        """Returns 404 when student not found."""
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/user/99999999/photo')
        assert response.status_code == 404
        assert response.json['message'] == 'No student was found for the requested id.'


@pytest.mark.usefixtures('db_session')
class TestUserAnalytics:
    """User Analytics API."""

    api_path = '/api/user/{}/analytics'
    field_hockey_star = api_path.format(61889)
    non_student_uid = '2040'
    non_student = api_path.format(non_student_uid)
    unknown_uid = 9999999
    unknown = api_path.format(unknown_uid)

    @pytest.fixture()
    def authenticated_session(self, fake_auth):
        test_uid = '1133399'
        fake_auth.login(test_uid)

    @pytest.fixture()
    def authenticated_response(self, authenticated_session, client):
        return client.get(TestUserAnalytics.field_hockey_star)

    @staticmethod
    def get_course_for_code(response, term_id, code):
        term = next((term for term in response.json['enrollmentTerms'] if term['termId'] == term_id), None)
        if term:
            return next((course for course in term['enrollments'] if course['displayName'] == code), None)

    def test_user_analytics_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        response = client.get(TestUserAnalytics.field_hockey_star)
        assert response.status_code == 401

    def test_user_analytics_authenticated(self, authenticated_response):
        """Returns a well-formed response if authenticated."""
        assert authenticated_response.status_code == 200
        assert authenticated_response.json['uid'] == '61889'
        assert authenticated_response.json['canvasProfile']['id'] == 9000100
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
        assert len(authenticated_response.json['enrollmentTerms'][0]['enrollments']) == 3
        assert authenticated_response.json['enrollmentTerms'][1]['termName'] == 'Spring 2017'
        assert authenticated_response.json['enrollmentTerms'][1]['enrolledUnits'] == 10
        assert len(authenticated_response.json['enrollmentTerms'][1]['enrollments']) == 3

    def test_user_analytics_term_cutoff(self, authenticated_response):
        """Ignores terms before the configured cutoff."""
        for term in authenticated_response.json['enrollmentTerms']:
            assert term['termName'] != 'Spring 2016'

    def test_enrollment_without_course_site(self, authenticated_response):
        """Returns enrollments with no associated course sites."""
        enrollment_without_site = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert enrollment_without_site['title'] == 'Private Carillon Lessons for Advanced Students'
        assert enrollment_without_site['canvasSites'] == []

    def test_enrollment_with_multiple_course_sites(self, authenticated_response):
        """Returns multiple course sites associated with an enrollment, sorted by site id."""
        enrollment_with_multiple_sites = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert len(enrollment_with_multiple_sites['canvasSites']) == 2
        assert enrollment_with_multiple_sites['canvasSites'][0]['courseName'] == 'Radioactive Waste Management'
        assert enrollment_with_multiple_sites['canvasSites'][1]['courseName'] == 'Optional Friday Night Radioactivity Group'

    def test_multiple_primary_section_enrollments(self, authenticated_response):
        """Disambiguates multiple primary sections under a single course display name."""
        classics_first = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'CLASSIC 130 LEC 001')
        classics_second = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'CLASSIC 130 LEC 002')
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

    def test_athletic_enrollments_removed(self, authenticated_response):
        """Removes athletic enrollments."""
        for enrollment in authenticated_response.json['enrollmentTerms'][0]['enrollments']:
            assert enrollment['displayName'] != 'PHYSED 11'

    def test_past_term_dropped_enrollments_removed(self, authenticated_response):
        """Removes dropped enrollments from past terms."""
        for enrollment in authenticated_response.json['enrollmentTerms'][1]['enrollments']:
            print(enrollment)
            for section in enrollment['sections']:
                assert section['enrollmentStatus'] != 'D'

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
        course_without_membership = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        assert course_without_membership['canvasSites'][0]['analytics']['error'] == 'Unable to retrieve analytics'

    def test_course_site_with_enrollment(self, authenticated_response):
        """Returns sensible data if the expected enrollment is found in the course site."""
        course_with_enrollment = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'MED ST 205')
        analytics = course_with_enrollment['canvasSites'][0]['analytics']

        assert analytics['assignmentsOnTime']['student']['raw'] == 5
        assert analytics['assignmentsOnTime']['student']['percentile'] == 93
        assert analytics['assignmentsOnTime']['courseDeciles'][0] == 0
        assert analytics['assignmentsOnTime']['courseDeciles'][9] == 5
        assert analytics['assignmentsOnTime']['courseDeciles'][10] == 6

        assert analytics['courseCurrentScore']['student']['raw'] == 84

        assert analytics['pageViews']['student']['raw'] == 768
        assert analytics['pageViews']['student']['percentile'] == 54
        assert analytics['pageViews']['courseDeciles'][0] == 9
        assert analytics['pageViews']['courseDeciles'][9] == 917
        assert analytics['pageViews']['courseDeciles'][10] == 31983

        assert analytics['participations']['student']['raw'] == 5
        assert analytics['participations']['student']['percentile'] == 83
        assert analytics['participations']['courseDeciles'][0] == 0
        assert analytics['participations']['courseDeciles'][9] == 6
        assert analytics['participations']['courseDeciles'][10] == 12

        assert analytics['loch']['assignmentsOnTime']['student']['raw'] == 7
        assert analytics['loch']['assignmentsSubmitted']['student']['raw'] == 8
        assert analytics['loch']['pageViews']['student']['raw'] == 766

    def test_empty_canvas_course_feed(self, client, fake_auth):
        """Returns 200 if user is found and Canvas course feed is empty."""
        fake_auth.login(TestUserAnalytics.non_student_uid)
        response = client.get(TestUserAnalytics.non_student)
        assert response.status_code == 200
        assert response.json['uid'] == TestUserAnalytics.non_student_uid
        assert not response.json['sid']
        assert not response.json['enrollmentTerms']

    def test_canvas_profile_not_found(self, authenticated_session, client):
        """Returns 404 if Canvas profile not found."""
        response = client.get(TestUserAnalytics.unknown)
        assert response.status_code == 404
        assert response.json['message'] == 'No Canvas profile found for user'

    def test_relevant_majors(self, authenticated_session, client):
        """Returns list of majors relevant to our student population."""
        response = client.get('/api/majors/relevant')
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_sis_enrollment_merge(self, authenticated_response):
        """Merges sorted SIS enrollment data."""
        burmese = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        assert burmese['displayName'] == 'BURMESE 1A'
        assert burmese['title'] == 'Introductory Burmese'
        assert len(burmese['sections']) == 1
        assert burmese['sections'][0]['ccn'] == 90100
        assert burmese['sections'][0]['sectionNumber'] == '001'
        assert burmese['sections'][0]['enrollmentStatus'] == 'E'
        assert burmese['sections'][0]['units'] == 4
        assert burmese['sections'][0]['gradingBasis'] == 'Letter'
        assert burmese['sections'][0]['midtermGrade'] == 'D+'
        assert not burmese['sections'][0]['grade']
        assert burmese['units'] == 4
        assert burmese['gradingBasis'] == 'Letter'
        assert burmese['midtermGrade'] == 'D+'
        assert not burmese['grade']

        medieval = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'MED ST 205')
        assert medieval['displayName'] == 'MED ST 205'
        assert medieval['title'] == 'Medieval Manuscripts as Primary Sources'
        assert len(medieval['sections']) == 1
        assert medieval['sections'][0]['ccn'] == 90200
        assert medieval['sections'][0]['sectionNumber'] == '001'
        assert medieval['sections'][0]['enrollmentStatus'] == 'E'
        assert medieval['sections'][0]['units'] == 5
        assert medieval['sections'][0]['gradingBasis'] == 'Letter'
        assert not medieval['sections'][0]['grade']

        nuclear = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert nuclear['displayName'] == 'NUC ENG 124'
        assert nuclear['title'] == 'Radioactive Waste Management'
        assert len(nuclear['sections']) == 2
        assert nuclear['sections'][0]['ccn'] == 90300
        assert nuclear['sections'][0]['sectionNumber'] == '002'
        assert nuclear['sections'][0]['enrollmentStatus'] == 'E'
        assert nuclear['sections'][0]['units'] == 3
        assert nuclear['sections'][0]['gradingBasis'] == 'P/NP'
        assert nuclear['sections'][0]['grade'] == 'P'
        assert nuclear['sections'][1]['ccn'] == 90301
        assert nuclear['sections'][1]['sectionNumber'] == '201'
        assert nuclear['sections'][1]['enrollmentStatus'] == 'E'
        assert nuclear['sections'][1]['units'] == 0
        assert nuclear['sections'][1]['gradingBasis'] == 'NON'
        assert not nuclear['sections'][1]['grade']

        music = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert music['displayName'] == 'MUSIC 41C'
        assert music['title'] == 'Private Carillon Lessons for Advanced Students'
        assert len(music['sections']) == 1
        assert music['sections'][0]['ccn'] == 80100
        assert music['sections'][0]['sectionNumber'] == '001'
        assert music['sections'][0]['enrollmentStatus'] == 'E'
        assert music['sections'][0]['units'] == 2
        assert music['sections'][0]['gradingBasis'] == 'Letter'
        assert music['sections'][0]['grade'] == 'A-'
        assert music['units'] == 2
        assert music['gradingBasis'] == 'Letter'
        assert music['grade'] == 'A-'

    def test_dropped_sections(self, authenticated_response):
        """Collects dropped sections in a separate feed."""
        dropped_sections = authenticated_response.json['enrollmentTerms'][0]['droppedSections']
        assert len(dropped_sections) == 1
        assert dropped_sections[0]['displayName'] == 'NUC ENG 124'
        assert dropped_sections[0]['component'] == 'DIS'
        assert dropped_sections[0]['sectionNumber'] == '200'

    def test_sis_enrollment_not_found(self, authenticated_session, client):
        """Gracefully handles missing SIS enrollments."""
        sis_error = MockResponse(200, {}, '{"apiResponse": {"response": {"message": "Something unexpected."}}}')
        with register_mock(sis_enrollments_api._get_enrollments, sis_error):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 200
            assert len(response.json['enrollmentTerms']) > 0
            for term in response.json['enrollmentTerms']:
                assert term['enrollments'] == []

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
        assert sis_profile['plans'][1]['description'] == 'Astrophysics BS'
        assert sis_profile['plans'][1]['program'] == 'Undergrad Letters & Science'
        assert sis_profile['plans'][1]['degreeProgramUrl'] == 'http://guide.berkeley.edu/undergraduate/degree-programs/astrophysics/'
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

    def test_athletics_profile(self, authenticated_response):
        """Includes athletics profile."""
        athletics_profile = authenticated_response.json['athleticsProfile']
        assert athletics_profile['name'] == 'Brigitte Lin'
        assert athletics_profile['uid'] == '61889'
        assert athletics_profile['sid'] == '11667051'
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

    def test_sis_profile_unexpected_payload(self, authenticated_session, client):
        """Gracefully handles unexpected SIS profile data."""
        sis_response = MockResponse(200, {}, '{"apiResponse": {"response": {"message": "Something wicked."}}}')
        with register_mock(sis_student_api._get_student, sis_response):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 200
            assert response.json['canvasProfile']
            assert not response.json['sisProfile']

    def test_sis_profile_error(self, authenticated_session, client):
        """Gracefully handles SIS profile error."""
        sis_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(sis_student_api._get_student, sis_error):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 200
            assert response.json['canvasProfile']
            assert not response.json['sisProfile']

    def test_get_students(self, authenticated_session, client):
        data = {
            'gpaRanges': ['numrange(3, 3.5, \'[)\')', 'numrange(3.5, 4, \'[]\')'],
            'groupCodes': ['MFB-DB', 'MFB-DL'],
            'levels': ['Junior', 'Senior'],
            'majors': ['English BA', 'History BA', 'Letters & Sci Undeclared UG', 'Gender and Women\'s Studies'],
            'unitRanges': [],
            'inIntensiveCohort': None,
            'orderBy': 'last_name',
            'offset': 1,
            'limit': 50,
        }
        response = client.post('/api/students', data=json.dumps(data), content_type='application/json')

        assert response.status_code == 200
        assert 'members' in response.json
        students = response.json['members']
        assert 2 == len(students)
        # Offset of 1, ordered by lastName
        assert ['1133399', '242881'] == [student['uid'] for student in students]
        group_codes_1133399 = [a['groupCode'] for a in students[0]['athletics']]
        assert len(group_codes_1133399) == 3
        assert 'MFB-DB' in group_codes_1133399
        assert 'MFB-DL' in group_codes_1133399
        assert 'MTE' in group_codes_1133399
        group_codes_242881 = [a['groupCode'] for a in students[1]['athletics']]
        assert group_codes_242881 == ['MFB-DL']

    def test_get_intensive_cohort(self, authenticated_session, client):
        """Returns the canned 'intensive' cohort, available to all authenticated users."""
        response = client.post('/api/students', data=json.dumps({'inIntensiveCohort': True}), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'members' in cohort
        assert cohort['totalMemberCount'] == len(cohort['members']) == 4
        assert 'teamGroups' not in cohort
        for student in cohort['members']:
            assert student['inIntensiveCohort']
            assert student['isActiveAsc']

    def test_order_by_with_intensive_cohort(self, authenticated_session, client):
        """Returns the canned 'intensive' cohort, available to all authenticated users."""
        all_expected_order = {
            'first_name': ['61889', '1022796', '1049291', '242881'],
            'gpa': ['1022796', '242881', '1049291', '61889'],
            'group_name': ['242881', '1049291', '61889', '1022796'],
            'last_name': ['1022796', '1049291', '242881', '61889'],
            'level': ['1022796', '242881', '1049291', '61889'],
            'major': ['1022796', '61889', '242881', '1049291'],
            'units': ['61889', '1022796', '242881', '1049291'],
        }
        for order_by, expected_uid_list in all_expected_order.items():
            args = {
                'inIntensiveCohort': True,
                'orderBy': order_by,
            }
            response = client.post('/api/students', data=json.dumps(args), content_type='application/json')
            assert response.status_code == 200, f'Non-200 response where order_by={order_by}'
            cohort = json.loads(response.data)
            assert cohort['totalMemberCount'] == 4, f'Wrong count where order_by={order_by}'
            uid_list = [s['uid'] for s in cohort['members']]
            assert uid_list == expected_uid_list, f'Unmet expectation where order_by={order_by}'

    def test_get_inactive_cohort(self, authenticated_session, client):
        response = client.post('/api/students', data=json.dumps({'isInactive': True}), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'members' in cohort
        assert cohort['totalMemberCount'] == len(cohort['members']) == 1
        assert 'teamGroups' not in cohort
        inactive_student = response.json['members'][0]
        assert not inactive_student['isActiveAsc']
        assert inactive_student['statusAsc'] == 'Trouble'
