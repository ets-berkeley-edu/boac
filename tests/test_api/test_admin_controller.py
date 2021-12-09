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

import pytest
from tests.util import override_config


@pytest.fixture()
def admin_session(fake_auth):
    fake_auth.login('2040')


@pytest.fixture()
def asc_advisor_session(fake_auth):
    fake_auth.login('1081940')


advisee_sid = '5000000000'


class TestCachejobAccess:

    def test_not_authenticated(self, client):
        """Require authentication."""
        response = client.get('/api/admin/cachejob')
        assert response.status_code == 401

    def test_not_an_admin(self, client, asc_advisor_session):
        """Return 403 for normal users."""
        response = client.get('/api/admin/cachejob')
        assert response.status_code == 401

    def test_as_an_admin(self, client, admin_session):
        """Return success."""
        response = client.get('/api/admin/cachejob')
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'application/json'

    def test_api_key_match(self, app, client):
        api_key = 'Hey ho, seely sheepe!'
        with override_config(app, 'API_KEY', api_key):
            headers = {'app_key': api_key}
            response = client.get('/api/admin/cachejob', headers=headers)
            assert response.status_code == 200
            assert response.headers.get('Content-Type') == 'application/json'

    def test_api_key_no_match(self, app, client):
        with override_config(app, 'API_KEY', 'Hey ho, seely sheepe!'):
            headers = {'app_key': 'I saw the bouncing Bellibone'}
            response = client.get('/api/admin/cachejob', headers=headers)
            assert response.status_code == 401

    def test_api_key_disabled(self, app, client):
        with override_config(app, 'API_KEY', None):
            headers = {'app_key': None}
            response = client.get('/api/admin/cachejob', headers=headers)
            assert response.status_code == 401
