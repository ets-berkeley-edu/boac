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

from boac.models.authorized_user import AuthorizedUser
from boac.models.degree_progress_template import DegreeProgressTemplate
from flask import current_app as app
import pytest
from tests.util import override_config


admin_uid = '2040'
coe_advisor_no_access_uid = '90412'
coe_advisor_read_only_uid = '6972201'
coe_advisor_read_write_uid = '1133399'
qcadv_advisor_uid = '53791'


@pytest.fixture()
def mock_template():
    return DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=AuthorizedUser.get_id_per_uid('1133399'),
        degree_name='Zoology BS 2021',
    )


class TestCreateDegreeProgressTemplate:
    """Degree Progress Template Creation."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_create_template(client, name='Interstellar Overdrive', expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        _api_create_template(client, name='Space is the place', expected_status_code=401)

    def test_create_template(self, client, fake_auth):
        """Authorized user can create an template."""
        fake_auth.login(coe_advisor_read_write_uid)
        name = 'She Divines Water'
        api_json = _api_create_template(client=client, name=name)
        assert 'id' in api_json
        assert api_json['name'] == name


class TestDeleteTemplate:
    """Delete Template API."""

    def test_not_authenticated(self, client):
        """Denies anonymous user."""
        assert client.delete('/api/degree/1').status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        assert client.delete('/api/degree/1').status_code == 401

    def test_delete(self, client, fake_auth):
        """COE advisor can delete template."""
        fake_auth.login(coe_advisor_read_write_uid)
        user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        assert user.degree_progress_permission == 'read_write'
        template = DegreeProgressTemplate.create(['COENG'], user.id, f'Classical Civilizations, by {user.id}')
        assert client.delete(f'/api/degree/{template.id}').status_code == 200
        assert client.get(f'/api/degree/{template.id}').status_code == 404


class TestGetDegreeTemplates:
    """Get Degree Templates."""

    @classmethod
    def _api_get_templates(cls, client, expected_status_code=200):
        response = client.get('/api/degree/templates')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_templates(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_templates(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Authorized user can get all templates."""
        fake_auth.login(coe_advisor_read_write_uid)
        assert self._api_get_templates(client) == []

    def test_get_master_templates(self, client, fake_auth):
        """Returns a list of nondeleted master templates."""
        # user_id = AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid)
        fake_auth.login(coe_advisor_read_write_uid)
        _api_create_template(client=client, name='Classical Civilizations')
        _api_create_template(client=client, name='Dutch Studies')
        api_json = _api_create_template(client=client, name='Peace & Conflict Studies')
        assert client.delete(f"/api/degree/{api_json['id']}").status_code == 200

        api_json = self._api_get_templates(client)

        def _is_present(name):
            template = next((row for row in api_json if row['name'] == name), None)
            return template is not None
        assert _is_present('Classical Civilizations')
        assert _is_present('Dutch Studies')
        assert not _is_present('Peace & Conflict Studies')


def _api_create_template(client, name, expected_status_code=200):
    response = client.post(
        '/api/degree/create',
        data=json.dumps({'name': name}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return json.loads(response.data)


class TestCreateUnitRequirement:
    """Degree Progress Unit Requirement Creation."""

    @classmethod
    def _api_add_unit_requirement(cls, client, template_id, name, min_units, expected_status_code=200):
        data = {
            'name': name,
            'minUnits': min_units,
        }
        response = client.post(
            f'/api/degree/{template_id}/unit_requirement',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_template):
        """Returns 401 if not authenticated."""
        self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Biology Units',
            min_units=38,
            expected_status_code=401,
        )

    def test_advisor_no_permission(self, client, mock_template, fake_auth, app):
        """Returns 401 if user has no degree progress permission."""
        fake_auth.login(coe_advisor_no_access_uid)
        self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Ecology Units',
            min_units=24,
            expected_status_code=401,
        )

    def test_advisor_read_only_permission(self, client, mock_template, fake_auth, app):
        """Returns 401 if user has read-only degree progress permission."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Wildlife Management Units',
            min_units=22,
            expected_status_code=401,
        )

    def test_advisor_read_write_permission(self, client, mock_template, fake_auth, app):
        """Returns newly created unit requirement if user has read-write degree progress permission."""
        fake_auth.login(coe_advisor_read_write_uid)
        unit_requirement = self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Anatomy Units',
            min_units=12,
            expected_status_code=200,
        )
        assert unit_requirement
        assert unit_requirement.get('name') == 'Anatomy Units'
        assert unit_requirement.get('minUnits') == '12'
        assert unit_requirement.get('templateId') == str(mock_template.id)

    def test_admin(self, client, mock_template, fake_auth, app):
        """Returns newly created unit requirement if user is admin."""
        fake_auth.login(admin_uid)
        unit_requirement = self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Chemistry Units',
            min_units=10,
            expected_status_code=200,
        )
        assert unit_requirement
        assert unit_requirement.get('name') == 'Chemistry Units'
        assert unit_requirement.get('minUnits') == '10'
        assert unit_requirement.get('templateId') == str(mock_template.id)

    def test_add_to_nonexistent_template(self, client, fake_auth, app):
        """Returns 404 if template_id doesn't exist."""
        fake_auth.login(coe_advisor_read_write_uid)
        self._api_add_unit_requirement(
            client,
            template_id=666,
            name='Botany Units',
            min_units=17,
            expected_status_code=404,
        )

    def test_feature_flag(self, client, mock_template, fake_auth):
        """Returns 401 if feature flag is False."""
        with override_config(app, 'FEATURE_FLAG_DEGREE_CHECK', False):
            fake_auth.login(coe_advisor_read_write_uid)
            self._api_add_unit_requirement(
                client,
                template_id=mock_template.id,
                name='Physics Units',
                min_units=10,
                expected_status_code=401,
            )
