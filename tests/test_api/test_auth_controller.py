"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import json

from tests.util import override_config


class TestDevAuth:
    """DevAuth handling."""

    admin_uid = '2040'

    def test_disabled(self, app, client):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            response = client.post('/api/auth/dev_auth_login')
            assert response.status_code == 404
            params = {'uid': self.admin_uid, 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
            response = client.post('/api/auth/dev_auth_login', data=json.dumps(params), content_type='application/json')
            assert response.status_code == 404

    def test_password_fail(self, app, client):
        """Fails if no match on developer password."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {'uid': self.admin_uid, 'password': 'Born 2 Lose'}
            response = client.post('/api/auth/dev_auth_login', data=json.dumps(params), content_type='application/json')
            assert response.status_code == 401

    def test_authorized_user_fail(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {'uid': 'A Bad Sort', 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
            response = client.post('/api/auth/dev_auth_login', data=json.dumps(params), content_type='application/json')
            assert response.status_code == 403

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {'uid': '1015674', 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
            response = client.post('/api/auth/dev_auth_login', data=json.dumps(params), content_type='application/json')
            assert response.status_code == 403

    def test_known_user_with_correct_password_logs_in(self, app, client):
        """There is a happy path."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {'uid': self.admin_uid, 'password': app.config['DEVELOPER_AUTH_PASSWORD']}
            response = client.post('/api/auth/dev_auth_login', data=json.dumps(params), content_type='application/json')
            assert response.status_code == 200
            response = client.get('/api/user/status')
            assert response.status_code == 200
            assert response.json['uid'] == self.admin_uid
            response = client.get('/api/auth/logout')
            assert response.status_code == 200
            response = client.get('/api/user/status')
            assert response.status_code == 200
            assert response.json['isAnonymous']


class TestCasAuth:
    """CAS login URL generation and redirects."""

    def test_cas_login_url(self, client):
        """Returns berkeley.edu URL of CAS login page."""
        response = client.get('/cas/login_url')
        assert response.status_code == 200
        assert 'berkeley.edu/cas/login' in response.json.get('casLoginUrl')

    def test_cas_callback_with_invalid_ticket(self, client):
        """Fails if CAS can not verify the ticket."""
        response = client.get('/cas/callback?ticket=is_invalid')
        assert response.status_code == 302
        assert 'error' in response.location


class TestBecomeUser:
    """Easy access to DevAuth for admin users."""

    admin_uid = '2040'
    advisor_uid = '1133399'

    def test_disabled(self, app, client, fake_auth):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            fake_auth.login(self.admin_uid)
            response = client.post(
                '/api/auth/become_user',
                data=json.dumps({'uid': self.advisor_uid}),
                content_type='application/json',
            )
            assert response.status_code == 404

    def test_unauthorized_user(self, app, client, fake_auth):
        """Blocks access unless user is admin."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            fake_auth.login(self.advisor_uid)
            response = client.post('/api/auth/become_user', data=json.dumps({'uid': self.advisor_uid}), content_type='application/json')
            assert response.status_code == 401

    def test_authorized_user(self, app, client, fake_auth):
        """Gives access to admin user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            fake_auth.login(self.admin_uid)
            response = client.post('/api/auth/become_user', data=json.dumps({'uid': self.advisor_uid}), content_type='application/json')
            assert response.status_code == 200
            response = client.get('/api/user/status')
            assert response.status_code == 200
            assert response.json['uid'] == self.advisor_uid
