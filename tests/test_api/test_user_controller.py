from boac.externals import sis_enrollments_api, sis_student_api
from boac.lib.mockingbird import MockResponse, register_mock
import pytest


class TestUser:
    """User API"""

    def test_profile_not_authenticated(self, client):
        """returns a well-formed response"""
        response = client.get('/api/profile')
        assert response.status_code == 200
        assert not response.json['uid']

    def test_all_users(self, client):
        """returns a list of users, including team"""
        response = client.get('/api/students/all')
        assert response.status_code == 200
        # We have one student not on a team
        assert len(response.json) == 5

    def test_profile_includes_lack_of_canvas_account(self, client, fake_auth):
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/profile')
        assert response.status_code == 200
        assert response.json['uid'] == test_uid
        assert response.json['canvasProfile'] is False

    def test_includes_canvas_profile_if_available(self, client, fake_auth):
        test_uid = '2040'
        fake_auth.login(test_uid)
        response = client.get('/api/profile')
        assert response.json['canvasProfile']['sis_login_id'] == test_uid


@pytest.mark.usefixtures('db_session')
class TestUserAnalytics:
    """User Analytics API"""
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
        """returns 401 if not authenticated"""
        response = client.get(TestUserAnalytics.field_hockey_star)
        assert response.status_code == 401

    def test_user_analytics_authenticated(self, authenticated_response):
        """returns a well-formed response if authenticated"""
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
        """returns all terms with enrollment data in reverse order"""
        assert len(authenticated_response.json['enrollmentTerms']) == 2
        assert authenticated_response.json['enrollmentTerms'][0]['termName'] == 'Fall 2017'
        assert authenticated_response.json['enrollmentTerms'][0]['enrolledUnits'] == 12.5
        assert len(authenticated_response.json['enrollmentTerms'][0]['enrollments']) == 3
        assert authenticated_response.json['enrollmentTerms'][1]['termName'] == 'Spring 2017'
        assert authenticated_response.json['enrollmentTerms'][1]['enrolledUnits'] == 10
        assert len(authenticated_response.json['enrollmentTerms'][1]['enrollments']) == 3

    def test_user_analytics_term_cutoff(self, authenticated_response):
        """ignores terms before the configured cutoff"""
        for term in authenticated_response.json['enrollmentTerms']:
            assert term['termName'] != 'Spring 2016'

    def test_enrollment_without_course_site(self, authenticated_response):
        """returns enrollments with no associated course sites"""
        enrollment_without_site = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert enrollment_without_site['title'] == 'Private Carillon Lessons for Advanced Students'
        assert enrollment_without_site['canvasSites'] == []

    def test_enrollment_with_multiple_course_sites(self, authenticated_response):
        """returns multiple course sites associated with an enrollment, sorted by site id"""
        enrollment_with_multiple_sites = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert len(enrollment_with_multiple_sites['canvasSites']) == 2
        assert enrollment_with_multiple_sites['canvasSites'][0]['courseName'] == 'Radioactive Waste Management'
        assert enrollment_with_multiple_sites['canvasSites'][1]['courseName'] == 'Optional Friday Night Radioactivity Group'

    def test_multiple_primary_section_enrollments(self, authenticated_response):
        """disambiguates multiple primary sections under a single course display name"""
        classics_first = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'CLASSIC 130 LEC 001')
        classics_second = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'CLASSIC 130 LEC 002')
        assert len(classics_first['sections']) == 1
        assert classics_first['sections'][0]['units'] == 4
        assert classics_first['sections'][0]['gradingBasis'] == 'EPN'
        assert classics_first['sections'][0]['grade'] == 'P'
        assert classics_first['units'] == 4
        assert classics_first['gradingBasis'] == 'EPN'
        assert classics_first['grade'] == 'P'

        assert len(classics_second['sections']) == 1
        assert classics_second['sections'][0]['units'] == 4
        assert classics_second['sections'][0]['gradingBasis'] == 'GRD'
        assert classics_second['sections'][0]['grade'] == 'B-'
        assert classics_second['units'] == 4
        assert classics_second['gradingBasis'] == 'GRD'
        assert classics_second['grade'] == 'B-'

    def test_enrollments_sorted(self, authenticated_response):
        """sorts enrollments by course display name"""
        spring_2017_enrollments = authenticated_response.json['enrollmentTerms'][1]['enrollments']
        assert(spring_2017_enrollments[0]['displayName'] == 'CLASSIC 130 LEC 001')
        assert(spring_2017_enrollments[1]['displayName'] == 'CLASSIC 130 LEC 002')
        assert(spring_2017_enrollments[2]['displayName'] == 'MUSIC 41C')

    def test_athletic_enrollments_removed(self, authenticated_response):
        """removes athletic enrollments"""
        for enrollment in authenticated_response.json['enrollmentTerms'][0]['enrollments']:
            assert enrollment['displayName'] != 'PHYSED 11'

    def test_past_term_dropped_enrollments_removed(self, authenticated_response):
        """removes dropped enrollments from past terms"""
        for enrollment in authenticated_response.json['enrollmentTerms'][1]['enrollments']:
            print(enrollment)
            for section in enrollment['sections']:
                assert section['enrollmentStatus'] != 'D'

    def test_course_site_without_enrollment(self, authenticated_response):
        """returns course sites with no associated enrollments"""
        assert len(authenticated_response.json['enrollmentTerms'][0]['unmatchedCanvasSites']) == 0
        assert len(authenticated_response.json['enrollmentTerms'][1]['unmatchedCanvasSites']) == 1
        unmatched_site = authenticated_response.json['enrollmentTerms'][1]['unmatchedCanvasSites'][0]
        assert unmatched_site['courseCode'] == 'STAT 154'
        assert unmatched_site['courseName'] == 'Modern Statistical Prediction and Machine Learning'
        assert unmatched_site['analytics']

    def test_course_site_without_membership(self, authenticated_response):
        """returns a graceful error if the expected membership is not found in the course site"""
        course_without_membership = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        assert course_without_membership['canvasSites'][0]['analytics']['error'] == 'Unable to retrieve analytics'

    def test_course_site_with_enrollment(self, authenticated_response):
        """returns sensible data if the expected enrollment is found in the course site"""
        course_with_enrollment = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'MED ST 205')
        analytics = course_with_enrollment['canvasSites'][0]['analytics']

        assert analytics['assignmentsOnTime']['student']['raw'] == 5
        assert analytics['assignmentsOnTime']['student']['percentile'] == 93
        assert analytics['assignmentsOnTime']['courseDeciles'][0] == 0
        assert analytics['assignmentsOnTime']['courseDeciles'][9] == 5
        assert analytics['assignmentsOnTime']['courseDeciles'][10] == 6

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

    def test_empty_canvas_course_feed(self, client, fake_auth):
        """returns 200 if user is found and Canvas course feed is empty"""
        fake_auth.login(TestUserAnalytics.non_student_uid)
        response = client.get(TestUserAnalytics.non_student)
        assert response.status_code == 200
        assert response.json['uid'] == TestUserAnalytics.non_student_uid
        assert not response.json['enrollmentTerms']

    def test_canvas_profile_not_found(self, authenticated_session, client):
        """returns 404 if Canvas profile not found"""
        response = client.get(TestUserAnalytics.unknown)
        assert response.status_code == 404
        assert response.json['message'] == 'No Canvas profile found for user'

    def test_sis_enrollment_merge(self, authenticated_response):
        """merges sorted SIS enrollment data"""
        burmese = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        assert burmese['displayName'] == 'BURMESE 1A'
        assert burmese['title'] == 'Introductory Burmese'
        assert len(burmese['sections']) == 1
        assert burmese['sections'][0]['ccn'] == 90100
        assert burmese['sections'][0]['sectionNumber'] == '001'
        assert burmese['sections'][0]['enrollmentStatus'] == 'E'
        assert burmese['sections'][0]['units'] == 4
        assert burmese['sections'][0]['gradingBasis'] == 'GRD'
        assert burmese['sections'][0]['midtermGrade'] == 'D+'
        assert not burmese['sections'][0]['grade']
        assert burmese['units'] == 4
        assert burmese['gradingBasis'] == 'GRD'
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
        assert medieval['sections'][0]['gradingBasis'] == 'GRD'
        assert not medieval['sections'][0]['grade']

        nuclear = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert nuclear['displayName'] == 'NUC ENG 124'
        assert nuclear['title'] == 'Radioactive Waste Management'
        assert len(nuclear['sections']) == 2
        assert nuclear['sections'][0]['ccn'] == 90300
        assert nuclear['sections'][0]['sectionNumber'] == '002'
        assert nuclear['sections'][0]['enrollmentStatus'] == 'E'
        assert nuclear['sections'][0]['units'] == 3
        assert nuclear['sections'][0]['gradingBasis'] == 'PNP'
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
        assert music['sections'][0]['gradingBasis'] == 'GRD'
        assert music['sections'][0]['grade'] == 'A-'
        assert music['units'] == 2
        assert music['gradingBasis'] == 'GRD'
        assert music['grade'] == 'A-'

    def test_dropped_sections(self, authenticated_response):
        """collects dropped sections in a separate feed"""
        dropped_sections = authenticated_response.json['enrollmentTerms'][0]['droppedSections']
        assert len(dropped_sections) == 1
        assert dropped_sections[0]['displayName'] == 'NUC ENG 124'
        assert dropped_sections[0]['component'] == 'DIS'
        assert dropped_sections[0]['sectionNumber'] == '200'

    def test_sis_enrollment_not_found(self, authenticated_session, client):
        """gracefully handles missing SIS enrollments"""
        sis_error = MockResponse(200, {}, '{"apiResponse": {"response": {"message": "Something unexpected."}}}')
        with register_mock(sis_enrollments_api._get_enrollments, sis_error):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 200
            assert len(response.json['enrollmentTerms']) > 0
            for term in response.json['enrollmentTerms']:
                assert term['enrollments'] == []

    def test_sis_profile(self, authenticated_response):
        """provides SIS profile data"""
        sis_profile = authenticated_response.json['sisProfile']
        assert sis_profile['cumulativeGPA'] == 3.8
        assert sis_profile['cumulativeUnits'] == 101.3
        assert sis_profile['degreeProgress']['americanCultures'] is True
        assert sis_profile['degreeProgress']['americanHistory'] is True
        assert sis_profile['degreeProgress']['americanInstitutions'] is True
        assert sis_profile['degreeProgress']['entryLevelWriting'] is True
        assert sis_profile['degreeProgress']['foreignLanguage'] is True
        assert sis_profile['emailAddress'] == 'oski@berkeley.edu'
        assert sis_profile['level']['code'] == '30'
        assert sis_profile['level']['description'] == 'Junior'
        assert sis_profile['phoneNumber'] == '415/123-4567'
        assert len(sis_profile['plans']) == 2
        assert sis_profile['plans'][0]['description'] == 'English BA'
        assert sis_profile['plans'][0]['program'] == 'Undergrad Letters & Science'
        assert sis_profile['plans'][1]['description'] == 'Astrophysics BS'
        assert sis_profile['plans'][1]['program'] == 'Undergrad Letters & Science'
        assert sis_profile['preferredName'] == 'Osk Bear'
        assert sis_profile['primaryName'] == 'Oski Bear'
        assert sis_profile['termsInAttendance'] == 5

    def test_sis_profile_unexpected_payload(self, authenticated_session, client):
        """gracefully handles unexpected SIS profile data"""
        sis_response = MockResponse(200, {}, '{"apiResponse": {"response": {"message": "Something wicked."}}}')
        with register_mock(sis_student_api._get_student, sis_response):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 200
            assert response.json['canvasProfile']
            assert not response.json['sisProfile']

    def test_sis_profile_error(self, authenticated_session, client):
        """gracefully handles SIS profile error"""
        sis_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(sis_student_api._get_student, sis_error):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 200
            assert response.json['canvasProfile']
            assert not response.json['sisProfile']
