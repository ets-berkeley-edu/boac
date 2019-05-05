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

from datetime import datetime

from boac.lib.util import camelize
from boac.models.tool_setting import ToolSetting
import pytest
import simplejson as json


@pytest.fixture()
def admin_session(fake_auth):
    fake_auth.login('2040')


@pytest.fixture()
def advisor_session(fake_auth):
    fake_auth.login('1081940')


@pytest.fixture()
def mock_tool_settings():
    return [_create(is_public=False), _create(is_public=True), _create(is_public=False)]


class TestGetToolSettings:
    """Tool Settings API."""

    @staticmethod
    def _api_tool_settings(client, keys, expected_status_code=200):
        response = client.post(
            '/api/tool_settings',
            content_type='application/json',
            data=json.dumps({'keys': keys}),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Rejects anonymous user."""
        tool_setting = _create(is_public=True)
        self._api_tool_settings(client, keys=[tool_setting.key], expected_status_code=401)

    def test_authenticated_advisor(self, advisor_session, client, mock_tool_settings):
        """Only serves public settings to non-admin user."""
        keys = [s.key for s in mock_tool_settings]
        api_json = self._api_tool_settings(client, keys=keys)
        assert len(api_json) == 1
        expected = mock_tool_settings[1]
        assert api_json == {
            camelize(expected.key): expected.value,
        }

    def test_authenticated_admin(self, admin_session, client, mock_tool_settings):
        """Serves all tool settings to admin user."""
        api_json = self._api_tool_settings(client, keys=[s.key for s in mock_tool_settings])
        assert len(api_json) == 3
        for setting in mock_tool_settings:
            assert api_json[camelize(setting.key)] == setting.value


class TestUpsertToolSettings:
    """Tool Settings API."""

    @staticmethod
    def _api_upsert_settings(client, key, value, expected_status_code=200):
        response = client.post(
            '/api/tool_setting/upsert',
            content_type='application/json',
            data=json.dumps({'key': key, 'value': value}),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Rejects anonymous user."""
        self._api_upsert_settings(
            client,
            key=f'KEY_{datetime.now().timestamp()}',
            value='The sun goes down and the world goes dancing',
            expected_status_code=401,
        )

    def test_not_authorized(self, advisor_session, client):
        """Rejects non-admin user."""
        self._api_upsert_settings(
            client,
            key=f'KEY_{datetime.now().timestamp()}',
            value='Abigail, Belle of Kilronan',
            expected_status_code=401,
        )

    def test_tool_setting_upsert(self, admin_session, client):
        """Create new tool setting."""
        key = f'KEY_SNAKE_CASE'
        value = 'Papa was a rodeo'
        api_json = self._api_upsert_settings(client, key=key, value=value)
        assert api_json['keySnakeCase'] == value
        settings = ToolSetting.get_tool_settings([key])
        assert len(settings) == 1
        assert settings[0].key == key
        assert settings[0].value == value
        assert settings[0].is_public is False


def _create(is_public=False):
    now = datetime.now().timestamp()
    return ToolSetting.upsert(
        key=f'KEY_{now}',
        value=f'value-{now}',
        is_public=is_public,
    )
