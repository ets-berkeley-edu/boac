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

from unittest import mock

import pytest

from boac import db
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from boac.models.note import Note

coe_advisor_uid = '1133399'
# An active BOA user, a soft-deleted BOA user, and a number that belongs to no BOA user.
tagged_uid = '6446'
deleted_uid = '1015674'
not_a_user = '999999999'

TAGGED_BODY = f'<p>Ask @{tagged_uid} and @{deleted_uid} about room @{not_a_user} today.</p>'


def _sent_bodies(send):
    # Every body that a mocked sqs.send call would have put on the search queue.
    return [row['body'] for call in send.call_args_list for row in call.kwargs['rows'] if 'body' in row]


def _assert_tags_stripped(send):
    bodies = _sent_bodies(send)
    assert bodies
    for body in bodies:
        assert f'@{tagged_uid}' not in body
        assert f'@{deleted_uid}' not in body
        # Text that only looks like a tag is ordinary note text and stays searchable.
        assert f'@{not_a_user}' in body
        assert 'Ask' in body
        assert 'today' in body


def _create_note(body, is_draft=False, parent_note_id=None, peer_advising_department_id=None):
    return Note.create(
        author_uid=coe_advisor_uid,
        author_name='Test Author',
        author_role='Advisor',
        author_dept_codes=['COENG'],
        body=body,
        is_draft=is_draft,
        parent_note_id=parent_note_id,
        peer_advising_department_id=peer_advising_department_id,
        sid='11667051',
        subject='Search tag test',
    )


@pytest.fixture
def comment_parent(app):
    return CommentParent.find_or_create(parent_type='appointment', parent_id='user-tag-sqs-appointment')


@pytest.mark.usefixtures('db_session')
class TestNoteSqsBody:

    def test_create(self):
        """A published note goes to search without the UIDs it tags, and keeps them in the database."""
        with mock.patch('boac.externals.sqs.send') as send:
            note = _create_note(TAGGED_BODY)
        _assert_tags_stripped(send)
        assert Note.find_by_id(note.id).body == TAGGED_BODY

    def test_publish_draft(self):
        """Publishing a draft sends the stripped body."""
        draft = _create_note('<p>Draft</p>', is_draft=True)
        with mock.patch('boac.externals.sqs.send') as send:
            Note.update(is_draft=False, note_id=draft.id, sid='11667051', subject='Search tag test', body=TAGGED_BODY)
        _assert_tags_stripped(send)
        assert Note.find_by_id(draft.id).body == TAGGED_BODY

    def test_update_and_delete(self):
        """Edits and deletes of a published note send the stripped body."""
        note = _create_note('<p>No tags yet</p>')
        with mock.patch('boac.externals.sqs.send') as send:
            Note.update(is_draft=False, note_id=note.id, sid='11667051', subject='Search tag test', body=TAGGED_BODY)
            Note.update_subject(note.id, 'New subject')
            Note.delete(note.id)
        assert len(send.call_args_list) == 3
        _assert_tags_stripped(send)

    def test_note_comment(self):
        """A note comment, which is a notes row with a parent, goes to search stripped."""
        note = _create_note('<p>Parent</p>')
        with mock.patch('boac.externals.sqs.send') as send:
            comment = _create_note(TAGGED_BODY, parent_note_id=note.id)
        _assert_tags_stripped(send)
        assert Note.find_by_id(comment.id).body == TAGGED_BODY

    def test_peer_note(self):
        """A peer advising note goes to search stripped."""
        with mock.patch('boac.externals.sqs.send') as send:
            _create_note(TAGGED_BODY, peer_advising_department_id=1)
        _assert_tags_stripped(send)

    def test_batch(self):
        """Every row of a batch note goes to search stripped."""
        with mock.patch('boac.externals.sqs.send') as send:
            Note.create_batch(
                author_id=1,
                author_uid=coe_advisor_uid,
                author_name='Test Author',
                author_role='Advisor',
                author_dept_codes=['COENG'],
                body=TAGGED_BODY,
                contact_type=None,
                is_private=False,
                set_date=None,
                sids=['11667051', '9000000000'],
                subject='Search tag test',
            )
        assert len(_sent_bodies(send)) == 2
        _assert_tags_stripped(send)

    def test_body_without_tags_unchanged(self):
        """A body with no tags is sent exactly as saved."""
        body = '<p>Email me at advisor@example.edu</p>'
        with mock.patch('boac.externals.sqs.send') as send:
            _create_note(body)
        assert _sent_bodies(send) == [body]


@pytest.mark.usefixtures('db_session')
class TestCommentSqsBody:

    def test_create_update_delete(self, comment_parent):
        """Appointment and eForm comments go to search stripped on create, update and delete."""
        with mock.patch('boac.externals.sqs.send') as send:
            comment = Comment.create(
                comment_parent_id=comment_parent.id,
                author_uid=coe_advisor_uid,
                author_name='Test Author',
                author_role='Advisor',
                author_dept_codes=['COENG'],
                body=TAGGED_BODY,
            )
            comment.update(body=TAGGED_BODY)
            comment.soft_delete()
        assert len(_sent_bodies(send)) == 3
        _assert_tags_stripped(send)
        # The comment is soft-deleted, so read the row directly rather than through find_by_id.
        assert db.session.get(Comment, comment.id).body == TAGGED_BODY
