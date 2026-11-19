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
from boac.models.user_tag import UserTag

admin_uid = '2040'
coe_advisor_uid = '1133399'
l_s_advisor_uid = '242881'
peer_advisor_uid = '1563405'


@pytest.fixture
def note(app):
    return _create_note(author_uid=l_s_advisor_uid, author_dept_codes=['QCADV'])


@pytest.fixture
def comment(app):
    parent = CommentParent.find_or_create(parent_type='appointment', parent_id='user-tag-api-test-appointment')
    return Comment.create(
        comment_parent_id=parent.id,
        author_uid=l_s_advisor_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=['QCADV'],
        body='A comment that tags another advisor.',
    )


def _create_note(author_uid, author_dept_codes):
    return Note.create(
        author_uid=author_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=author_dept_codes,
        body='A note that tags an advisor.',
        sid='11667051',
        subject='Tagging test',
    )


def _user_id(uid):
    return AuthorizedUser.get_id_per_uid(uid)


def _archive(user_tag):
    # The model has no archive method yet, so set the flag directly the way an archive action would.
    user_tag.archived_by_user = True
    std_commit()


@pytest.mark.usefixtures('db_session')
class TestListUserTags:

    @classmethod
    def _api_list_user_tags(cls, client, expected_status_code=200):
        response = client.get('/api/user_tag/list')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        self._api_list_user_tags(client, expected_status_code=401)

    def test_peer_advisor(self, client, fake_auth):
        """Denies access to a peer advisor, who has no advisor role."""
        fake_auth.login(peer_advisor_uid)
        self._api_list_user_tags(client, expected_status_code=401)

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
        assert notifications[0]['object']
        assert notifications[0]['object']['author']['uid'] == l_s_advisor_uid
        assert notifications[0]['object']['author']['name'] == 'Test Author'
        assert notifications[0]['object']['body'] == 'A comment that tags another advisor.'
        assert notifications[0]['objectId'] == comment.id
        assert notifications[0]['objectType'] == 'comment'
        assert notifications[0]['userId'] == user_id
        assert notifications[0]['readByUser'] is False
        assert notifications[0]['archivedByUser'] is False
        assert notifications[1]['object']
        assert notifications[1]['object']['authorUid'] == l_s_advisor_uid
        assert notifications[1]['object']['authorName'] == 'Test Author'
        assert notifications[1]['object']['body'] == 'A note that tags an advisor.'
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

    def test_admin(self, client, fake_auth, note):
        """Admin users can list their own tags."""
        user_tag = UserTag.create(user_id=_user_id(admin_uid), object_id=note.id, object_type='note')
        fake_auth.login(admin_uid)
        notifications = self._api_list_user_tags(client)['notifications']
        assert [n['id'] for n in notifications] == [user_tag.id]


@pytest.mark.usefixtures('db_session')
class TestArchivedUserTags:

    @classmethod
    def _api_archived_user_tags(cls, client, expected_status_code=200):
        response = client.get('/api/user_tag/archived')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Denies anonymous access."""
        self._api_archived_user_tags(client, expected_status_code=401)

    def test_peer_advisor(self, client, fake_auth):
        """Denies access to a peer advisor, who has no advisor role."""
        fake_auth.login(peer_advisor_uid)
        self._api_archived_user_tags(client, expected_status_code=401)

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
