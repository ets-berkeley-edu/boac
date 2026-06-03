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

from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_read import NoteRead
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from tests.util import mock_advising_note_s3_bucket

admin_uid = '2040'
asc_advisor_uid = '6446'
ce3_advisor_uid = '2525'
ce3_navcal_peer_advisor_uid = '1133400'
ce3_navcal_peer_advisor_2_uid = '188444'
ce3_navcal_peer_advisor_manager_uid = '2525'
coe_advisor_no_advising_data_uid = '1022796'
coe_mech_peer_advisor_uid = '1913062'
coe_student = {
    'sid': '9000000000',
    'uid': '300847',
}
qcadv_advisor_uid = '53791'

class TestCreatePeerAdvisingNote:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    def test_not_authorized(self, client, fake_auth):
        """Returns 401 if not authorized."""
        for uid in (None, ce3_navcal_peer_advisor_manager_uid, qcadv_advisor_uid):
            fake_auth.login(uid)
            assert _api_create_peer_advising_note(
                body='Yes, you are not authorized.',
                client=client,
                expected_status_code=401,
                peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
                sid=coe_student['sid'],
            )

    def test_peer_advisor_manager_attach_to_peer_advisor_note(self, app, client, fake_auth):
        navcal_department = PeerAdvisingDepartment.get_department_by_name('NAVCAL')
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        with mock_advising_note_s3_bucket(app):
            base_dir = app.config['BASE_DIR']
            attachment = f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'
            with open(attachment, 'r') as file:
                note = Note.create(
                    attachments=[
                        {
                            'name': attachment.rsplit('/', 1)[-1],
                            'byte_stream': file.read(),
                        },
                    ],
                    author_uid=ce3_navcal_peer_advisor_uid,
                    author_name='CE3 Peer Advisor',
                    author_role='Peer Advisor',
                    author_dept_codes=['ZCEEE'],
                    body='Rock \'n Roll rang sweet as victory, under neon signs',
                    peer_advising_department_id=navcal_department.id,
                    sid='11667051',
                    subject='',
                )
                std_commit(allow_test_environment=True)
                _api_note_attachments_upload(
                    app=app,
                    attachments=[f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'],
                    client=client,
                    note_id=note.id,
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
            sid=coe_student['sid'],
        )

    def test_authorized(self, app, client, fake_auth):
        """Create a note."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        topics = ['Enrollment: Waitlist, Swaps, etc.', 'Program Planning, Semester or Longer Term']
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student['sid'],
            topics=topics,
        )
        note_id = note['id']
        base_dir = app.config['BASE_DIR']
        note = _api_note_attachments_upload(
            app=app,
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
            client=client,
            note_id=note_id,
        )
        assert note_id
        assert note['author']['uid'] == ce3_navcal_peer_advisor_uid
        assert note['author']['departments'] == [{'deptCode': 'ZCEEE', 'deptName': 'Centers for Educational Equity and Excellence'}]
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert note['read'] is True
        # Verify that topics containing commas do not confuse server-side parsing.
        assert set(note['topics']) == set(topics)
        assert len(note.get('attachments')) == 2


class TestGetPeerAdvisingNotesAuthoredBy:

    @classmethod
    def _api_notes_authored_by(
            cls,
            client,
            peer_advising_department_id,
            uid,
            expected_status_code=200,
            timeframe=None,
    ):
        data = {
            'timeframe': timeframe,
            'peerAdvisingDepartmentId': peer_advising_department_id,
            'uid': uid,
        }
        response = client.post(
            '/api/peer_advising/notes/authored_by',
            content_type='application/json',
            data=json.dumps(data),
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 if not authenticated."""
        for uid in [None, coe_advisor_no_advising_data_uid, coe_student['uid']]:
            if uid:
                fake_auth.login(uid)
        self._api_notes_authored_by(
            client=client,
            expected_status_code=401,
            peer_advising_department_id=1,
            uid=uid,
        )

    def test_authorized(self, client, fake_auth):
        """Advisor can view notes created by another Advisor or Peer Advisor user."""
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        peer_advisor = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        peer_advising_department_id = PeerAdvisingDepartmentMember.get_peer_advising_department_membership(
            role_type='peer_advisor',
            user_id=peer_advisor.id,
        ).peer_advising_department_id
        note = Note.create(
            author_uid=peer_advisor.uid,
            peer_advising_department_id=peer_advising_department_id,
            author_name='CE3 Peer Advisor',
            author_role='Peer Advisor',
            author_dept_codes=['ZCEEE'],
            body='He spattered me with tomatoes, Hummus, chick peas',
            sid=coe_student['sid'],
            subject='',
        )
        api_json = self._api_notes_authored_by(
            client=client,
            peer_advising_department_id=peer_advising_department_id,
            uid=peer_advisor.uid,
        )
        assert len(api_json)
        assert next((n for n in api_json if n['id'] == note.id), None)
        api_json = self._api_notes_authored_by(
            client=client,
            peer_advising_department_id=peer_advising_department_id,
            timeframe={
                'year': 1999,
                'month': 12,
            },
            uid=peer_advisor.uid,
        )
        assert not len(api_json)


class TestGetPeerAdvisingNotes:

    @classmethod
    def setup_class(cls):
        # Get Peer Advising department ID
        cls.ce3_navcal_peer_advisor_user = AuthorizedUser.find_by_uid(ce3_navcal_peer_advisor_uid)
        user_id = cls.ce3_navcal_peer_advisor_user.id
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    def test_unauthorized(self, client, fake_auth):
        """Returns 401 unless user is a Peer Advisor."""
        peer_advisor_uid = coe_mech_peer_advisor_uid
        for uid in [None, qcadv_advisor_uid, ce3_navcal_peer_advisor_manager_uid]:
            if uid:
                fake_auth.login(uid)
            _api_get_notes_for_peer_advisor(
                client,
                expected_status_code=401,
                uid=peer_advisor_uid,
            )

    def test_authorized(self, client, fake_auth):
        """Delivers notes per peer_advising_department of Peer Advisor."""
        uid = ce3_navcal_peer_advisor_uid
        fake_auth.login(uid)
        # Create a note...
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student['sid'],
        )
        assert note['id']
        assert note['author']['uid'] == ce3_navcal_peer_advisor_uid
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        # Fetch that note, without student.
        api_json = _api_get_notes_for_peer_advisor(client, uid=uid)
        notes = api_json['notes']
        assert len(notes) > 0
        assert len(notes) == api_json['totalNoteCount']
        note = next((n for n in notes if n['id'] == note['id']), None)
        assert note
        assert 'student' not in note
        # Fetch that note, with student.
        api_json = _api_get_notes_for_peer_advisor(client, include_students=True, uid=uid)
        student = next((student for student in api_json['notes'] if student['sid'] == coe_student['sid']), None)
        assert student
        # Verify with BOA Admin
        fake_auth.login(admin_uid)
        _api_get_notes_for_peer_advisor(client, uid=uid)

    def test_note_access_by_department(self, client, fake_auth, mock_navcal_peer_advising_note_with_comments, mock_eop_peer_advising_note):  # noqa: ARG002
        """Peer advisor can only see notes and note comments authored by users in their department."""
        note_id = mock_navcal_peer_advising_note_with_comments.id
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = _api_get_notes_for_peer_advisor(client, uid=ce3_navcal_peer_advisor_uid)
        notes = api_json['notes']
        assert len(notes) > 0
        assert len(notes) == api_json['totalNoteCount']
        assert not next((n for n in notes if n['peerAdvisingDepartmentId'] != self.ce3_navcal_peer_advising_department_id), None)
        note = next((n for n in notes if n['id'] == note_id), None)
        assert note
        assert note['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert len(note['comments'])
        for comment in note['comments']:
            assert comment['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id


class TestGetPeerAdvisingTopics:

    @classmethod
    def _api_get_peer_advising_topics(cls, client, expected_status_code=200):
        response = client.get('/api/peer_advising/note_topics')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
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


class TestPeerAdvisorAddNoteComment:

    @classmethod
    def setup_class(cls):
        peer_advisor_user_id = AuthorizedUser.get_id_per_uid(ce3_navcal_peer_advisor_uid)
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(peer_advisor_user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']


    def test_unauthorized_peer_advising_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note):
        """Unauthorized user cannot comment on Peer Advising note."""
        for uid in [None, coe_advisor_no_advising_data_uid, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_add_note_comment(
                body='Hack the body!',
                client=client,
                parent_note_id=mock_navcal_peer_advising_note.id,
                expected_status_code=401,
            )

    def test_admin_peer_advising_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note):
        """Admin user cannot comment on Peer Advising note."""
        fake_auth.login(admin_uid)
        self._api_add_note_comment(
            body='With great power comes great responsibility.',
            client=client,
            parent_note_id=mock_navcal_peer_advising_note.id,
            expected_status_code=404,
        )

    def test_foreign_dept_peer_advisor_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note):
        """Peer advisor cannot comment on a Peer Advising note from another department."""
        fake_auth.login(coe_mech_peer_advisor_uid)
        self._api_add_note_comment(
            body='A comment that has no business being here',
            client=client,
            parent_note_id=mock_navcal_peer_advising_note.id,
            expected_status_code=404,
        )

    def test_nonexistent_peer_advising_note_comment(self, client, fake_auth):
        """Peer advisor cannot comment on a nonexistent Peer Advising note."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        self._api_add_note_comment(
            body='An orphan comment',
            client=client,
            parent_note_id=9999,
            expected_status_code=404,
        )

    def test_peer_advisor_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note):
        """Peer advisor can comment on a Peer Advising note within their department."""
        # Peer Advising Manager reads a peer advisor's note
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        _api_mark_note_read(client, mock_navcal_peer_advising_note.id)

        # Another Peer Advisor comments on the note
        body = 'A very interesting comment!'
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_add_note_comment(
            body=body,
            client=client,
            parent_note_id=mock_navcal_peer_advising_note.id,
        )
        assert api_json['body'].strip().replace(' ', '') == body.strip().replace(' ', '')
        assert api_json['parentNoteId'] == mock_navcal_peer_advising_note.id
        assert api_json['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert api_json['sid'] == mock_navcal_peer_advising_note.sid
        # Comment marked read by its author
        comment_author_id = AuthorizedUser.get_id_per_uid(api_json['author']['uid'])
        notes_read = NoteRead.get_notes_read_by_user(viewer_id=comment_author_id, note_ids=[api_json['id']])
        assert len(notes_read) == 1

        # Note and comment marked unread for Peer Advising Manager
        manager_id = AuthorizedUser.get_id_per_uid(ce3_navcal_peer_advisor_manager_uid)
        notes_read = NoteRead.get_notes_read_by_user(
            viewer_id=manager_id,
            note_ids=[mock_navcal_peer_advising_note.id, api_json['id']],
        )
        assert len(notes_read) == 0

        # Note and comment marked unread for note author
        note_author_id = AuthorizedUser.get_id_per_uid(mock_navcal_peer_advising_note.author_uid)
        notes_read = NoteRead.get_notes_read_by_user(viewer_id=note_author_id, note_ids=[mock_navcal_peer_advising_note.id, api_json['id']])
        assert len(notes_read) == 0


    @classmethod
    def _api_add_note_comment(
            cls,
            body,
            client,
            parent_note_id,
            attachments=None,
            expected_status_code=200,
    ):
        data = {
            'parentNoteId': parent_note_id,
            'body': body,
            'attachments': attachments,
        }
        response = client.post(
            '/api/peer_advising/note/add_comment',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json


class TestPeerAdvisorEditNoteComment:

    @classmethod
    def setup_class(cls):
        peer_advisor_user_id = AuthorizedUser.get_id_per_uid(ce3_navcal_peer_advisor_uid)
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(peer_advisor_user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']


    def test_unauthorized_peer_advising_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note_with_comments):
        """Unauthorized user cannot edit a Peer Advising note comment."""
        comments = Note.get_notes_by_parent_id(mock_navcal_peer_advising_note_with_comments.id)
        for uid in [None, coe_advisor_no_advising_data_uid, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            for comment in comments:
                self._api_edit_note_comment(
                    comment_id=comment.id,
                    body='Hack the body!',
                    client=client,
                    parent_note_id=mock_navcal_peer_advising_note_with_comments.id,
                    expected_status_code=401,
                )

    def test_admin_peer_advising_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note_with_comments):
        """Admin user cannot edit a Peer Advising note comment."""
        comments = Note.get_notes_by_parent_id(mock_navcal_peer_advising_note_with_comments.id)
        fake_auth.login(admin_uid)
        for comment in comments:
            self._api_edit_note_comment(
                comment_id=comment.id,
                body='With great power comes great responsibility.',
                client=client,
                parent_note_id=mock_navcal_peer_advising_note_with_comments.id,
                expected_status_code=404,
            )

    def test_nonexistent_peer_advising_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note_with_comments):
        """Peer advisor cannot edit a nonexistent Peer Advising note comment."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        self._api_edit_note_comment(
            comment_id=666,
            body='An orphan comment',
            client=client,
            parent_note_id=mock_navcal_peer_advising_note_with_comments.id,
            expected_status_code=404,
        )

    def test_other_advisor_peer_advising_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note_with_comments):
        """Peer advisor cannot edit another advisor's comment."""
        comments = Note.get_notes_by_parent_id(mock_navcal_peer_advising_note_with_comments.id)
        fake_auth.login(ce3_navcal_peer_advisor_2_uid)
        for comment in comments:
            if comment.author_uid != ce3_navcal_peer_advisor_2_uid:
              self._api_edit_note_comment(
                  comment_id=comment.id,
                  body='A comment that has no business being here',
                  client=client,
                  parent_note_id=mock_navcal_peer_advising_note_with_comments.id,
                  expected_status_code=404,
              )

    def test_authorized_peer_advisor_note_comment(self, client, fake_auth, mock_navcal_peer_advising_note_with_comments):
        """Peer advisor can edit their own Peer Advising note comment."""
        # Peer Advising Manager reads the note, marking the comment read as well
        fake_auth.login(ce3_navcal_peer_advisor_manager_uid)
        _api_mark_note_read(client, mock_navcal_peer_advising_note_with_comments.id)

        # Comment author edits the comment
        body = 'A very interesting comment!'
        comments = Note.get_notes_by_parent_id(mock_navcal_peer_advising_note_with_comments.id)
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        comment = next((c for c in comments if c.author_uid == ce3_navcal_peer_advisor_uid), None)
        api_json = self._api_edit_note_comment(
            comment_id=comment.id,
            body=body,
            client=client,
            parent_note_id=mock_navcal_peer_advising_note_with_comments.id,
        )
        assert api_json['body'].strip().replace(' ', '') == body.strip().replace(' ', '')
        assert api_json['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert api_json['sid'] == mock_navcal_peer_advising_note_with_comments.sid
        assert api_json['updatedAt']
        assert api_json['createdAt'] != api_json['updatedAt']

        # Comment marked read by its author
        comment_author_id = AuthorizedUser.get_id_per_uid(api_json['author']['uid'])
        notes_read = NoteRead.get_notes_read_by_user(viewer_id=comment_author_id, note_ids=[api_json['id']])
        assert len(notes_read) == 1

        # Note and comment marked unread for Peer Advising Manager
        manager_id = AuthorizedUser.get_id_per_uid(ce3_navcal_peer_advisor_manager_uid)
        notes_read = NoteRead.get_notes_read_by_user(
            viewer_id=manager_id,
            note_ids=[mock_navcal_peer_advising_note_with_comments.id, api_json['id']],
        )
        assert len(notes_read) == 0

        # Note and comment marked unread for note author
        note_author_id = AuthorizedUser.get_id_per_uid(mock_navcal_peer_advising_note_with_comments.author_uid)
        notes_read = NoteRead.get_notes_read_by_user(
            viewer_id=note_author_id,
            note_ids=[mock_navcal_peer_advising_note_with_comments.id, api_json['id']],
        )
        assert len(notes_read) == 0

    @classmethod
    def _api_edit_note_comment(
            cls,
            comment_id,
            body,
            client,
            parent_note_id,
            attachments=None,
            expected_status_code=200,
    ):
        data = {
            'id': comment_id,
            'parentNoteId': parent_note_id,
            'body': body,
            'attachments': attachments,
        }
        response = client.post(
            '/api/peer_advising/note/edit_comment',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json


class TestPeerAdvisingNoteAttachments:

    @classmethod
    def setup_class(cls):
        author_uid = ce3_navcal_peer_advisor_uid
        peer_advisor_user_id = AuthorizedUser.get_id_per_uid(author_uid)
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(peer_advisor_user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']

    def test_remove_attachment(self, app, client, fake_auth):
        """Remove an attachment from an existing Peer Advising note."""
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        note = _api_create_peer_advising_note(
            body='CE3 NAVCAL note created by Peer Advisor',
            client=client,
            peer_advising_department_id=self.ce3_navcal_peer_advising_department_id,
            sid=coe_student['sid'],
        )
        note_id = note['id']
        base_dir = app.config['BASE_DIR']
        note = _api_note_attachments_upload(
            app=app,
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
            client=client,
            note_id=note_id,
        )
        attachment_ids = [note['attachments'][0]['id'], note['attachments'][1]['id']]
        # Both PAM and Peer Advisors can delete attachments of this note.
        for uid in (ce3_navcal_peer_advisor_uid, ce3_navcal_peer_advisor_manager_uid):
            fake_auth.login(uid)
            # Delete attachment
            attachment_id_to_delete = attachment_ids.pop()
            delete_response = client.delete(f'/api/peer_advising/note/{note_id}/attachment/{attachment_id_to_delete}')
            assert delete_response.status_code == 200
            std_commit(allow_test_environment=True)
            # Verify
            note = Note.find_by_id(note_id)
            attachment = next((a for a in note.attachments if a.id == attachment_id_to_delete), None)
            assert attachment is None


class TestGetStudentEnrollments:

    @classmethod
    def _api_get_student_enrollments(cls, client, sid, expected_status_code=200):
        response = client.get(f'/api/peer_advising/{sid}/enrollments')
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Only Peer Advisors can reach this API."""
        for uid in [None, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_get_student_enrollments(
                client,
                expected_status_code=401,
                sid='11667051',
            )

    def test_authorized(self, client, fake_auth):
        """Peer Advisors get minimal access to student enrollment data."""
        fake_auth.login(coe_mech_peer_advisor_uid)
        api_json = self._api_get_student_enrollments(client, sid='11667051')
        # Verify term info
        assert len(api_json)
        previous_academic_calendar = None
        for academic_year_label, enrollments_by_term_id in api_json.items():
            if previous_academic_calendar:
                assert academic_year_label < previous_academic_calendar
            previous_academic_calendar = academic_year_label
            assert len(enrollments_by_term_id) == 3
            previous_term_id = None
            for term_id, enrollments in enrollments_by_term_id.items():
                if previous_term_id:
                    assert int(term_id) > int(previous_term_id)
                # Verify limited enrollment data
                previous_display_name = None
                for enrollment in enrollments:
                    assert set(enrollment.keys()) == {'displayName', 'sections', 'title', 'units'}
                    display_name = enrollment['displayName']
                    if previous_display_name:
                        assert display_name > previous_display_name
                    sections = enrollment['sections']
                    assert len(sections)
                    assert set(sections[0]) == {'component', 'enrollmentStatus', 'isUncompletedPerGrade', 'primary', 'sectionId', 'sectionNumber'}
                    previous_display_name = display_name
                previous_term_id = term_id


class TestUpdatePeerAdvisingNotes:

    @classmethod
    def setup_class(cls):
        author_uid = ce3_navcal_peer_advisor_uid
        peer_advisor_user_id = AuthorizedUser.get_id_per_uid(author_uid)
        memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(peer_advisor_user_id)
        cls.ce3_navcal_peer_advising_department_id = memberships[0]['peer_advising_department_id']
        cls.mock_ce3_navcal_peer_advising_note = None
        cls.student_sid_of_note = '11667051'
        # Create mock note
        note = Note.create(
            author_uid=author_uid,
            author_name='Davey Jones',
            author_role='peer_advisor',
            author_dept_codes=[],
            body="""
                I bought you a pair of shoes, a trumpet you can blow
                And a book of rules on what to say to people
                When they pick on you
                'Cause if you stay with us, you're gonna be pretty kooky, too.
            """,
            peer_advising_department_id=cls.ce3_navcal_peer_advising_department_id,
            sid=cls.student_sid_of_note,
            subject='Kooks',
            contact_type=None,
            topics=['collaborative synergies', 'vertical solutions'],
        )
        std_commit(allow_test_environment=True)
        cls.peer_advising_note_id = note.id

    @classmethod
    def _api_peer_advising_note_update(
            cls,
            body,
            client,
            note_id,
            subject,
            expected_status_code=200,
            contact_type=None,
            topics=None,
    ):
        data = {
            'id': note_id,
            'body': body,
            'contactType': contact_type,
            'subject': subject,
            'topics': topics or [],
        }
        response = client.post(
            '/api/peer_advising/note/update',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized_peer_advising_note_update(self, client, fake_auth):
        """Unauthorized user cannot update Peer Advising note."""
        for uid in [None, coe_advisor_no_advising_data_uid, qcadv_advisor_uid]:
            if uid:
                fake_auth.login(uid)
            self._api_peer_advising_note_update(
                body='Hack the body!',
                client=client,
                expected_status_code=401,
                note_id=self.peer_advising_note_id,
                subject='Hack the subject!',
            )

    def test_authorized_peer_advising_note_update(self, client, fake_auth):
        """Update Peer Advising note topics."""
        body = """
            Don't pick fights with the bullies or the cads
            'Cause I'm not much cop at punching other people's dads
            And if the homework brings you down
            Then we'll throw it on the fire and take the car downtown
        """
        subject = 'Cause we believe in you'
        topics = ['One', 'two', 'three', 'four']
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_peer_advising_note_update(
            body=body,
            client=client,
            contact_type='Email',
            note_id=self.peer_advising_note_id,
            subject=subject,
            topics=topics,
        )
        assert api_json['body'].strip().replace(' ', '') == body.strip().replace(' ', '')
        assert api_json['peerAdvisingDepartmentId'] == self.ce3_navcal_peer_advising_department_id
        assert api_json['subject'] == subject
        assert api_json['sid'] == self.student_sid_of_note
        for topic in topics:
            assert topic in api_json['topics']

    def test_remove_note_topics(self, client, fake_auth):
        """Delete note topics."""
        note = Note.find_by_id(self.peer_advising_note_id)
        assert len(note.topics) > 0
        fake_auth.login(ce3_navcal_peer_advisor_uid)
        api_json = self._api_peer_advising_note_update(
            body=note.body,
            client=client,
            contact_type='Email',
            note_id=note.id,
            subject=note.subject,
            topics=[],
        )
        assert len(api_json['topics']) == 0
        # Put those topics back
        fresh_topics = ['One', 'two', 'three', 'four']
        api_json = self._api_peer_advising_note_update(
            body=note.body,
            client=client,
            contact_type='Email',
            note_id=note.id,
            subject=note.subject,
            topics=fresh_topics,
        )
        assert set(api_json['topics']) == set(fresh_topics)


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
        'topics': topics,
    }
    response = client.post(
        '/api/peer_advising/note/create',
        content_type='application/json',
        data=json.dumps(data),
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_get_notes_for_peer_advisor(client, uid, include_students=False, expected_status_code=200):
    response = client.get(f'/api/peer_advisor/{uid}/notes?includeStudents={include_students}')
    assert response.status_code == expected_status_code
    return response.json


def _api_note_attachments_upload(
    app,
    attachments,
    client,
    note_id,
    expected_status_code=200,
):
    with mock_advising_note_s3_bucket(app):
        data = {}
        for index, path in enumerate(attachments):
            data[f'attachment[{index}]'] = open(path, 'rb')
        response = client.post(
            f'/api/peer_advisor/note/{note_id}/attachments',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json


def _api_mark_note_read(
    client,
    note_id,
    expected_status_code=201,
):
    response = client.post(f'/api/notes/{note_id}/mark_read')
    assert response.status_code == expected_status_code
    return response.json
