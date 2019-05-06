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

from boac.models.tool_setting import ToolSetting
import pytest
import simplejson as json
from tests.util import override_config


@pytest.fixture()
def admin_session(fake_auth):
    fake_auth.login('2040')


@pytest.fixture()
def advisor_session(fake_auth):
    fake_auth.login('1081940')


@pytest.fixture()
def announcement_is_not_live():
    return _update_service_announcement(text='Not reddy four prime tyme', is_live=False)


@pytest.fixture()
def announcement_is_live():
    return _update_service_announcement(text='Papa was a rodeo', is_live=True)


class TestConfigController:
    """Config API."""

    def test_anonymous(self, client):
        """Returns a well-formed response to anonymous user."""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'boacEnv' in response.json
        # In tests, certain configs are omitted or disabled (e.g., Google Analytics)
        data = response.json
        assert data['ebEnvironment'] is None
        assert data['googleAnalyticsId'] is False
        assert '@' in data['supportEmailAddress']
        assert data['featureFlagEditNotes'] is True
        assert data['maxAttachmentsPerNote'] > 0

    def test_anonymous_version_request(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/version')
        assert response.status_code == 200
        assert 'version' in response.json
        assert 'build' in response.json

    def test_demo_mode_on(self, app, client):
        """Demo-mode/blur is on."""
        with override_config(app, 'DEMO_MODE_AVAILABLE', True):
            assert client.get('/api/config').json.get('isDemoModeAvailable')

    def test_demo_mode_off(self, app, client):
        """Demo-mode/blur is off."""
        with override_config(app, 'DEMO_MODE_AVAILABLE', False):
            assert not client.get('/api/config').json.get('isDemoModeAvailable')


class TestServiceAnnouncement:
    """Tool Settings API."""

    @staticmethod
    def _api_service_announcement(client, expected_status_code=200):
        response = client.get('/api/service_announcement')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, announcement_is_live):
        """Rejects anonymous user."""
        self._api_service_announcement(client, expected_status_code=401)

    def test_announcement_is_not_live_as_advisor(self, client, advisor_session, announcement_is_not_live):
        """Advisor does not have access to the unpublished announcement."""
        assert self._api_service_announcement(client) is None

    def test_announcement_is_not_live_as_admin(self, client, admin_session, announcement_is_not_live):
        """Admin has access to the unpublished announcement."""
        unpublished_announcement = announcement_is_not_live['text']
        api_json = self._api_service_announcement(client)
        assert api_json == {
            'text': unpublished_announcement,
            'isLive': False,
        }

    def test_announcement_is_live(self, client, advisor_session, announcement_is_live):
        """All users get the service announcement."""
        assert self._api_service_announcement(client) == announcement_is_live


class TestUpdateAnnouncement:
    """Tool Settings API."""

    @staticmethod
    def _api_update_announcement(client, text, is_live, expected_status_code=200):
        response = client.post(
            '/api/service_announcement/update',
            content_type='application/json',
            data=json.dumps({'text': text, 'isLive': is_live}),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Rejects anonymous user."""
        self._api_update_announcement(
            client,
            text='The sun goes down and the world goes dancing',
            is_live=True,
            expected_status_code=401,
        )

    def test_not_authorized(self, client, advisor_session):
        """Rejects non-admin user."""
        self._api_update_announcement(
            client,
            text='Abigail, Belle of Kilronan',
            is_live=True,
            expected_status_code=401,
        )

    def test_update_service_announcement(self, client, admin_session):
        """Admin can update service announcement."""
        text = 'Papa was a rodeo'
        self._api_update_announcement(client, text=text, is_live=True)
        # Verify the update
        response = client.get('/api/service_announcement')
        assert response.status_code == 200
        assert response.json == {
            'text': text,
            'isLive': True,
        }


def _update_service_announcement(text, is_live):
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_TEXT', text)
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_IS_LIVE', is_live)
    return {
        'text': text,
        'isLive': is_live,
    }
