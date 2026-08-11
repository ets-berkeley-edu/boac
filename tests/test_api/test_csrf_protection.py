"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

coe_advisor_uid = '1133399'


class TestCsrfProtection:

    def test_blocks_mutating_request_with_no_token(self, app, client, fake_auth):
        """Rejects a state-changing request that carries no CSRF token."""
        fake_auth.login(coe_advisor_uid)
        with override_config(app, 'WTF_CSRF_ENABLED', True):
            response = client.post('/api/note/create_draft', data=json.dumps({'sid': None}), content_type='application/json')
            assert response.status_code == 400
            assert response.json['error_class'] == 'CSRFError'

    def test_allows_mutating_request_with_token_from_config_endpoint(self, app, client, fake_auth):
        """Accepts a state-changing request carrying the token the app fetches from /api/config at boot."""
        fake_auth.login(coe_advisor_uid)
        with override_config(app, 'WTF_CSRF_ENABLED', True):
            csrf_token = client.get('/api/config').json['csrfToken']
            response = client.post(
                '/api/note/create_draft',
                data=json.dumps({'sid': None}),
                content_type='application/json',
                headers={'X-CSRFToken': csrf_token},
            )
            assert response.status_code == 200

    def test_get_requests_need_no_token(self, app, client, fake_auth):
        """Safe methods are never subject to CSRF checks."""
        fake_auth.login(coe_advisor_uid)
        with override_config(app, 'WTF_CSRF_ENABLED', True):
            assert client.get('/api/config').status_code == 200

    def test_exempts_api_key_authenticated_requests(self, app, client):
        """Service-to-service calls authenticated via the App-Key header carry no session cookie."""
        with override_config(app, 'WTF_CSRF_ENABLED', True), override_config(app, 'API_KEY', 'a-test-api-key'), \
                override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            response = client.post(
                '/api/auth/become_user',
                data=json.dumps({'uid': coe_advisor_uid}),
                content_type='application/json',
                headers={'App-Key': 'a-test-api-key'},
            )
            assert response.status_code != 400
