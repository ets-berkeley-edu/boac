import json


class TestDevAuth:
    """DevAuth handling."""

    authorized_uid = '2040'

    def test_disabled(self, app, client):
        """Blocks access unless enabled."""
        app.config['DEVELOPER_AUTH_ENABLED'] = False
        response = client.post('/devauth/login')
        assert response.status_code == 404
        params = {'uid': self.authorized_uid, 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 404

    def test_password_fail(self, app, client):
        """Fails if no match on developer password."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': self.authorized_uid, 'password': 'Born 2 Lose'}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 403

    def test_authorized_user_fail(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': 'A Bad Sort', 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 403

    def test_known_user_with_correct_password_logs_in(self, app, client):
        """There is a happy path."""
        app.config['DEVELOPER_AUTH_ENABLED'] = True
        params = {'uid': self.authorized_uid, 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
        response = client.post('/devauth/login', data=json.dumps(params), content_type='application/json')
        assert response.status_code == 302
        response = client.get('/api/status')
        assert response.status_code == 200
        assert response.json['authenticated_as']['uid'] == self.authorized_uid
        response = client.get('/logout')
        assert response.status_code == 200
        response = client.get('/api/status')
        assert response.status_code == 200
        assert response.json['authenticated_as']['is_anonymous']
