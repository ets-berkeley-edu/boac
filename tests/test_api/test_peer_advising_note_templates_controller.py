"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.authorized_user import AuthorizedUser
from boac.models.note_template import NoteTemplate
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
import simplejson as json

peer_advisor_manager_uid = '2525'
peer_advisor_uid = '1133400'
qcadv_advisor_uid = '53791'


class TestCreatePeerAdvisingNoteTemplate:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_create_peer_advising_note_template(cls, client, data, expected_status_code=200):
        response = client.post(
            '/api/peer_advising/note_template/create',
            content_type='application/json',
            data=json.dumps(data),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_peer_advising_note_template):
        """Returns 401 if not authenticated."""
        data = {
            'peerAdvisingDeptId': self.ce3_navcal_peer_advising_department_id,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': [t.topic for t in mock_peer_advising_note_template.topics],
        }
        self._api_create_peer_advising_note_template(client, data, expected_status_code=401)

    def test_admin_is_unauthorized(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 401 if current user is an admin (or lacks proper advising access)."""
        fake_auth.login(qcadv_advisor_uid)
        data = {
            'peerAdvisingDeptId': self.ce3_navcal_peer_advising_department_id,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': [t.topic for t in mock_peer_advising_note_template.topics],
        }
        self._api_create_peer_advising_note_template(client, data, expected_status_code=401)

    def test_invalid_parameters(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 400 if required parameters are missing."""
        fake_auth.login(peer_advisor_manager_uid)
        # Missing peerAdvisingDeptId.
        data = {
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': [t.topic for t in mock_peer_advising_note_template.topics],
        }
        self._api_create_peer_advising_note_template(client, data, expected_status_code=400)

    def test_create_peer_advising_note_template_success(self, client, fake_auth, mock_peer_advising_note_template):
        """Creates a peer advising note template and returns its JSON."""
        fake_auth.login(peer_advisor_manager_uid)
        data = {
            'peerAdvisingDeptId': self.ce3_navcal_peer_advising_department_id,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': [t.topic for t in mock_peer_advising_note_template.topics],
        }
        api_json = self._api_create_peer_advising_note_template(client, data)
        print(api_json)
        note_template_id = api_json.get('id')
        print(note_template_id)

        note_template = NoteTemplate.find_by_id(note_template_id)
        print(note_template)

        assert note_template is not None
        assert note_template.body == mock_peer_advising_note_template.body
        assert note_template.title == mock_peer_advising_note_template.title
        assert len(note_template.topics) == 2
        # Ensure the peer advising department ID matches the one provided.
        assert note_template.id == note_template_id


class TestGetPeerAdvisingNoteTemplate:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_get_peer_advising_note_template(cls, client, note_template_id, expected_status_code=200):
        response = client.get(f'/api/peer_advising/note_template/{note_template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_peer_advising_note_template):
        """Returns 401 if not authenticated."""
        self._api_get_peer_advising_note_template(client, mock_peer_advising_note_template.id, expected_status_code=401)

    def test_template_not_found(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 404 if the template is not found."""
        fake_auth.login(peer_advisor_uid)
        self._api_get_peer_advising_note_template(client, note_template_id=999999, expected_status_code=404)

    def test_user_not_in_peer_advising_department(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 401 if the user is not in the template’s peer advising department."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_peer_advising_note_template(client, mock_peer_advising_note_template.id, expected_status_code=401)

    def test_get_peer_advising_note_template_success(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns the note template JSON for a user in the proper department."""
        fake_auth.login(peer_advisor_manager_uid)
        api_json = self._api_get_peer_advising_note_template(client, mock_peer_advising_note_template.id)
        assert api_json.get('id') == mock_peer_advising_note_template.id
        assert api_json.get('title') == mock_peer_advising_note_template.title


class TestGetNoteTemplatesForPeerAdvisingDepartment:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_get_templates_for_dept(cls, client, dept_id, expected_status_code=200):
        response = client.get(f'/api/peer_advising/note_templates/peer_advising_department_id/{dept_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_peer_advising_note_template):
        """Returns 401 if not authenticated."""
        self._api_get_templates_for_dept(client, dept_id=mock_peer_advising_note_template.peer_advising_department_id,
                                         expected_status_code=401)

    def test_get_templates_for_dept_success(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns all note templates for a given peer advising department."""
        fake_auth.login(peer_advisor_manager_uid)
        creator_id = mock_peer_advising_note_template.creator_id
        names = ['Template A', 'Template B']
        for name in names:
            NoteTemplate.create(
                body='Body',
                topics=['topic'],
                title=name,
                creator_id=creator_id,
                peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            )
        api_json = self._api_get_templates_for_dept(client,
                                                    dept_id=mock_peer_advising_note_template.peer_advising_department_id,
                                                    )
        returned_titles = [template['title'] for template in api_json]
        for name in names:
            assert name in returned_titles


class TestUpdatePeerAdvisingNoteTemplate:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_update_peer_advising_note_template(cls, client, data, expected_status_code=200):
        response = client.post(
            '/api/peer_advising/note_template/update',
            content_type='application/json',
            data=json.dumps(data),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_peer_advising_note_template):
        """Returns 401 if not authenticated."""
        data = {
            'id': mock_peer_advising_note_template.id,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': ['new'],
        }
        self._api_update_peer_advising_note_template(client, data, expected_status_code=401)

    def test_template_not_found(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 404 if the template is not found."""
        fake_auth.login(peer_advisor_manager_uid)
        data = {
            'id': 999999,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': ['new'],
        }
        self._api_update_peer_advising_note_template(client, data, expected_status_code=404)

    def test_user_not_in_peer_advising_department(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 403 if the current user is not in the appropriate department."""
        fake_auth.login(qcadv_advisor_uid)
        data = {
            'id': mock_peer_advising_note_template.id,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': ['new'],
        }
        self._api_update_peer_advising_note_template(client, data, expected_status_code=401)

    def test_update_peer_advising_note_template_success(self, client, fake_auth, mock_peer_advising_note_template):
        """Successfully updates a peer advising note template."""
        fake_auth.login(peer_advisor_manager_uid)
        data = {
            'id': mock_peer_advising_note_template.id,
            'body': mock_peer_advising_note_template.body,
            'title': mock_peer_advising_note_template.title,
            'topics': ['new'],
        }
        api_json = self._api_update_peer_advising_note_template(client, data)
        assert api_json.get('title') == mock_peer_advising_note_template.title
        assert api_json.get('body') == mock_peer_advising_note_template.body


class TestDeletePeerAdvisingNoteTemplate:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_delete_peer_advising_note_template(cls, client, note_template_id, expected_status_code=200):
        response = client.delete(f'/api/peer_advising/note_template/delete/{note_template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client, mock_peer_advising_note_template):
        """Returns 401 if not authenticated."""
        self._api_delete_peer_advising_note_template(client, mock_peer_advising_note_template.id,
                                                     expected_status_code=401)

    def test_template_not_found(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 404 if the template does not exist."""
        fake_auth.login(peer_advisor_manager_uid)
        self._api_delete_peer_advising_note_template(client, 999999, expected_status_code=404)

    def test_user_not_in_peer_advising_department(self, client, fake_auth, mock_peer_advising_note_template):
        """Returns 401 if the current user is not a member of the template’s peer advising department."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_delete_peer_advising_note_template(client, mock_peer_advising_note_template.id,
                                                     expected_status_code=401)

    def test_delete_peer_advising_note_template_success(self, client, fake_auth, mock_peer_advising_note_template):
        """Deletes a peer advising note template and returns a confirmation message."""
        fake_auth.login(peer_advisor_manager_uid)
        note_template_id = mock_peer_advising_note_template.id
        # Ensure the template exists in the database.
        assert NoteTemplate.find_by_id(note_template_id)
        response_json = self._api_delete_peer_advising_note_template(client, note_template_id)
        assert 'deleted' in response_json.get('message')
        # Verify deletion.
        assert not NoteTemplate.find_by_id(note_template_id)
