"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

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

import pytest

from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from boac.models.note import Note
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.user_tag import UserTag

admin_uid = '2040'
coe_advisor_uid = '1133399'
l_s_advisor_uid = '242881'
# An appointment and an eForm in the fake data loch (fixtures/loch/loch.sql), both for student 11667051.
loch_appointment_id = '11667051-00010'
loch_eform_id = 'eform-10096'
loch_student_sid = '11667051'

# An EOP peer advisor and the EOP peer advisor manager.
peer_advisor_uid = '1563405'
peer_advisor_manager_uid = '3535'


@pytest.fixture
def note(app):
    return _create_note(author_uid=l_s_advisor_uid, author_dept_codes=['QCADV'])


@pytest.fixture
def comment(app):
    return _create_comment(parent_type='appointment', parent_id=loch_appointment_id)


def _create_comment(parent_type, parent_id):
    # The parent type matters to the test that checks what kind of record each tagged comment is on.
    parent = CommentParent.find_or_create(parent_type=parent_type, parent_id=parent_id)
    return Comment.create(
        comment_parent_id=parent.id,
        author_uid=l_s_advisor_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=['QCADV'],
        body='A comment that tags another advisor.',
    )


def _create_note_comment(parent_note, author_uid=l_s_advisor_uid, body='A comment on the note.'):
    # A note comment is itself a note, with parent_note_id pointing at the note it's on.
    return Note.create(
        author_uid=author_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=['QCADV'],
        body=body,
        sid=parent_note.sid,
        subject=parent_note.subject,
        parent_note_id=parent_note.id,
        peer_advising_department_id=parent_note.peer_advising_department_id,
    )


def _create_note(author_uid, author_dept_codes, peer_advising_department_id=None):
    # Pass peer_advising_department_id for a peer note. Tagging rules let a peer advisor be tagged only in their own
    # department's peer notes.
    return Note.create(
        author_uid=author_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=author_dept_codes,
        body='A note that tags an advisor.',
        sid='11667051',
        subject='Tagging test',
        peer_advising_department_id=peer_advising_department_id,
    )


def _peer_advising_department_id(uid):
    memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=_user_id(uid))
    return memberships[0]['peer_advising_department_id']


def _user_id(uid):
    return AuthorizedUser.get_id_per_uid(uid)


def _archive(user_tag):
    # The model has no archive method yet, so set the flag directly the way an archive action would.
    user_tag.archived_by_user = True
    std_commit()


