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

import json

from boac import std_commit
from boac.lib.berkeley import get_dept_codes
from boac.models.authorized_user import AuthorizedUser
from boac.models.degree_progress_template import DegreeProgressTemplate
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
import pytest


admin_uid = '2040'
coe_advisor_no_access_uid = '90412'
coe_advisor_read_only_uid = '6972201'
coe_advisor_read_write_uid = '1133399'
coe_student_sid = '9000000000'
qcadv_advisor_uid = '53791'


@pytest.fixture()
def mock_degree_check():
    user_id = AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid)
    parent_template = DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=user_id,
        degree_name='Zoology BS 2021',
    )
    degree_check = DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=user_id,
        degree_name='Zoology BS 2021',
        parent_template_id=parent_template.id,
        student_sid=coe_student_sid,
    )
    std_commit(allow_test_environment=True)
    yield degree_check
    # Avoid polluting other tests
    DegreeProgressTemplate.delete(degree_check.id)
    std_commit(allow_test_environment=True)


@pytest.fixture()
def mock_template():
    return DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid),
        degree_name='Zoology BS 2021',
    )


@pytest.fixture()
def mock_unit_requirement():
    template = DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid),
        degree_name='Ursinology 2025',
    )
    return DegreeProgressUnitRequirement.create(
        created_by=AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid),
        min_units=16,
        name='Aureum Ursi',
        template_id=template.id,
    )


