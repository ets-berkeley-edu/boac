class TestConfigController:
    """Config API"""

    def test_anonymous_api_config_request(self, client):
        """returns a well-formed response"""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'boacEnv' in response.json
        # In tests, Google Analytics is integrated and disabled
        assert response.json['googleAnalyticsId'] is False

    def test_anonymous_api_version_request(self, client):
        """returns a well-formed response"""
        response = client.get('/api/version')
        assert response.status_code == 200
        assert 'version' in response.json
        assert 'build' in response.json
