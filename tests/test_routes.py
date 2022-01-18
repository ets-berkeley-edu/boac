"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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


class TestFrontEndRoute:

    def test_front_end_route(self, app, client, asc_advisor_session):
        """No server-side redirect if Vue code is bundled in deployment (AWS environment)."""
        with override_config(app, 'VUE_LOCALHOST_BASE_URL', None):
            response = client.get('/student/123?r=1')
            assert response.status_code == 200

    def test_front_end_route_redirect(self, app, client, asc_advisor_session):
        """Server-side redirect to Vue.js (separate port) on developer workstation."""
        vue_path = '/student/12345?r=1'
        vue_base_url = 'http://localhost:8080'
        with override_config(app, 'VUE_LOCALHOST_BASE_URL', vue_base_url):
            response = client.get(vue_path)
            assert response.status_code == 302
            assert response.location == vue_base_url + vue_path
