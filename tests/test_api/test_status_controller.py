class TestStatusController:
    '''Status API'''
    def test_anonymous_status(self, client):
        '''returns a well-formed response'''
        response = client.get('/api/status')
        assert response.status_code == 200
        assert 'authenticated_as' in response.json
