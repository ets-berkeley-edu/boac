"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.models.user_login import UserLogin
import cas
import mock
from tests.util import override_config, pause_mock_sts

admin_uid = '2040'
advisor_uid = '1133399'
unauthorized_uid = '1015674'
no_calnet_record_for_uid = '13'


class TestDevAuth:
    """DevAuth handling."""

    @staticmethod
    def _api_dev_auth_login(client, params, expected_status_code=200):
        response = client.post(
            '/api/auth/dev_auth_login',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_disabled(self, app, client):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': admin_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
                expected_status_code=404,
            )

    def test_password_fail(self, app, client):
        """Fails if no match on developer password."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': admin_uid,
                    'password': 'Born 2 Lose',
                },
                expected_status_code=401,
            )

    def test_authorized_user_fail(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': 'A Bad Sort',
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
                expected_status_code=403,
            )

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                params={
                    'uid': unauthorized_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
                expected_status_code=403,
            )

    def test_known_user_with_correct_password_logs_in(self, app, client):
        """There is a happy path."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            api_json = self._api_dev_auth_login(
                client,
                params={
                    'uid': admin_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
            )
            assert api_json['uid'] == admin_uid
            response = client.get('/api/auth/logout')
            assert response.status_code == 200
            assert response.json['isAnonymous']

    def test_user_expired_according_to_calnet(self, app, client):
        """Fails if user has no record in LDAP."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            from boac.models import json_cache
            json_cache.clear('%')
            self._api_dev_auth_login(
                client,
                params={
                    'uid': no_calnet_record_for_uid,
                    'password': app.config['DEVELOPER_AUTH_PASSWORD'],
                },
                expected_status_code=403,
            )


class TestAuthorization:

    @staticmethod
    def _api_my_profile(client, expected_status_code=200):
        response = client.get('/api/profile/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized_is_not_active(self, client, fake_auth):
        fake_auth.login(unauthorized_uid)
        api_json = self._api_my_profile(client)
        assert not api_json['isActive']
        assert not api_json['departments']

    def test_admin_is_active(self, client, fake_auth):
        fake_auth.login(admin_uid)
        api_json = self._api_my_profile(client)
        assert api_json['isActive']
        assert not api_json['departments']

    def test_is_active(self, client, fake_auth):
        fake_auth.login(advisor_uid)
        api_json = self._api_my_profile(client)
        assert api_json['isActive']
        assert len(api_json['departments']) == 1


class TestCasAuth:
    """CAS login URL generation and redirects."""

    def test_cas_login_url(self, client):
        """Returns berkeley.edu URL of CAS login page."""
        response = client.get('/cas/login_url')
        assert response.status_code == 200
        assert 'berkeley.edu/cas/login' in response.json.get('casLoginUrl')

    def test_cas_callback_with_invalid_ticket(self, client):
        """Fails if CAS can not verify the ticket."""
        with pause_mock_sts():
            response = client.get('/cas/callback?ticket=is_invalid')
            assert response.status_code == 302
            assert 'error' in response.location

    @mock.patch.object(cas.CASClientV3, 'verify_ticket', autospec=True)
    def test_cas_callback_with_valid_ticket(self, mock_verify_ticket, client):
        """Records a successful user login."""
        mock_verify_ticket.return_value = (advisor_uid, {}, 'is_valid')
        response = client.get('/cas/callback?ticket=is_valid')
        assert response.status_code == 302
        assert 'casLogin=true' in response.location

        user_login = UserLogin.query.filter_by(uid=advisor_uid).first()
        assert user_login.uid == advisor_uid


class TestBecomeUser:
    """Easy access to DevAuth for admin users."""

    def test_disabled(self, app, client, fake_auth):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            fake_auth.login(admin_uid)
            response = client.post(
                '/api/auth/become_user',
                data=json.dumps({'uid': advisor_uid}),
                content_type='application/json',
            )
            assert response.status_code == 404

    def test_unauthorized_user(self, app, client, fake_auth):
        """Blocks access unless user is admin."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            fake_auth.login(advisor_uid)
            response = client.post('/api/auth/become_user', data=json.dumps({'uid': advisor_uid}), content_type='application/json')
            assert response.status_code == 401

    def test_authorized_user(self, app, client, fake_auth):
        """Gives access to admin user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            fake_auth.login(admin_uid)
            response = client.post('/api/auth/become_user', data=json.dumps({'uid': advisor_uid}), content_type='application/json')
            assert response.status_code == 200
            assert response.json['uid'] == advisor_uid
