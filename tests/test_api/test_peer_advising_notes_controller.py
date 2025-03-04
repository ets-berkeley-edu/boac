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

import json

from boac.models.authorized_user import AuthorizedUser
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember

admin_uid = '2040'
ce3_advisor_uid = '2525'
ce3_navcal_peer_advisor_uid = '1133400'
ce3_navcal_peer_advisor_manager_uid = '2525'
coe_mech_peer_advisor_uid = '1913062'
coe_student_sid = '9000000000'
qcadv_advisor_uid = '53791'


class TestCreatePeerAdvisingNote:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    def test_not_authorized(self, app, client, fake_auth):
        """Returns 401 if not authorized."""
        for uid in (None, admin_uid, ce3_navcal_peer_advisor_manager_uid, qcadv_advisor_uid):
            fake_auth.login(uid)
            assert _api_create_peer_advising_note(
                body='Yes, you are not authorized.',
                client=client,
                expected_status_code=401,
                peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
                sid=coe_student_sid,
            )

    def test_invalid_peer_advising_department_id(self, client, fake_auth):
        coe_mech_peer_advisor = AuthorizedUser.find_by_uid(coe_mech_peer_advisor_uid)
        user_id = coe_mech_peer_advisor.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        # CoE peer advising dept
        coe_mech_peer_advising_department_id = memberships[0]['peer_advising_department_id']
        # Log in as CE3 peer_advisor
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        _api_create_peer_advising_note(
            body='Yes, you are not authorized.',
            client=client,
            expected_status_code=403,
            peer_advising_department_id=coe_mech_peer_advising_department_id,
            sid=coe_student_sid,
        )

    def test_authorized(self, app, client, fake_auth):
        """Create a note."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student_sid,
        )
        assert note['id']
        assert note['author']['uid'] == ce3_navcal_peer_advisor_uid
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert note['read'] is True


class TestGetPeerAdvisingNotes:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    @classmethod
    def _api_get_notes_for_peer_advisor(cls, client, include_students=False, expected_status_code=200):
        response = client.get(f'/api/peer_advisor/notes?includeStudents={include_students}')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 unless user is a Peer Advisor."""
        for uid in [None, admin_uid, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(qcadv_advisor_uid)
            self._api_get_notes_for_peer_advisor(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Delivers notes per peer_advising_department of Peer Advisor."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        # Create a note...
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student_sid,
        )
        assert note['id']
        assert note['author']['uid'] == ce3_navcal_peer_advisor_uid
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        # Fetch that note, without student.
        api_json = self._api_get_notes_for_peer_advisor(client)
        notes = api_json['notes']
        assert len(notes) > 0
        assert len(notes) == api_json['totalNoteCount']
        assert notes[0]['id'] == note['id']
        assert 'student' not in notes[0]
        # Fetch that note, with student.
        api_json = self._api_get_notes_for_peer_advisor(client, include_students=True)
        notes = api_json['notes']
        assert notes[0]['student']['sid'] == coe_student_sid


class TestGetPeerAdvisingTopics:

    @classmethod
    def _api_get_peer_advising_topics(cls, client, expected_status_code=200):
        response = client.get('/api/peer_advising/note_topics')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_get_peer_advising_topics(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 if user is neither admin nor Peer Advising Manager."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_peer_advising_topics(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Delivers peer_advising_department data to authorized user."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_get_peer_advising_topics(client)
        assert len(api_json)
        assert 'Probation' in [topic['topic'] for topic in api_json]


def _api_create_peer_advising_note(
        client,
        body,
        peer_advising_department_id,
        sid,
        subject='',
        contact_type=None,
        expected_status_code=200,
        topics=(),
):
    data = {
        'body': body,
        'contactType': contact_type,
        'peerAdvisingDepartmentId': peer_advising_department_id,
        'sid': sid,
        'subject': subject,
        'topics': ','.join(topics),
    }
    response = client.post(
        '/api/peer_advising/note/create',
        content_type='application/json',
        data=json.dumps(data),
    )
    assert response.status_code == expected_status_code
    return response.json