@pytest.mark.usefixtures('db_session')
class TestListUserTags:
    """List user tags API."""

    @classmethod
    def _api_list_user_tags(cls, client, expected_status_code=200):
        response = client.get('/api/user_tag/list')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        self._api_list_user_tags(client, expected_status_code=401)

    def test_peer_advisor_no_user_tags(self, client, fake_auth):
        """Allows a peer advisor, and returns an empty list when nobody has tagged them."""
        fake_auth.login(peer_advisor_uid)
        assert self._api_list_user_tags(client) == {'notifications': []}

    def test_peer_advisor(self, client, fake_auth, note):
        """Returns a peer advisor's tags on their department's peer notes, and nobody else's tags."""
        peer_note = _create_note(
            author_uid=peer_advisor_manager_uid,
            author_dept_codes=['ZCEEE'],
            peer_advising_department_id=_peer_advising_department_id(peer_advisor_uid),
        )
        user_tag = UserTag.create(user_id=_user_id(peer_advisor_uid), object_id=peer_note.id, object_type='note')
        UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note')
        fake_auth.login(peer_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [user_tag.id]
        assert notifications[0]['object']['id'] == peer_note.id
        assert notifications[0]['object']['peerAdvisingDepartmentId'] == peer_note.peer_advising_department_id

    def test_no_user_tags(self, client, fake_auth):
        """Returns an empty list when nobody has tagged the current user."""
        fake_auth.login(coe_advisor_uid)
        assert self._api_list_user_tags(client) == {'notifications': []}

    def test_list_user_tags(self, client, fake_auth, note, comment):
        """Returns the current user's tags on notes and comments, newest first."""
        user_id = _user_id(coe_advisor_uid)
        note_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        comment_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        fake_auth.login(coe_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        # Both tags are created in one transaction and share a created_at, so the id tiebreaker sets the order.
        assert [n['id'] for n in notifications] == [comment_tag.id, note_tag.id]
        # A tag in an appointment comment carries the appointment, with the tagged comment among its comments.
        assert notifications[0]['object']['id'] == loch_appointment_id
        assert notifications[0]['object']['type'] == 'appointment'
        tagged_comment = next(c for c in notifications[0]['object']['comments'] if c['id'] == comment.id)
        assert tagged_comment['author']['uid'] == l_s_advisor_uid
        assert tagged_comment['author']['name'] == 'Test Author'
        assert tagged_comment['body'] == 'A comment that tags another advisor.'
        assert notifications[0]['objectId'] == comment.id
        assert notifications[0]['objectType'] == 'comment'
        assert notifications[0]['userId'] == user_id
        assert notifications[0]['readByUser'] is False
        assert notifications[0]['archivedByUser'] is False
        assert notifications[1]['object']['id'] == note.id
        assert notifications[1]['object']['type'] == 'note'
        assert notifications[1]['object']['author']['uid'] == l_s_advisor_uid
        assert notifications[1]['object']['author']['name'] == 'Test Author'
        assert notifications[1]['object']['body'] == 'A note that tags an advisor.'
        assert notifications[1]['object']['comments'] == []
        assert notifications[1]['object']['taggedUsers'] == {}
        assert notifications[1]['objectId'] == note.id
        assert notifications[1]['objectType'] == 'note'
        assert notifications[1]['userId'] == user_id
        assert notifications[1]['readByUser'] is False
        assert notifications[1]['archivedByUser'] is False

    def test_only_my_user_tags(self, client, fake_auth, note):
        """Leaves out tags that belong to other users."""
        UserTag.create(user_id=_user_id(admin_uid), object_id=note.id, object_type='note')
        own_tag = UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [own_tag.id]

    def test_deleted_user_tags_excluded(self, client, fake_auth, note, comment):
        """Leaves out tags removed from a note or comment."""
        user_id = _user_id(coe_advisor_uid)
        UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        comment_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        UserTag.delete(user_id=user_id, object_id=note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [comment_tag.id]

    def test_archived_user_tags_excluded(self, client, fake_auth, note, comment):
        """Leaves out tags the user has archived."""
        user_id = _user_id(coe_advisor_uid)
        archived_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        unarchived_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        _archive(archived_tag)
        fake_auth.login(coe_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [unarchived_tag.id]
        assert notifications[0]['archivedByUser'] is False

    def test_user_tags_themself(self, client, fake_auth):
        """Lists a tag that a user put on their own note."""
        own_note = _create_note(author_uid=coe_advisor_uid, author_dept_codes=['COENG'])
        user_tag = UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=own_note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [user_tag.id]
        assert notifications[0]['objectId'] == own_note.id

    def test_user_tagged_by_another_user(self, client, fake_auth, note):
        """Lists the tag for the tagged user, but not for the author who wrote the tag."""
        # The note fixture is written by the L&S advisor, who tags the COE advisor.
        user_tag = UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [user_tag.id]
        assert notifications[0]['userId'] == _user_id(coe_advisor_uid)
        fake_auth.login(l_s_advisor_uid)
        assert self._api_list_user_tags(client) == {'notifications': []}

    def test_note_with_comments(self, client, fake_auth, note):
        """A tag in a note carries the note with its comments."""
        note_comment = _create_note_comment(note)
        user_tag = UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        notification = self._api_list_user_tags(client)['notifications'][0]
        assert notification['id'] == user_tag.id
        assert notification['object']['id'] == note.id
        assert [c['id'] for c in notification['object']['comments']] == [note_comment.id]

    def test_note_comment(self, client, fake_auth, note):
        """A tag in a note comment carries the whole parent note, with all of its comments."""
        first_comment = _create_note_comment(note, body='First comment.')
        second_comment = _create_note_comment(note, body='Second comment, which tags an advisor.')
        UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=second_comment.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        notification = self._api_list_user_tags(client)['notifications'][0]
        # objectId still names the tagged comment.
        assert notification['objectId'] == second_comment.id
        assert notification['object']['id'] == note.id
        assert [c['id'] for c in notification['object']['comments']] == [first_comment.id, second_comment.id]

    def test_appointment_with_comments(self, client, fake_auth, comment):
        """A tag in an appointment comment carries the appointment, with all of its comments."""
        other_comment = _create_comment(parent_type='appointment', parent_id=loch_appointment_id)
        UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=comment.id, object_type='comment')
        fake_auth.login(coe_advisor_uid)
        notification = self._api_list_user_tags(client)['notifications'][0]
        assert notification['objectId'] == comment.id
        assert notification['object']['id'] == loch_appointment_id
        assert notification['object']['type'] == 'appointment'
        assert {c['id'] for c in notification['object']['comments']} == {comment.id, other_comment.id}
        # A comment has no SID of its own, so the student comes from the appointment.
        assert notification['object']['student']['sid'] == loch_student_sid

    def test_eform_with_comments(self, client, fake_auth):
        """A tag in an eForm comment carries the eForm, with all of its comments."""
        eform_comment = _create_comment(parent_type='late_drop_eform', parent_id=loch_eform_id)
        UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=eform_comment.id, object_type='comment')
        fake_auth.login(coe_advisor_uid)
        notification = self._api_list_user_tags(client)['notifications'][0]
        assert notification['objectId'] == eform_comment.id
        assert notification['object']['id'] == loch_eform_id
        assert notification['object']['type'] == 'eForm'
        assert notification['object']['parentType'] == 'late_drop_eform'
        assert [c['id'] for c in notification['object']['comments']] == [eform_comment.id]
        assert notification['object']['student']['sid'] == loch_student_sid

    def test_object_not_found(self, client, fake_auth):
        """Returns a null object when the appointment a comment is on isn't in the data loch."""
        orphan_comment = _create_comment(parent_type='appointment', parent_id='user-tag-api-test-missing-appointment')
        UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=orphan_comment.id, object_type='comment')
        fake_auth.login(coe_advisor_uid)
        notification = self._api_list_user_tags(client)['notifications'][0]
        assert notification['objectId'] == orphan_comment.id
        assert notification['object'] is None

    def test_admin(self, client, fake_auth, note):
        """Admin users can list their own tags."""
        user_tag = UserTag.create(user_id=_user_id(admin_uid), object_id=note.id, object_type='note')
        fake_auth.login(admin_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [user_tag.id]


@pytest.mark.usefixtures('db_session')
class TestArchivedUserTags:
    """Archived user tags API."""

    @classmethod
    def _api_archived_user_tags(cls, client, expected_status_code=200):
        response = client.get('/api/user_tag/archived')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        self._api_archived_user_tags(client, expected_status_code=401)

    def test_peer_advisor_no_archived_user_tags(self, client, fake_auth):
        """Allows a peer advisor, and returns an empty list when they have archived no tags."""
        fake_auth.login(peer_advisor_uid)
        assert self._api_archived_user_tags(client) == {'archived': []}

    def test_peer_advisor(self, client, fake_auth, note):
        """Returns a peer advisor's archived tags on their department's peer notes, and nobody else's tags."""
        peer_department_id = _peer_advising_department_id(peer_advisor_uid)
        archived_note = _create_note(peer_advisor_manager_uid, ['ZCEEE'], peer_advising_department_id=peer_department_id)
        unarchived_note = _create_note(peer_advisor_manager_uid, ['ZCEEE'], peer_advising_department_id=peer_department_id)
        user_id = _user_id(peer_advisor_uid)
        archived_tag = UserTag.create(user_id=user_id, object_id=archived_note.id, object_type='note')
        UserTag.create(user_id=user_id, object_id=unarchived_note.id, object_type='note')
        _archive(archived_tag)
        _archive(UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note'))
        fake_auth.login(peer_advisor_uid)
        archived = self._api_archived_user_tags(client)['archived']
        assert [t['id'] for t in archived] == [archived_tag.id]

    def test_no_archived_user_tags(self, client, fake_auth, note):
        """Returns an empty list when the current user has archived no tags."""
        UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        assert self._api_archived_user_tags(client) == {'archived': []}

    def test_archived_user_tags(self, client, fake_auth, note, comment):
        """Returns only the current user's archived tags, newest first."""
        user_id = _user_id(coe_advisor_uid)
        own_note = _create_note(author_uid=coe_advisor_uid, author_dept_codes=['COENG'])
        note_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        comment_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        unarchived_tag = UserTag.create(user_id=user_id, object_id=own_note.id, object_type='note')
        _archive(note_tag)
        _archive(comment_tag)
        fake_auth.login(coe_advisor_uid)
        archived = self._api_archived_user_tags(client)['archived']
        # All three tags share a created_at within the test transaction, so the id tiebreaker sets the order.
        assert [t['id'] for t in archived] == [comment_tag.id, note_tag.id]
        assert unarchived_tag.id not in [t['id'] for t in archived]
        assert archived[0] == comment_tag.to_api_json()
        assert all(t['archivedByUser'] is True for t in archived)

    def test_only_my_archived_user_tags(self, client, fake_auth, note):
        """Leaves out archived tags that belong to other users."""
        _archive(UserTag.create(user_id=_user_id(admin_uid), object_id=note.id, object_type='note'))
        own_tag = UserTag.create(user_id=_user_id(coe_advisor_uid), object_id=note.id, object_type='note')
        _archive(own_tag)
        fake_auth.login(coe_advisor_uid)
        archived = self._api_archived_user_tags(client)['archived']
        assert [t['id'] for t in archived] == [own_tag.id]

    def test_deleted_archived_user_tags_excluded(self, client, fake_auth, note, comment):
        """Leaves out an archived tag that was later removed from its note or comment."""
        user_id = _user_id(coe_advisor_uid)
        _archive(UserTag.create(user_id=user_id, object_id=note.id, object_type='note'))
        comment_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        _archive(comment_tag)
        UserTag.delete(user_id=user_id, object_id=note.id, object_type='note')
        fake_auth.login(coe_advisor_uid)
        archived = self._api_archived_user_tags(client)['archived']
        assert [t['id'] for t in archived] == [comment_tag.id]

    def test_archived_and_list_do_not_overlap(self, client, fake_auth, note, comment):
        """Each tag shows up in exactly one of the list and archived responses."""
        user_id = _user_id(coe_advisor_uid)
        archived_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        unarchived_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        _archive(archived_tag)
        fake_auth.login(coe_advisor_uid)
        assert [t['id'] for t in self._api_archived_user_tags(client)['archived']] == [archived_tag.id]
        notifications = TestListUserTags._api_list_user_tags(client)['notifications']
        assert [t['id'] for t in notifications] == [unarchived_tag.id]

    def test_admin(self, client, fake_auth, note):
        """Admin users can list their own archived tags."""
        user_tag = UserTag.create(user_id=_user_id(admin_uid), object_id=note.id, object_type='note')
        _archive(user_tag)
        fake_auth.login(admin_uid)
        archived = self._api_archived_user_tags(client)['archived']
        assert [t['id'] for t in archived] == [user_tag.id]
