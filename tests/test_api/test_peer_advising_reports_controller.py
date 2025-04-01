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
from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_topic import NoteTopic
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember

ce3_advisor_uid = '5405613'
ce3_navcal_peer_advisor_manager_uid = '2525'
ce3_navcal_peer_advisor_uid = '1133400'
coe_mech_peer_advisor_manager_uid = '1133399'
coe_mech_peer_advisor_uid = '1913062'
l_s_advisor_uid = '188242'
l_s_director_uid = '53791'


class TestPeerAdvisingDownloadCSV:

    @classmethod
    def _api_peer_advising_csv_download(cls, client, peer_advising_department_id, uid, expected_status_code=200):
        response = client.post(f'/api/peer_advising/{peer_advising_department_id}/notes/csv')
        assert response.status_code == expected_status_code, f'Failed during user session of UID {uid}'
        return response

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 if user is not a Peer Advisor Manager in the designated peer_advising_department."""
        peer_advisor = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        ce3_peer_advising_department_id = PeerAdvisingDepartmentMember.get_peer_advising_department_membership(
            role_type='peer_advisor',
            user_id=peer_advisor.id,
        ).peer_advising_department_id

        for uid in [None, ce3_advisor_uid, l_s_advisor_uid, coe_mech_peer_advisor_manager_uid]:
            if uid:
                profile = fake_auth.login(uid)
                assert not profile['isAdmin']
            self._api_peer_advising_csv_download(
                client,
                expected_status_code=401,
                peer_advising_department_id=ce3_peer_advising_department_id,
                uid=uid,
            )

    def test_authorized(self, client, fake_auth):
        """Peer Advising report is available only to authorized Peer Advising Managers."""
        def _get_peer_advising_department(role_type, uid):
            peer_advising_department_id = PeerAdvisingDepartmentMember.get_peer_advising_department_membership(
                role_type=role_type,
                user_id=AuthorizedUser.get_id_per_uid(uid),
            ).peer_advising_department_id
            return PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)

        # Look up Peer Advising department IDs
        ce3_peer_advising_department = _get_peer_advising_department(
            role_type='peer_advisor',
            uid=ce3_navcal_peer_advisor_uid,
        )
        ce3_peer_advising = {
            'dept_code': 'ZCEEE',
            'peer_advising_department_id': ce3_peer_advising_department.id,
            'peer_advisor_uid': ce3_navcal_peer_advisor_uid,
        }
        coe_peer_advising_department = _get_peer_advising_department(
            role_type='peer_advisor_manager',
            uid=coe_mech_peer_advisor_manager_uid,
        )
        coe_peer_advising = {
            'dept_code': 'COENG',
            'peer_advising_department_id': coe_peer_advising_department.id,
            'peer_advisor_uid': coe_mech_peer_advisor_uid,
        }
        # Create two dummy notes: One by CE3 peer advisor and another by CoE peer advisor.
        # We expect the CSV to contain only the former.
        notes = []
        topics = []
        for (index, peer_advising) in enumerate([ce3_peer_advising, coe_peer_advising]):
            # Verify that both the note with topics and the one without are found in the report.
            uid = peer_advising['peer_advisor_uid']
            note = Note.create(
                author_uid=uid,
                author_name=f'author_name {uid}',
                author_role=f'author_role {index}',
                author_dept_codes=[peer_advising['dept_code']],
                peer_advising_department_id=peer_advising['peer_advising_department_id'],
                sid='11667051',
                subject='',
                body=f"""
                    User {uid}'s note body has an apostrophe
                    and some line breaks.
                """,
            )
            if uid == ce3_navcal_peer_advisor_uid:
                for topic in ('Three Feet High', 'and', 'Rising'):
                    topics.append(NoteTopic.create(note=note, topic=topic, author_uid=ce3_navcal_peer_advisor_uid))
            notes.append(note)
        std_commit(allow_test_environment=True)
        # Log in as CE3 Peer Advisor Manager
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        response = self._api_peer_advising_csv_download(
            client,
            peer_advising_department_id=ce3_peer_advising_department.id,
            uid=ce3_navcal_peer_advisor_manager_uid,
        )
        assert 'csv' in response.content_type
        csv_rows = response.data.decode('UTF-8').split('\n')
        assert len(csv_rows) >= 3
        is_mock_ce3_note_present_in_csv = False
        for (index, row) in enumerate(csv_rows):
            if index == 0:
                assert 'author_name,author_uid,author_role' in row
            elif index == len(csv_rows) - 1:
                # Last line in CSV is empty
                assert row == ''
            else:
                if f'author_name {ce3_navcal_peer_advisor_uid}' in row:
                    is_mock_ce3_note_present_in_csv = True
                    assert 'Three Feet High' in row
                    assert f'author_name {ce3_navcal_peer_advisor_uid}' in row
                    assert f"User {ce3_navcal_peer_advisor_uid}'s note body has an apostrophe and some line breaks" in row
                assert ce3_peer_advising_department.name in row
        assert is_mock_ce3_note_present_in_csv


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
