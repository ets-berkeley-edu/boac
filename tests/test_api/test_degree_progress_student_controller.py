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

from datetime import datetime
import json

from boac.models.authorized_user import AuthorizedUser
from boac.models.degree_progress_template import DegreeProgressTemplate
import pytest

coe_advisor_read_only_uid = '6972201'
coe_advisor_read_write_uid = '1133399'
coe_student_sid = '9000000000'
qcadv_advisor_uid = '53791'


@pytest.fixture()
def mock_degree_checks():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    marker = datetime.now().timestamp()
    degree_checks = []
    for index in (1, 2, 3):
        degree_checks.append(
            DegreeProgressTemplate.create(
                advisor_dept_codes=['COENG'],
                created_by=user.id,
                degree_name=f'I am a mock template, made for a mock category ({marker}_{index})',
                student_sid=coe_student_sid,
            ),
        )
    return degree_checks


@pytest.fixture()
def mock_template():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    marker = datetime.now().timestamp()
    return DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=user.id,
        degree_name=f'I am a mock template, made for a mock category ({marker})',
    )


class TestCreateStudentDegreeCheck:

    @classmethod
    def _api_create_degree_check(
            cls,
            client,
            sid,
            template_id,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/degree/check/{sid}/create',
            data=json.dumps({'templateId': template_id}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_degree_check(client, sid=coe_student_sid, template_id=1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_create_degree_check(client, sid=coe_student_sid, template_id=1, expected_status_code=401)

    def test_create_category(self, client, fake_auth, mock_template):
        """Authorized user can create a degree check."""
        fake_auth.login(coe_advisor_read_write_uid)
        api_json = self._api_create_degree_check(client, sid=coe_student_sid, template_id=mock_template.id)
        assert api_json['id']


class TestGetStudentDegreeChecks:

    @classmethod
    def _api_get_degree_checks(cls, client, sid, expected_status_code=200):
        response = client.get(f'/api/degrees/student/{sid}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_degree_checks(client, sid=coe_student_sid, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_degree_checks(client, sid=coe_student_sid, expected_status_code=401)

    def test_authorized(self, client, fake_auth, mock_degree_checks, app):
        """Authorized user can get student degree checks."""
        fake_auth.login(coe_advisor_read_only_uid)

        def _sort_by(item):
            return item.updated_at
        mock_degree_checks.sort(key=_sort_by, reverse=True)
        expected_current_id = mock_degree_checks[0].id

        degree_checks = self._api_get_degree_checks(client, sid=coe_student_sid)
        assert len(degree_checks) == 3
        assert degree_checks[0]['id'] == expected_current_id
        assert degree_checks[0]['isCurrent'] is True
        assert degree_checks[1]['isCurrent'] is False
        assert degree_checks[2]['isCurrent'] is False
