class TestCachejobAccess:

    def test_not_authenticated(self, client):
        """requires authentication"""
        response = client.get('/api/admin/cachejob')
        assert response.status_code == 401

    def test_not_an_admin(self, client, fake_auth):
        """returns 403 for normal users"""
        test_uid = '6446'
        fake_auth.login(test_uid)
        response = client.get('/api/admin/cachejob')
        assert response.status_code == 401

    def test_as_an_admin(self, client, fake_auth):
        """returns success"""
        test_uid = '2040'
        fake_auth.login(test_uid)
        response = client.get('/api/admin/cachejob')
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'application/json'

    def test_api_key_match(self, app, client):
        api_key = 'Hey ho, seely sheepe!'
        app.config['API_KEY'] = api_key
        headers = {'app_key': api_key}
        response = client.get('/api/admin/cachejob', headers=headers)
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'application/json'

    def test_api_key_no_match(self, app, client):
        app.config['API_KEY'] = 'Hey ho, seely sheepe!'
        headers = {'app_key': 'I saw the bouncing Bellibone'}
        response = client.get('/api/admin/cachejob', headers=headers)
        assert response.status_code == 401

    def test_api_key_disabled(self, app, client):
        app.config['API_KEY'] = None
        headers = {'app_key': None}
        response = client.get('/api/admin/cachejob', headers=headers)
        assert response.status_code == 401
