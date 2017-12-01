from boac.externals import sis_enrollments_api, sis_student_api
from boac.lib.mockingbird import MockResponse, register_mock
import pytest


class TestUserProfile:
    """User Profile API"""

    def test_profile_not_authenticated(self, client):
        """returns a well-formed response"""
        response = client.get('/api/profile')
        assert response.status_code == 200
        assert not response.json['uid']

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
        assert len(authenticated_response.json['enrollmentTerms'][0]['enrollments']) == 3
        assert authenticated_response.json['enrollmentTerms'][1]['termName'] == 'Spring 2017'
        assert len(authenticated_response.json['enrollmentTerms'][1]['enrollments']) == 1

    def test_enrollment_without_course_site(self, authenticated_response):
        """returns enrollments with no associated course sites"""
        enrollment_without_site = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert enrollment_without_site['title'] == 'Private Carillon Lessons for Advanced Students'
        assert enrollment_without_site['canvasSites'] == []

    def test_enrollment_with_multiple_course_sites(self, authenticated_response):
        """returns multiple course sites associated with an enrollment"""
        enrollment_with_multiple_sites = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert len(enrollment_with_multiple_sites['canvasSites']) == 2
        assert enrollment_with_multiple_sites['canvasSites'][0]['courseName'] == 'Radioactive Waste Management'
        assert enrollment_with_multiple_sites['canvasSites'][1]['courseName'] == 'Optional Friday Night Radioactivity Group'

    def test_athletic_enrollments_removed(self, authenticated_response):
        """removes athletic enrollments"""
        for enrollment in authenticated_response.json['enrollmentTerms'][0]['enrollments']:
            assert enrollment['displayName'] != 'PHYSED 11'

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
        assert analytics['assignmentsOnTime']['student']['zscore'] == pytest.approx(1.469, 0.01)
        assert analytics['assignmentsOnTime']['courseDeciles'][0] == 0
        assert analytics['assignmentsOnTime']['courseDeciles'][9] == 5
        assert analytics['assignmentsOnTime']['courseDeciles'][10] == 6

        assert analytics['pageViews']['student']['raw'] == 768
        assert analytics['pageViews']['student']['percentile'] == 54
        assert analytics['pageViews']['student']['zscore'] == pytest.approx(0.108, 0.01)
        assert analytics['pageViews']['courseDeciles'][0] == 9
        assert analytics['pageViews']['courseDeciles'][9] == 917
        assert analytics['pageViews']['courseDeciles'][10] == 31983

        assert analytics['participations']['student']['raw'] == 5
        assert analytics['participations']['student']['percentile'] == 83
        assert analytics['participations']['student']['zscore'] == pytest.approx(0.941, 0.01)
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
        """merges SIS enrollment data"""
        burmese = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'BURMESE 1A')
        assert burmese['ccn'] == 90100
        assert burmese['displayName'] == 'BURMESE 1A'
        assert burmese['title'] == 'Introductory Burmese'
        assert burmese['sectionNumber'] == '001'
        assert burmese['enrollmentStatus'] == 'E'
        assert burmese['units'] == 4
        assert burmese['gradingBasis'] == 'GRD'
        assert burmese['grade'] == 'B+'

        medieval = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'MED ST 205')
        assert medieval['ccn'] == 90200
        assert medieval['displayName'] == 'MED ST 205'
        assert medieval['title'] == 'Medieval Manuscripts as Primary Sources'
        assert medieval['sectionNumber'] == '001'
        assert medieval['enrollmentStatus'] == 'D'
        assert medieval['units'] == 5
        assert medieval['gradingBasis'] == 'GRD'
        assert not medieval['grade']

        nuclear = TestUserAnalytics.get_course_for_code(authenticated_response, '2178', 'NUC ENG 124')
        assert nuclear['ccn'] == 90300
        assert nuclear['displayName'] == 'NUC ENG 124'
        assert nuclear['title'] == 'Radioactive Waste Management'
        assert nuclear['sectionNumber'] == '002'
        assert nuclear['enrollmentStatus'] == 'E'
        assert nuclear['units'] == 3
        assert nuclear['gradingBasis'] == 'PNP'
        assert nuclear['grade'] == 'P'

        music = TestUserAnalytics.get_course_for_code(authenticated_response, '2172', 'MUSIC 41C')
        assert music['ccn'] == 80100
        assert music['displayName'] == 'MUSIC 41C'
        assert music['title'] == 'Private Carillon Lessons for Advanced Students'
        assert music['sectionNumber'] == '001'
        assert music['enrollmentStatus'] == 'E'
        assert music['units'] == 2
        assert music['gradingBasis'] == 'GRD'
        assert music['grade'] == 'A-'

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
        assert sis_profile['plan']['description'] == 'English BA'
        assert sis_profile['plan']['fromDate'] == '2016-01-12'
        assert sis_profile['plan']['program'] == 'Undergrad Letters & Science'
        assert sis_profile['preferredName'] == 'Osk Bear'
        assert sis_profile['primaryName'] == 'Oski Bear'

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
