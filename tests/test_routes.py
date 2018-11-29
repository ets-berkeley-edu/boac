"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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
def asc_advisor_session(fake_auth):
    fake_auth.login('1081940')


class TestVueRedirect:

    def test_vue_enabled_path(self, client, asc_advisor_session):
        """Serves Vue.js index page."""
        response = client.get('/cohort/filtered/all')
        assert response.status_code == 200
        assert 'I am a Vue.js page' in str(response.data)

    def test_path_token_replace(self, app, client, asc_advisor_session):
        """Serves Vue.js index page."""
        with override_config(app, 'VUE_LOCALHOST_BASE_URL', 'http://localhost:8080'):
            response = client.get('/student/123')
            assert response.status_code == 302
            assert response.location == 'http://localhost:8080/student_123'

    def test_non_vue_enabled_path(self, client, asc_advisor_session):
        """Serves default index page."""
        response = client.get('/home')
        assert response.status_code == 200
        assert 'I am the default index page' in str(response.data)