class TestCloneDegreeTemplate:
    """Clone degree template API."""

    @classmethod
    def _api_clone_template(cls, client, name, template_id, expected_status_code=200):
        response = client.post(
            f'/api/degree/{template_id}/clone',
            data=json.dumps({'name': name}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_clone_template(client, name='Soulsonic Force', template_id=1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_clone_template(client, name='Space is the place', template_id=1, expected_status_code=401)

    def test_update_template(self, client, fake_auth):
        """Authorized user can edit a template."""
        user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(user.uid)

        template = DegreeProgressTemplate.create(
            advisor_dept_codes=get_dept_codes(user),
            created_by=user.id,
            degree_name='Boogie Down Productions',
        )
        for index in (1, 2, 3):
            DegreeProgressUnitRequirement.create(
                created_by=user.id,
                min_units=index,
                name=f'Unit Requirement #{index}',
                template_id=template.id,
            )

        updated_name = 'KRS One'
        api_json = self._api_clone_template(client=client, name=updated_name, template_id=template.id)
        assert api_json['id'] != template.id
        assert api_json['name'] == updated_name
        assert len(api_json['unitRequirements']) == 3

    def test_error_if_duplicate_name(self, client, fake_auth):
        """Template names must be unique."""
        fake_auth.login(coe_advisor_read_write_uid)
        name = 'Good artists copy, great artists clone.'
        api_json = _api_create_template(client, name=name)
        std_commit(allow_test_environment=True)
        template_id = api_json['id']
        # Try to clone using the same name, case-insensitive
        api_json = self._api_clone_template(
            client=client,
            expected_status_code=400,
            name=name.lower(),
            template_id=template_id,
        )
        assert 'already exists' in api_json['message']


class TestCreateDegreeTemplate:
    """Degree Progress Template Creation."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_create_template(client, name='Interstellar Overdrive', expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        _api_create_template(client, name='Space is the place', expected_status_code=401)

    def test_create_template(self, client, fake_auth):
        """Authorized user can create a template."""
        user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(user.uid)
        name = 'She Divines Water'
        api_json = _api_create_template(client=client, name=name)
        assert 'id' in api_json
        assert api_json['name'] == name
        assert api_json['createdBy'] == user.id
        assert api_json['updatedBy'] == user.id

    def test_error_if_duplicate_name(self, client, fake_auth):
        """Template names must be unique."""
        fake_auth.login(coe_advisor_read_write_uid)
        name = 'Oops, I did it again!'
        api_json = _api_create_template(client=client, name=name)
        assert api_json['name'] == name
        # Try again with same name and expect error.
        api_json = _api_create_template(client=client, name=name, expected_status_code=400)
        assert 'already exists' in api_json['message']


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


class TestGetDegreeTemplate:
    """Get Degree Template."""

    @classmethod
    def _api_get_template(cls, client, template_id, expected_status_code=200):
        response = client.get(f'/api/degree/{template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client, mock_template):
        """Denies anonymous user."""
        self._api_get_template(client, mock_template.id, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_template):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_template(client, mock_template.id, expected_status_code=401)

    def test_authorized(self, client, fake_auth, mock_template):
        """Authorized user can get a template."""
        fake_auth.login(coe_advisor_read_only_uid)
        template = self._api_get_template(client, mock_template.id)
        assert template
        assert template['id'] == mock_template.id
        assert template['parentTemplateId'] is None
        assert template['unitRequirements'] == []

    def test_student_degree_check(self, client, fake_auth, mock_degree_check):
        """Student degree check includes parent template's id and last updated."""
        fake_auth.login(coe_advisor_read_only_uid)
        template = self._api_get_template(client, mock_degree_check.id)
        assert template
        assert template['id'] == mock_degree_check.id
        assert template['parentTemplateId']
        assert template['parentTemplateUpdatedAt']


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
        # Assert response.status_code is 200
        self._api_get_templates(client)

    def test_get_master_templates(self, client, fake_auth):
        """Returns a list of nondeleted master templates."""
        fake_auth.login(coe_advisor_read_write_uid)
        _api_create_template(client=client, name='Classical Civilizations')
        _api_create_template(client=client, name='Dutch Studies')
        api_json = _api_create_template(client=client, name='Peace & Conflict Studies')
        assert client.delete(f"/api/degree/{api_json['id']}").status_code == 200

        def _is_present(name):
            template = next((row for row in api_json if row['name'] == name), None)
            return template is not None

        api_json = self._api_get_templates(client)
        assert _is_present('Classical Civilizations')
        assert _is_present('Dutch Studies')
        assert not _is_present('Peace & Conflict Studies')


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
            content_type='application/json',
            data=json.dumps(data),
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

    def test_advisor_no_permission(self, client, mock_template, fake_auth):
        """Returns 401 if user has no degree progress permission."""
        fake_auth.login(coe_advisor_no_access_uid)
        self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Ecology Units',
            min_units=24,
            expected_status_code=401,
        )

    def test_advisor_read_only_permission(self, client, mock_template, fake_auth):
        """Returns 401 if user has read-only degree progress permission."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_add_unit_requirement(
            client,
            template_id=mock_template.id,
            name='Wildlife Management Units',
            min_units=22,
            expected_status_code=401,
        )

    def test_advisor_read_write_permission(self, client, mock_template, fake_auth):
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
        assert unit_requirement.get('minUnits') == 12
        assert unit_requirement.get('templateId') == str(mock_template.id)

    def test_admin(self, client, mock_template, fake_auth):
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
        assert unit_requirement.get('minUnits') == 10
        assert unit_requirement.get('templateId') == str(mock_template.id)

    def test_add_to_nonexistent_template(self, client, fake_auth):
        """Returns 404 if template_id doesn't exist."""
        fake_auth.login(coe_advisor_read_write_uid)
        self._api_add_unit_requirement(
            client,
            template_id=666,
            name='Botany Units',
            min_units=17,
            expected_status_code=404,
        )


class TestDeleteUnitRequirement:
    """Degree Progress Unit Requirement Deletion."""

    @classmethod
    def _api_delete_unit_requirement(cls, client, unit_requirement_id, expected_status_code=200):
        response = client.delete(f'/api/degree/unit_requirement/{unit_requirement_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_unit_requirement):
        """Returns 401 if not authenticated."""
        self._api_delete_unit_requirement(client, mock_unit_requirement.id, expected_status_code=401)

    def test_advisor_no_permission(self, client, mock_unit_requirement, fake_auth):
        """Returns 401 if user has no degree progress permission."""
        fake_auth.login(coe_advisor_no_access_uid)
        self._api_delete_unit_requirement(client, mock_unit_requirement.id, expected_status_code=401)

    def test_advisor_read_only_permission(self, client, mock_unit_requirement, fake_auth):
        """Returns 401 if user has read-only degree progress permission."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_delete_unit_requirement(client, mock_unit_requirement.id, expected_status_code=401)

    def test_advisor_read_write_permission(self, client, mock_unit_requirement, fake_auth):
        """Deletes unit requirement if user has read-write degree progress permission."""
        fake_auth.login(coe_advisor_read_write_uid)
        response = self._api_delete_unit_requirement(client, mock_unit_requirement.id)
        assert response
        assert response.get('message') == f'Unit requirement {mock_unit_requirement.id} deleted'

    def test_admin(self, client, mock_unit_requirement, fake_auth):
        """Deletes unit requirement if user is admin."""
        fake_auth.login(admin_uid)
        response = self._api_delete_unit_requirement(client, mock_unit_requirement.id)
        assert response
        assert response.get('message') == f'Unit requirement {mock_unit_requirement.id} deleted'


class TestUpdateDegreeTemplate:
    """Update degree template API."""

    @classmethod
    def _api_update_template(cls, client, name, template_id, expected_status_code=200):
        response = client.post(
            f'/api/degree/{template_id}/update',
            data=json.dumps({'name': name}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_update_template(client, name='Soulsonic Force', template_id=1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_update_template(client, name='Space is the place', template_id=1, expected_status_code=401)

    def test_update_template(self, client, fake_auth):
        """Authorized user can edit a template."""
        fake_auth.login(coe_advisor_read_write_uid)
        name = 'Afrika Bambaataa'
        api_json = _api_create_template(client, name=name)
        template_id = api_json['id']
        assert api_json['name'] == name

        name = 'Renegades of Funk'
        api_json = self._api_update_template(client=client, name=name, template_id=template_id)
        assert api_json['id'] == template_id
        assert api_json['name'] == name

    def test_error_if_duplicate_name(self, client, fake_auth):
        """Template names must be unique."""
        fake_auth.login(coe_advisor_read_write_uid)
        name = 'I like pie.'
        _api_create_template(client=client, name=name)

        api_json = _api_create_template(client=client, name='I like cake.')
        template_id = api_json['id']

        # Reuse the name and expect an error
        api_json = self._api_update_template(
            client=client,
            expected_status_code=400,
            name=name.lower(),
            template_id=template_id,
        )
        assert 'already exists' in api_json['message']


class TestUpdateUnitRequirement:
    """Update unit requirement API."""

    @classmethod
    def _api_update_unit_requirement(cls, client, mock, name=None, min_units=None, expected_status_code=200):
        response = client.post(
            f'/api/degree/unit_requirement/{mock.id}/update',
            data=json.dumps({
                'name': name or mock.name,
                'minUnits': min_units or mock.min_units,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_unit_requirement):
        """Denies anonymous user."""
        self._api_update_unit_requirement(client, mock_unit_requirement, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_unit_requirement):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_update_unit_requirement(client, mock_unit_requirement, expected_status_code=401)

        fake_auth.login(coe_advisor_read_only_uid)
        self._api_update_unit_requirement(client, mock_unit_requirement, expected_status_code=401)

    def test_advisor_read_write_permission(self, client, fake_auth, mock_unit_requirement):
        """Authorized user can edit a unit requirement."""
        fake_auth.login(coe_advisor_read_write_uid)
        min_units = 10
        name = 'χρυσή αρκούδα'
        api_json = self._api_update_unit_requirement(client, mock_unit_requirement, min_units=min_units, name=name)
        assert api_json['id'] == mock_unit_requirement.id
        assert api_json['name'] == name
        assert api_json['minUnits'] == min_units

    def test_admin(self, client, fake_auth, mock_unit_requirement):
        """Admin can edit a unit requirement."""
        fake_auth.login(admin_uid)
        min_units = 15
        api_json = self._api_update_unit_requirement(client, mock_unit_requirement, min_units=min_units)
        assert api_json['id'] == mock_unit_requirement.id
        assert api_json['name'] == mock_unit_requirement.name
        assert api_json['minUnits'] == min_units


def _api_create_template(client, name, expected_status_code=200):
    response = client.post(
        '/api/degree/create',
        data=json.dumps({'name': name}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return json.loads(response.data)
