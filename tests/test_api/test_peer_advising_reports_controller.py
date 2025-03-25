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

ce3_navcal_peer_advisor_manager_uid = '2525'
l_s_advisor_uid = '188242'
l_s_director_uid = '53791'


class TestPeerAdvisingNotesReport:

    @classmethod
    def _api_notes_report(cls, client, peer_advising_department_id, expected_status_code=200):
        response = client.get(f'/api/peer_advising/{peer_advising_department_id}/report/notes')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_notes_report(client, 1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 if user is neither admin nor peer_advisor_manager."""
        for uid in [None, l_s_advisor_uid, l_s_director_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_notes_report(client, 1, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Admin user can access L&S report."""
        uid = ce3_navcal_peer_advisor_manager_uid
        user_id = AuthorizedUser.get_id_per_uid(uid)
        fake_auth.login(uid)
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=user_id)
        peer_advising_department_id = memberships[0]['peer_advising_department_id']
        api_json = self._api_notes_report(client, peer_advising_department_id)
        assert api_json['distinctPeerAdvisorAuthors'] >= 0
        assert 'noteTemplates' in api_json
        assert api_json['peerAdvisingDepartment']['name'] == 'NAVCAL'
        assert api_json['totalPeerAdvisingNoteCount'] >= 0
