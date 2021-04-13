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

from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.degree_progress_template import DegreeProgressTemplate
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
import pytest

coe_advisor_read_only_uid = '6972201'
coe_advisor_read_write_uid = '1133399'
qcadv_advisor_uid = '53791'


@pytest.fixture()
def mock_template():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    marker = datetime.now().timestamp()
    return DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=user.id,
        degree_name=f'I am a mock template, made for a mock category ({marker})',
    )


class TestCreateDegreeCategory:
    """Degree Progress Category Creation."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_create_category(
            client,
            category_type='Category',
            name='Anonymous hack!',
            parent_category_id=1,
            position=1,
            template_id=1,
            expected_status_code=401,
        )

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        _api_create_category(
            client,
            category_type='Category',
            name='Unauthorized hack!',
            parent_category_id=1,
            position=2,
            template_id=1,
            expected_status_code=401,
        )

    def test_create_category(self, client, fake_auth, mock_template):
        """Authorized user can create a category."""
        fake_auth.login(coe_advisor_read_write_uid)
        parent = _api_create_category(
            client,
            category_type='Category',
            name='I am the sun',
            position=1,
            template_id=mock_template.id,
        )
        api_json = _api_create_category(
            client,
            category_type='Subcategory',
            name='I am the rain',
            parent_category_id=parent['id'],
            position=1,
            template_id=mock_template.id,
        )
        assert api_json['id']
        assert api_json['categoryType'] == 'Subcategory'
        assert api_json['name'] == 'I am the rain'
        assert api_json['parentCategoryId'] == parent['id']
        assert api_json['position'] == 1
        assert api_json['templateId'] == mock_template.id


class TestDeleteCategory:

    def test_not_authenticated(self, client):
        """Denies anonymous user."""
        assert client.delete('/api/degree/category/1').status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        assert client.delete('/api/degree/category/1').status_code == 401

    def test_delete(self, client, fake_auth, mock_template):
        """COE advisor can delete degree category."""
        fake_auth.login(coe_advisor_read_write_uid)
        category = _api_create_category(
            category_type='Category',
            client=client,
            name='Blister in the sun',
            position=3,
            template_id=mock_template.id,
        )
        subcategory = _api_create_category(
            category_type='Category',
            client=client,
            name='Gone Daddy Gone',
            parent_category_id=category['id'],
            position=3,
            template_id=mock_template.id,
        )
        course = _api_create_category(
            category_type='Category',
            client=client,
            name='Blister in the sun',
            parent_category_id=subcategory['id'],
            position=3,
            template_id=mock_template.id,
        )
        category_id = category['id']
        assert client.delete(f'/api/degree/category/{category_id}').status_code == 200
        # Verify that all were deleted.
        for object_id in (category_id, subcategory['id'], course['id']):
            assert client.get(f'/api/degree/category/{object_id}').status_code == 404


class TestGetTemplateWithCategory:
    """Get Degree Template API."""

    @classmethod
    def _api_get_template(cls, client, template_id, expected_status_code=200):
        response = client.get(f'/api/degree/{template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_get_template_categories(self, client, fake_auth, mock_template):
        """Authorized user can get a template and its categories."""
        user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(user.uid)
        category = _api_create_category(
            category_type='Category',
            client=client,
            description='Seeking subcategories for casual companionship.',
            name='Hot metal in the sun',
            position=3,
            template_id=mock_template.id,
        )
        subcategory = _api_create_category(
            category_type='Subcategory',
            client=client,
            name='Pony in the air',
            parent_category_id=category['id'],
            position=3,
            template_id=mock_template.id,
        )
        unit_requirement = DegreeProgressUnitRequirement.create(
            created_by=user.id,
            min_units=3,
            name='I am unit_requirement.',
            template_id=mock_template.id,
        )
        _api_create_category(
            category_type='Course',
            client=client,
            course_units=3,
            name='Sooey and saints at the fair',
            parent_category_id=subcategory['id'],
            position=3,
            template_id=mock_template.id,
            unit_requirement_ids=[unit_requirement.id],
        )
        std_commit(allow_test_environment=True)

        api_json = client.get(f'/api/degree/{mock_template.id}').json
        categories = api_json['categories']
        assert len(categories) == 1
        children = categories[0]['children']
        assert len(children) == 1
        grand_children = children[0]['children']
        assert len(grand_children) == 1
        assert grand_children[0]['courseUnits'] == 3

        unit_requirements = grand_children[0]['unitRequirements']
        assert len(unit_requirements) == 1
        assert unit_requirements[0]['id']
        assert unit_requirements[0]['name'] == 'I am unit_requirement.'


def _api_create_category(
        client,
        category_type,
        name,
        position,
        template_id,
        course_units=None,
        description=None,
        expected_status_code=200,
        parent_category_id=None,
        unit_requirement_ids=(),
):
    response = client.post(
        '/api/degree/category/create',
        data=json.dumps({
            'categoryType': category_type,
            'courseUnits': course_units,
            'description': description,
            'name': name,
            'parentCategoryId': parent_category_id,
            'position': position,
            'templateId': template_id,
            'unitRequirementIds': ','.join(str(id_) for id_ in unit_requirement_ids),
        }),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return json.loads(response.data)
