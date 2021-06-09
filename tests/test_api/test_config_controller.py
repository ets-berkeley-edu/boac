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
def announcement_unpublished():
    return _update_service_announcement(text='Not reddy four prime tyme', is_published=False)


@pytest.fixture()
def announcement_published():
    return _update_service_announcement(text='Papa was a rodeo', is_published=True)


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
        assert data['googleAnalyticsId'] == 'UA-XXX-X'
        assert '@' in data['supportEmailAddress']
        assert data['maxAttachmentsPerNote'] > 0
        assert data['pingFrequency'] == 900000
        assert data['timezone'] == 'America/Los_Angeles'
        category_type_options = data['degreeCategoryTypeOptions']
        assert len(category_type_options) == 3
        assert 'Placeholder' not in ''.join(category_type_options)

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

    def test_not_authenticated(self, client, announcement_published):
        """Returns None to anonymous user."""
        assert self._api_service_announcement(client) is None

    def test_advisor_cannot_read_unpublished(self, client, advisor_session, announcement_unpublished):
        """Advisor does not have access to the unpublished announcement."""
        assert self._api_service_announcement(client) is None

    def test_admin_can_read_unpublished(self, client, admin_session, announcement_unpublished):
        """Admin has access to the unpublished announcement."""
        api_json = self._api_service_announcement(client)
        assert api_json == {
            'text': announcement_unpublished['text'],
            'isPublished': False,
        }

    def test_announcement_published(self, client, advisor_session, announcement_published):
        """All users get the service announcement."""
        assert self._api_service_announcement(client) == announcement_published


class TestUpdateAnnouncement:
    """Tool Settings API."""

    @staticmethod
    def _publish_announcement(client, publish, expected_status_code=200):
        response = client.post(
            '/api/service_announcement/publish',
            content_type='application/json',
            data=json.dumps({'publish': publish}),
        )
        assert response.status_code == expected_status_code
        return response.json

    @staticmethod
    def _update_announcement(client, text, expected_status_code=200):
        response = client.post(
            '/api/service_announcement/update',
            content_type='application/json',
            data=json.dumps({'text': text}),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated_update(self, client):
        """Rejects anonymous user's attempt to update."""
        self._update_announcement(client, text='The sun goes down and the world goes dancing', expected_status_code=401)

    def test_not_authenticated_publish(self, client):
        """Rejects anonymous user's attempt to publish."""
        self._publish_announcement(client, publish=True, expected_status_code=401)

    def test_not_authorized_update(self, client, advisor_session):
        """Rejects advisor's attempt to update."""
        self._update_announcement(client, text='Abigail, Belle of Kilronan', expected_status_code=401)

    def test_not_authorized_publish(self, client, advisor_session):
        """Rejects advisor's attempt to publish."""
        self._publish_announcement(client, publish=True, expected_status_code=401)

    def test_update_service_announcement(self, client, admin_session, announcement_published):
        """Admin can update the service announcement text."""
        text = """
        Papa was a rodeo, Mama was a rock'n'roll band
        I could play guitar and rope a steer before I learned to stand
        Home was anywhere with diesel gas, Love was a trucker's hand
        Never stuck around long enough for a one night stand
        Before you kiss me you should know
        Papa was a rodeo
        """
        self._update_announcement(client, text=text)
        # Verify the update
        response = client.get('/api/service_announcement')
        assert response.status_code == 200
        assert response.json.get('isPublished') is True
        assert 'Home was anywhere with diesel gas, Love was a trucker\'s hand' in response.json.get('text')


def _update_service_announcement(text, is_published):
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_TEXT', text)
    ToolSetting.upsert('SERVICE_ANNOUNCEMENT_IS_PUBLISHED', is_published)
    return {
        'text': text,
        'isPublished': is_published,
    }
