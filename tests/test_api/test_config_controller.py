class TestConfigController:
    """Config API."""

    def test_anonymous_api_config_request(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'boacEnv' in response.json
        # In tests, certain configs are omitted or disabled (e.g., Google Analytics)
        assert response.json['ebEnvironment'] is None
        assert response.json['googleAnalyticsId'] is False

    def test_anonymous_api_version_request(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/version')
        assert response.status_code == 200
        assert 'version' in response.json
        assert 'build' in response.json
