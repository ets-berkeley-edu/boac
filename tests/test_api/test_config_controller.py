class TestConfigController:
    """Config API"""

    def test_anonymous_request(self, client):
        """returns a well-formed response"""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'boacEnv' in response.json
        assert 'version' in response.json
