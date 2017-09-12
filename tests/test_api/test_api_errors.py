class TestApiErrors:
    """API error handling"""
    def test_api_route_not_found(self, client):
        """returns a 404 for unknown API routes"""
        response = client.get('/api/rumpus/')
        assert response.status_code == 404
        assert response.json['message'] == 'The requested resource could not be found.'

    def test_non_api_route_not_found(self, client):
        """serves front-end template for unknown non-API routes"""
        response = client.get('/rumpus/')
        assert response.status_code == 200
        assert '<title>BOAC</title>' in str(response.data)
