import boac.externals.canvas as canvas
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
        assert response.json['canvas_profile'] is False

    def test_profile_includes_message_if_canvas_failure(self, client, fake_auth):
        test_uid = '1133399'
        fake_auth.login(test_uid)
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas.get_user_for_uid, canvas_error):
            response = client.get('/api/profile')
            assert response.status_code == 200
            assert response.json['uid'] == test_uid
            assert response.json['canvas_profile']['error']

    def test_includes_canvas_profile_if_available(self, client, fake_auth):
        test_uid = '2040'
        fake_auth.login(test_uid)
        response = client.get('/api/profile')
        assert response.json['canvas_profile']['sis_login_id'] == test_uid


class TestUserAnalytics:
    """User Analytics API"""

    api_path = '/api/user/{}/analytics'
    field_hockey_star = api_path.format(61889)
    non_student_uid = 2040
    non_student = api_path.format(non_student_uid)

    @pytest.fixture()
    def authenticated_session(self, fake_auth):
        test_uid = '1133399'
        fake_auth.login(test_uid)

    @pytest.fixture()
    def authenticated_response(self, authenticated_session, client):
        return client.get(TestUserAnalytics.field_hockey_star)

    @staticmethod
    def get_course_for_code(response, code):
        return next((course for course in response.json['courses'] if course['courseCode'] == code), None)

    def test_user_analytics_not_authenticated(self, client):
        """returns 401 if not authenticated"""
        response = client.get(TestUserAnalytics.field_hockey_star)
        assert response.status_code == 401

    def test_user_analytics_authenticated(self, authenticated_response):
        """returns a well-formed response if authenticated"""
        assert authenticated_response.status_code == 200
        assert authenticated_response.json['uid'] == '61889'
        assert authenticated_response.json['canvasProfile']['id'] == 9000100
        assert len(authenticated_response.json['courses']) == 3
        for course in authenticated_response.json['courses']:
            assert course['courseCode']
            assert course['canvasCourseId']
            assert course['courseName']
            assert course['analytics']

    def test_course_without_enrollment(self, authenticated_response):
        """returns a graceful error if the expected enrollment is not found"""
        course_without_enrollment = TestUserAnalytics.get_course_for_code(authenticated_response, 'BURMESE 1A')
        assert course_without_enrollment['analytics']['error'] == 'Unable to retrieve analytics'

    def test_course_with_enrollment(self, authenticated_response):
        """returns sensible data if the expected enrollment is found"""
        course_with_enrollment = TestUserAnalytics.get_course_for_code(authenticated_response, 'MED ST 205')

        assert course_with_enrollment['analytics']['assignmentsOnTime']['student']['raw'] == 5
        assert course_with_enrollment['analytics']['assignmentsOnTime']['student']['percentile'] == pytest.approx(92.9, 0.1)
        assert course_with_enrollment['analytics']['assignmentsOnTime']['student']['zscore'] == pytest.approx(1.469, 0.01)
        assert course_with_enrollment['analytics']['assignmentsOnTime']['courseDeciles'][0] == 0.0
        assert course_with_enrollment['analytics']['assignmentsOnTime']['courseDeciles'][9] == 5.0
        assert course_with_enrollment['analytics']['assignmentsOnTime']['courseDeciles'][10] == 6.0

        assert course_with_enrollment['analytics']['pageViews']['student']['raw'] == 768
        assert course_with_enrollment['analytics']['pageViews']['student']['percentile'] == pytest.approx(54.3, 0.1)
        assert course_with_enrollment['analytics']['pageViews']['student']['zscore'] == pytest.approx(0.108, 0.01)
        assert course_with_enrollment['analytics']['pageViews']['courseDeciles'][0] == 9.0
        assert course_with_enrollment['analytics']['pageViews']['courseDeciles'][9] == pytest.approx(917.0)
        assert course_with_enrollment['analytics']['pageViews']['courseDeciles'][10] == 31983.0

        assert course_with_enrollment['analytics']['participations']['student']['raw'] == 5
        assert course_with_enrollment['analytics']['participations']['student']['percentile'] == pytest.approx(82.64, 0.01)
        assert course_with_enrollment['analytics']['participations']['student']['zscore'] == pytest.approx(0.941, 0.01)
        assert course_with_enrollment['analytics']['participations']['courseDeciles'][0] == 0.0
        assert course_with_enrollment['analytics']['participations']['courseDeciles'][9] == 6.0
        assert course_with_enrollment['analytics']['participations']['courseDeciles'][10] == 12.0

    def test_empty_canvas_course_feed(self, client, fake_auth):
        """returns 200 if user is found and Canvas course feed is empty"""
        fake_auth.login(TestUserAnalytics.non_student_uid)
        response = client.get(TestUserAnalytics.non_student)
        assert response.status_code == 200
        assert int(response.json['uid']) == TestUserAnalytics.non_student_uid
        assert not response.json['courses']

    def test_canvas_profile_not_found(self, authenticated_session, client):
        """returns 404 if Canvas profile not found"""
        canvas_error = MockResponse(404, {}, '{"message": "Resource not found."}')
        with register_mock(canvas.get_user_for_uid, canvas_error):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 404
            assert response.json['message'] == 'No Canvas profile found for user'

    def test_canvas_unreachable(self, authenticated_session, client):
        """returns 500 if Canvas unreachable"""
        canvas_error = MockResponse(500, {}, '{"message": "Internal server error."}')
        with register_mock(canvas.get_user_for_uid, canvas_error):
            response = client.get(TestUserAnalytics.field_hockey_star)
            assert response.status_code == 500
            assert response.json['message'] == 'Unable to reach bCourses'
