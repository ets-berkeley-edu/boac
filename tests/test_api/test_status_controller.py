class TestStatusController:
    """Status API."""

    def test_anonymous_status(self, client):
        """Returns a well-formed response."""
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

    def test_ping(self, client):
        """Answers the phone when pinged."""
        response = client.get('/api/ping')
        assert response.status_code == 200
        assert response.json['app'] is True
        assert response.json['db'] is True
