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
from sqlalchemy.exc import IntegrityError

from boac import db
from boac.models.authorized_user import AuthorizedUser
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from boac.models.note import Note
from boac.models.user_tag import UserTag

admin_uid = '177473'
coe_advisor_uid = '1133399'
l_s_advisor_uid = '242881'


@pytest.fixture
def note(app):
    return Note.create(
        author_uid=coe_advisor_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=['COENG'],
        body='A note that tags another advisor.',
        sid='11667051',
        subject='Tagging test',
    )


@pytest.fixture
def comment(app):
    parent = CommentParent.find_or_create(parent_type='appointment', parent_id='user-tag-test-appointment')
    return Comment.create(
        comment_parent_id=parent.id,
        author_uid=coe_advisor_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=['COENG'],
        body='A comment that tags another advisor.',
    )


def _user_id(uid):
    return AuthorizedUser.get_id_per_uid(uid)


@pytest.mark.usefixtures('db_session')
class TestUserTag:
    """User tag."""

    def test_create_for_note(self, note):
        user_id = _user_id(l_s_advisor_uid)
        user_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        assert user_tag.id
        assert user_tag.user_id == user_id
        assert user_tag.object_id == note.id
        assert user_tag.object_type == 'note'
        assert user_tag.email_notification_sent is False
        assert user_tag.read_by_user is False
        assert user_tag.archived_by_user is False
        assert user_tag.deleted_at is None

    def test_create_for_comment(self, comment):
        user_tag = UserTag.create(user_id=_user_id(l_s_advisor_uid), object_id=comment.id, object_type='comment')
        assert user_tag.object_type == 'comment'
        assert user_tag.to_api_json()['objectId'] == comment.id

    def test_create_rejects_unknown_object_type(self, note):
        with pytest.raises(ValueError, match='Invalid user tag object type'):
            UserTag.create(user_id=_user_id(l_s_advisor_uid), object_id=note.id, object_type='appointment')

    def test_create_does_not_duplicate_tag(self, note):
        user_id = _user_id(l_s_advisor_uid)
        first = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        second = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        assert first.id == second.id
        assert len(UserTag.get_all_for_user(user_id)) == 1

    def test_same_object_id_for_different_types_is_distinct(self, note, comment):
        # A note and a comment can share an id value, so object_type has to be part of a tag's identity.
        user_id = _user_id(l_s_advisor_uid)
        note_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        comment_tag = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        assert note_tag.id != comment_tag.id

    def test_object_must_exist(self):
        # Backed by the foreign keys on the generated note_id and comment_id columns.
        with pytest.raises(IntegrityError):
            UserTag.create(user_id=_user_id(l_s_advisor_uid), object_id=999999999, object_type='note')
        db.session.rollback()
        with pytest.raises(IntegrityError):
            UserTag.create(user_id=_user_id(l_s_advisor_uid), object_id=999999999, object_type='comment')
        db.session.rollback()

    def test_mark_read_and_unread(self, note):
        user_id = _user_id(l_s_advisor_uid)
        user_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        assert UserTag.update_flags(user_tag.id, user_id, read_by_user=True).read_by_user is True
        assert UserTag.get_unread_count(user_id) == 0
        assert UserTag.update_flags(user_tag.id, user_id, read_by_user=False).read_by_user is False
        assert UserTag.get_unread_count(user_id) == 1

    def test_archive_and_unarchive(self, note):
        user_id = _user_id(l_s_advisor_uid)
        user_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        archived = UserTag.update_flags(user_tag.id, user_id, archived_by_user=True)
        # Archiving leaves the read flag alone, but an archived tag drops out of the list and the unread count.
        assert archived.archived_by_user is True
        assert archived.read_by_user is False
        assert UserTag.get_all_for_user(user_id) == []
        assert [t.id for t in UserTag.get_all_for_user(user_id, archived=True)] == [user_tag.id]
        assert UserTag.get_unread_count(user_id) == 0
        assert UserTag.update_flags(user_tag.id, user_id, archived_by_user=False).archived_by_user is False
        assert UserTag.get_unread_count(user_id) == 1

    def test_update_both_flags(self, note):
        user_id = _user_id(l_s_advisor_uid)
        user_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        updated = UserTag.update_flags(user_tag.id, user_id, read_by_user=True, archived_by_user=True)
        assert updated.read_by_user is True
        assert updated.archived_by_user is True

    def test_mark_read_only_own_tag(self, note):
        user_id = _user_id(l_s_advisor_uid)
        user_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        assert UserTag.update_flags(user_tag.id, _user_id(admin_uid), read_by_user=True, archived_by_user=True) is None
        user_tag = UserTag.find_by_id_for_user(user_tag.id, user_id)
        assert user_tag.read_by_user is False
        assert user_tag.archived_by_user is False

    def test_mark_read_deleted_tag(self, note):
        user_id = _user_id(l_s_advisor_uid)
        user_tag = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        UserTag.delete(user_id=user_id, object_id=note.id, object_type='note')
        assert UserTag.update_flags(user_tag.id, user_id, read_by_user=True) is None
        assert UserTag.update_flags(user_tag.id, user_id, archived_by_user=True) is None

    def test_get_unread_count(self, note, comment):
        user_id = _user_id(l_s_advisor_uid)
        own_note = Note.create(
            author_uid=admin_uid,
            author_name='Test Author',
            author_role='Advisor',
            author_dept_codes=['COENG'],
            body='Another note that tags an advisor.',
            sid='11667051',
            subject='Unread count test',
        )
        unread = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        read = UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        read.read_by_user = True
        archived = UserTag.create(user_id=user_id, object_id=own_note.id, object_type='note')
        archived.archived_by_user = True
        db.session.flush()
        UserTag.create(user_id=_user_id(admin_uid), object_id=note.id, object_type='note')
        assert UserTag.get_unread_count(user_id) == 1
        # A tag removed from its note or comment no longer counts.
        UserTag.delete(user_id=user_id, object_id=unread.object_id, object_type='note')
        assert UserTag.get_unread_count(user_id) == 0

    def test_get_all_for_user(self, note, comment):
        user_id = _user_id(l_s_advisor_uid)
        other_user_id = _user_id(admin_uid)
        UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        UserTag.create(user_id=user_id, object_id=comment.id, object_type='comment')
        UserTag.create(user_id=other_user_id, object_id=note.id, object_type='note')
        user_tags = UserTag.get_all_for_user(user_id)
        assert {(t.object_id, t.object_type) for t in user_tags} == {(note.id, 'note'), (comment.id, 'comment')}
        assert all(t.user_id == user_id for t in user_tags)
        assert len(UserTag.get_all_for_user(other_user_id)) == 1

    def test_delete_is_soft_and_scoped_to_one_user(self, note):
        user_id = _user_id(l_s_advisor_uid)
        other_user_id = _user_id(admin_uid)
        UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        UserTag.create(user_id=other_user_id, object_id=note.id, object_type='note')
        assert UserTag.delete(user_id=user_id, object_id=note.id, object_type='note') is True
        assert UserTag.get_all_for_user(user_id) == []
        assert len(UserTag.get_all_for_user(other_user_id)) == 1
        row = UserTag.query.filter_by(user_id=user_id, object_id=note.id).one()
        assert row.deleted_at is not None

    def test_delete_missing_tag(self, note):
        assert UserTag.delete(user_id=_user_id(l_s_advisor_uid), object_id=note.id, object_type='note') is False

    def test_tag_again_after_delete(self, note):
        user_id = _user_id(l_s_advisor_uid)
        first = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        UserTag.delete(user_id=user_id, object_id=note.id, object_type='note')
        second = UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        assert second.id != first.id
        assert len(UserTag.get_all_for_user(user_id)) == 1

    def test_delete_for_object(self, note, comment):
        user_ids = [_user_id(l_s_advisor_uid), _user_id(admin_uid)]
        for user_id in user_ids:
            UserTag.create(user_id=user_id, object_id=note.id, object_type='note')
        comment_tag = UserTag.create(user_id=user_ids[0], object_id=comment.id, object_type='comment')
        assert UserTag.delete_for_object(object_id=note.id, object_type='note') == 2
        assert [t.id for t in UserTag.get_all_for_user(user_ids[0])] == [comment_tag.id]
        assert UserTag.get_all_for_user(user_ids[1]) == []

    def test_delete_for_object_keeps_excepted_users(self, note):
        keep_id, drop_id = _user_id(l_s_advisor_uid), _user_id(admin_uid)
        UserTag.create(user_id=keep_id, object_id=note.id, object_type='note')
        UserTag.create(user_id=drop_id, object_id=note.id, object_type='note')
        assert UserTag.delete_for_object(object_id=note.id, object_type='note', except_user_ids=[keep_id]) == 1
        assert len(UserTag.get_all_for_user(keep_id)) == 1
        assert UserTag.get_all_for_user(drop_id) == []
