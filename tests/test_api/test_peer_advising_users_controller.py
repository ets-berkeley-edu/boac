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
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember

coe_mech_peer_advisor_manager_uid = '1133399'
coe_student = {'sid': '9000000000', 'uid': '300847'}
ce3_eop_peer_advisor_manager_uid = '3535'
ce3_navcal_peer_advisor_manager_uid = '2525'
ce3_navcal_peer_advisor_uid = '1133400'
qcadv_advisor_uid = '53791'


class TestGetBasicStudent:

    @classmethod
    def _api_get_basic_student(
            cls,
            client,
            sid,
            expected_status_code=200,
    ):
        response = client.get(f'/api/peer_advising/student/{sid}')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Rejects all users except Peer Advisors and Admins."""
        for uid in (None, qcadv_advisor_uid):
            if uid:
                fake_auth.login(uid)
            self._api_get_basic_student(
                client,
                expected_status_code=401,
                sid=coe_student['sid'],
            )

    def test_authorized(self, client, fake_auth):
        """Peer Advisor can fetch very limited student data."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        sid = coe_student['sid']
        api_json = self._api_get_basic_student(client=client, sid=sid)
        assert api_json['firstName']
        assert api_json['lastName']
        assert api_json['sid'] == sid
        assert api_json['uid']


class TestGetPeerAdvisingDepartment:

    @classmethod
    def _api_get_peer_advising_department(
            cls,
            client,
            peer_advising_department_id,
            role_type,
            expected_status_code=200,
            include_note_counts=False,
    ):
        url = f'/api/peer_advising/department/{peer_advising_department_id}/{role_type}'
        if include_note_counts:
            url += '?includeNoteCounts=true'
        response = client.get(url)
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_get_peer_advising_department(
            client,
            expected_status_code=401,
            peer_advising_department_id=1,
            role_type='peer_advisor',
        )

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 if user is neither admin nor Peer Advising Manager."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_peer_advising_department(
            client,
            expected_status_code=401,
            peer_advising_department_id=1,
            role_type='peer_advisor',
        )

    def test_authorized(self, client, fake_auth):
        """Delivers peer_advising_department data to authorized user."""
        user_profile = fake_auth.login(coe_mech_peer_advisor_manager_uid)
        departments = user_profile['departments']
        assert len(departments) == 1
        peer_advisor_manager = next((m for m in departments[0]['memberships'] if m['role'] == 'peer_advisor_manager'), None)
        assert peer_advisor_manager
        api_json = self._api_get_peer_advising_department(
            client=client,
            include_note_counts=True,
            peer_advising_department_id=2,
            role_type='peer_advisor',
        )
        assert api_json['name']
        department_members = api_json['peerAdvisingDepartmentMembers']
        assert len(department_members)
        for member in department_members:
            assert member['noteCount'] > -1


class TestDeleteAndRestore:

    @classmethod
    def setup_class(cls):
        cls.ce3_navcal_peer_advisor_user_id = AuthorizedUser.get_id_per_uid(ce3_navcal_peer_advisor_uid)
        # Get Peer Advising department ID
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(cls.ce3_navcal_peer_advisor_user_id)
        cls.ce3_navcal_peer_advising_dept_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_delete_peer_advisor(cls, client, peer_advising_department_id, user_id, expected_status_code=200):
        response = client.delete(f'/api/peer_advising/delete_peer_advisor/{peer_advising_department_id}/{user_id}')
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_restore_peer_advisor(cls, client, peer_advising_department_id, user_id, expected_status_code=200):
        response = client.get(f'/api/peer_advising/restore_peer_advisor/{peer_advising_department_id}/{user_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_delete_peer_advisor(
            client,
            expected_status_code=401,
            peer_advising_department_id=self.ce3_navcal_peer_advising_dept_id,
            user_id=self.ce3_navcal_peer_advisor_user_id,
        )
        self._api_restore_peer_advisor(
            client,
            expected_status_code=401,
            peer_advising_department_id=self.ce3_navcal_peer_advising_dept_id,
            user_id=self.ce3_navcal_peer_advisor_user_id,
        )

    def test_unauthorized(self, client, fake_auth):
        """COENG Peer Advisor Mgr cannot delete CE3 Peer Advisor."""
        fake_auth.login(coe_mech_peer_advisor_manager_uid)
        self._api_delete_peer_advisor(
            client,
            expected_status_code=401,
            peer_advising_department_id=self.ce3_navcal_peer_advising_dept_id,
            user_id=self.ce3_navcal_peer_advisor_user_id,
        )
        self._api_restore_peer_advisor(
            client,
            expected_status_code=401,
            peer_advising_department_id=self.ce3_navcal_peer_advising_dept_id,
            user_id=self.ce3_navcal_peer_advisor_user_id,
        )

    def test_authorized(self, client, fake_auth):
        """CE3 Peer Advisor Manager is authorized to delete CE3 Peer Advisor."""
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        peer_advisor_user_id = self.ce3_navcal_peer_advisor_user_id
        self._api_delete_peer_advisor(
            client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_dept_id,
            user_id=peer_advisor_user_id,
        )
        assert not PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
            authorized_user_id=peer_advisor_user_id,
        )
        self._api_restore_peer_advisor(
            client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_dept_id,
            user_id=peer_advisor_user_id,
        )
        peer_advising_memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
            authorized_user_id=peer_advisor_user_id,
        )
        assert len(peer_advising_memberships) == 1
        membership = peer_advising_memberships[0]
        assert membership['authorized_user_id'] == peer_advisor_user_id
        assert membership['peer_advising_department_id'] == self.ce3_navcal_peer_advising_dept_id
