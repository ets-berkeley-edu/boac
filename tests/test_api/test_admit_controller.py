"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from flask import current_app as app
import pytest
from tests.util import override_config

admin_uid = '2040'
asc_advisor_id = '1081940'
ce3_advisor_id = '2525'


@pytest.fixture()
def admin_login(fake_auth):
    fake_auth.login(admin_uid)


@pytest.fixture()
def asc_advisor_login(fake_auth):
    fake_auth.login(asc_advisor_id)


@pytest.fixture()
def ce3_advisor_login(fake_auth):
    fake_auth.login(ce3_advisor_id)


@pytest.mark.usefixtures('db_session')
class TestAdmitBySid:
    """Admit by SID API."""

    @classmethod
    def _api_admit_by_sid(cls, client, sid, expected_status_code=200):
        response = client.get(f'/api/admit/by_sid/{sid}')
        assert response.status_code == expected_status_code
        return response.json

    admit_sid = '00005852'

    def test_admit_by_sid_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            self._api_admit_by_sid(client=client, sid=self.admit_sid, expected_status_code=401)

    def test_admit_by_sid_feature_flag(self, client, ce3_advisor_login):
        """Returns 404 if feature flag is false."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            self._api_admit_by_sid(client=client, sid=self.admit_sid, expected_status_code=401)

    def test_admit_by_sid_non_ce3_advisor(self, client, asc_advisor_login):
        """Returns 401 if user is a non-CE3 advisor."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            self._api_admit_by_sid(client=client, sid=self.admit_sid, expected_status_code=401)

    def test_admit_by_sid_ce3_advisor(self, client, ce3_advisor_login):
        """Returns admit data if user is a CE3 advisor."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            response = self._api_admit_by_sid(client=client, sid=self.admit_sid)
            assert response['sid'] == self.admit_sid


@pytest.mark.usefixtures('db_session')
class TestAllAdmits:
    """All Admits API."""

    @classmethod
    def _api_all_admits(cls, client, expected_status_code=200):
        response = client.get('/api/admits/all')
        assert response.status_code == expected_status_code
        return response.json

    def test_all_admits_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            self._api_all_admits(client=client, expected_status_code=401)

    def test_all_admits_feature_flag(self, client, ce3_advisor_login):
        """Returns 404 if feature flag is false."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', False):
            self._api_all_admits(client=client, expected_status_code=401)

    def test_all_admits_non_ce3_advisor(self, client, asc_advisor_login):
        """Returns 401 if user is a non-CE3 advisor."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            self._api_all_admits(client=client, expected_status_code=401)

    def test_all_admits_ce3_advisor(self, client, ce3_advisor_login):
        """Returns admit data if user is a CE3 advisor."""
        with override_config(app, 'FEATURE_FLAG_ADMITTED_STUDENTS', True):
            response = self._api_all_admits(client=client)
            assert len(response['students']) == 3
            assert response['totalStudentCount'] == 3
