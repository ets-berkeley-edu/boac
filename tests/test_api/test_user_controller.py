import boac.externals.canvas as canvas
from boac.lib.mockingbird import MockResponse, register_mock


class TestUserController:
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
        assert response.json['canvas_profile'] == False

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