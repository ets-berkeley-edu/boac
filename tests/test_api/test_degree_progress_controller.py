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

coe_advisor_uid = '1133399'
qcadv_advisor_uid = '53791'


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
        fake_auth.login(coe_advisor_uid)
        name = 'She Divines Water'
        api_json = _api_create_template(client=client, name=name)
        assert 'id' in api_json
        assert api_json['name'] == name


class TestDeleteTemplate:
    """Delete Template API."""

    def test_not_authenticated(self, client):
        """Denies anonymous user."""
        assert client.delete('/api/degree/1/delete').status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        assert client.delete('/api/degree/1/delete').status_code == 401

    def test_delete(self, client, fake_auth):
        """COE advisor can delete template."""
        fake_auth.login(coe_advisor_uid)
        user = AuthorizedUser.find_by_uid(coe_advisor_uid)
        assert user.degree_progress_permission == 'read_write'
        template = DegreeProgressTemplate.create(['COENG'], user.id, f'Classical Civilizations, by {user.id}')
        assert client.delete(f'/api/degree/{template.id}/delete').status_code == 200
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
        fake_auth.login(coe_advisor_uid)
        assert self._api_get_templates(client) == []

    def test_get_master_templates(self, client, fake_auth):
        """Returns a list of nondeleted master templates."""
        # user_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        fake_auth.login(coe_advisor_uid)
        _api_create_template(client=client, name='Classical Civilizations')
        _api_create_template(client=client, name='Dutch Studies')
        api_json = _api_create_template(client=client, name='Peace & Conflict Studies')
        assert client.delete(f"/api/degree/{api_json['id']}/delete").status_code == 200

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
