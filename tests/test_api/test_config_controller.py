class TestConfigController:
    """Config API"""

    def test_anonymous_request(self, client):
        """returns a well-formed response"""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'boacEnv' in response.json
        # In tests, Google Analytics is integrated and disabled
        assert response.json['googleAnalyticsId'] is False
        assert 'version' in response.json
