class TestStatusController:
    """Status API"""

    def test_anonymous_status(self, client):
        """returns a well-formed response"""
        response = client.get('/api/status')
        assert response.status_code == 200
        assert 'authenticated_as' in response.json
        assert not response.json['authenticated_as']['is_authenticated']

    def test_when_authenticated(self, client, fake_auth):
        test_uid = '1133399'
        fake_auth.login(test_uid)
        response = client.get('/api/status')
        assert response.status_code == 200
        assert response.json['authenticated_as']['is_authenticated']
        assert response.json['authenticated_as']['uid'] == test_uid

    def test_includes_canvas_profile_if_available(self, client, fake_auth):
        test_uid = '2040'
        fake_auth.login(test_uid)
        response = client.get('/api/status')
        assert response.json['canvas_profile']['sis_login_id'] == test_uid
