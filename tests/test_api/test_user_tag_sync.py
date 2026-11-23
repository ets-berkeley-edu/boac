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

import json

import pytest

from boac.merged.calnet import get_calnet_user_for_uid
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.user_tag import UserTag

# Fixture UIDs, described in .claude/docs/permissions.md.
admin_uid = '2040'
coe_advisor_uid = '1133399'
ce3_writer_uid = '2525'
director_uid = '6446'
advisor_uid = '1081940'
ce3_advisor_uid = '5405613'
deleted_uid = '1015674'
eop_manager_uid = '3535'
eop_peer_advisor_uid = '1563405'
student_sid = '9000000000'
other_student_sid = '11667051'
# An appointment that exists for the fixture student in the data loch fixtures.
APPOINTMENT_PARENT_ID = '11667051-00010'


def _tag(*uids):
    # Synthetic text only. The tests care about who is tagged, not what the note says.
    return '<p>Synthetic note: ' + ' '.join(f'@{uid}' for uid in uids) + '</p>'


def _user_id(uid):
    return AuthorizedUser.find_by_uid(uid, ignore_deleted=False).id


def _active_tag_user_ids(object_id, object_type):
    rows = UserTag.query.filter_by(object_id=object_id, object_type=object_type, deleted_at=None).all()
    return sorted(row.user_id for row in rows)


def _all_tag_rows(object_id, object_type):
    return UserTag.query.filter_by(object_id=object_id, object_type=object_type).order_by(UserTag.id).all()


def _create_draft(client):
    response = client.post('/api/note/create_draft', content_type='application/json', data=json.dumps({'sid': None}))
    assert response.status_code == 200
    return response.json


def _api_update_note(client, note_id, body, expected_status_code=200, is_draft=False, is_private=False, sids=(student_sid,)):
    data = {
        'body': body,
        'id': note_id,
        'isDraft': is_draft,
        'isPrivate': is_private,
        'sids': list(sids),
        'subject': 'Synthetic subject',
    }
    response = client.post('/api/notes/update', buffered=True, content_type='multipart/form-data', data=data)
    assert response.status_code == expected_status_code
    return response.json


def _publish(client, body, is_private=False):
    draft = _create_draft(client)
    return _api_update_note(client, draft['id'], body, is_private=is_private)


def _api_form_post(client, endpoint, data, expected_status_code=200):
    response = client.post(endpoint, buffered=True, content_type='multipart/form-data', data=data)
    assert response.status_code == expected_status_code
    return response.json


def _api_create_peer_note(client, body, expected_status_code=200):
    data = {
        'body': body,
        'peerAdvisingDepartmentId': _eop_id(),
        'sid': student_sid,
        'subject': 'Synthetic subject',
        'topics': [],
    }
    response = client.post('/api/peer_advising/note/create', content_type='application/json', data=json.dumps(data))
    assert response.status_code == expected_status_code
    return response.json


def _eop_id():
    return PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program').id


def _invalid_tag(app, uid, reason):
    return {'uid': uid, 'name': get_calnet_user_for_uid(app, uid)['name'], 'reason': reason}


@pytest.mark.usefixtures('db_session')
class TestNoteSave:
    """Tags are checked and synced when an advising note is published or edited."""

    def test_publish_tagging_same_person_twice_creates_one_row(self, client, fake_auth):
        """Publishing a draft that tags the same person twice creates one row."""
        fake_auth.login(coe_advisor_uid)
        note = _publish(client, _tag(advisor_uid, advisor_uid))
        assert _active_tag_user_ids(note['id'], 'note') == [_user_id(advisor_uid)]

    def test_draft_autosave_creates_no_rows(self, client, fake_auth):
        """Saving a draft records no tags, even a tag the publish would reject."""
        fake_auth.login(coe_advisor_uid)
        draft = _create_draft(client)
        _api_update_note(client, draft['id'], _tag(advisor_uid, deleted_uid), is_draft=True, sids=())
        assert _all_tag_rows(draft['id'], 'note') == []

    def test_remove_then_readd_tag(self, client, fake_auth):
        """Removing a tag soft-deletes its row, and adding it back creates a new active row."""
        fake_auth.login(coe_advisor_uid)
        note = _publish(client, _tag(advisor_uid))
        _api_update_note(client, note['id'], '<p>Synthetic note with no tags</p>')
        assert _active_tag_user_ids(note['id'], 'note') == []
        _api_update_note(client, note['id'], _tag(advisor_uid))
        rows = _all_tag_rows(note['id'], 'note')
        assert [row.deleted_at is None for row in rows] == [False, True]

    def test_private_note_rejects_non_ce3_tag(self, app, client, fake_auth):
        """Publishing a private note that tags a non-CE3 advisor returns 400, and the note stays a draft."""
        fake_auth.login(ce3_writer_uid)
        draft = _create_draft(client)
        api_json = _api_update_note(client, draft['id'], _tag(advisor_uid), expected_status_code=400, is_private=True)
        assert api_json['invalidTags'] == [_invalid_tag(app, advisor_uid, 'private_note')]
        assert api_json['message']
        assert Note.find_by_id(draft['id']).is_draft is True
        assert _all_tag_rows(draft['id'], 'note') == []

    def test_batch_publish_with_tag_rejected(self, client, fake_auth):
        """A batch publish with a tag returns 400 batch_note and creates no notes."""
        fake_auth.login(coe_advisor_uid)
        draft = _create_draft(client)
        api_json = _api_update_note(client, draft['id'], _tag(advisor_uid), expected_status_code=400, sids=(student_sid, other_student_sid))
        assert [t['reason'] for t in api_json['invalidTags']] == ['batch_note']
        assert Note.find_by_id(draft['id']).is_draft is True

    def test_self_tag_rejected(self, client, fake_auth):
        """A writer cannot tag themself."""
        fake_auth.login(coe_advisor_uid)
        draft = _create_draft(client)
        api_json = _api_update_note(client, draft['id'], _tag(coe_advisor_uid), expected_status_code=400)
        assert [t['reason'] for t in api_json['invalidTags']] == ['self_tag']

    def test_deleted_user_rejected(self, client, fake_auth):
        """A deleted user cannot be tagged."""
        fake_auth.login(coe_advisor_uid)
        draft = _create_draft(client)
        api_json = _api_update_note(client, draft['id'], _tag(deleted_uid), expected_status_code=400)
        assert [t['reason'] for t in api_json['invalidTags']] == ['deleted_user']

    def test_rejected_edit_leaves_published_note_unchanged(self, client, fake_auth):
        """An edit with a bad tag changes nothing: the body and the rows stay as they were."""
        fake_auth.login(coe_advisor_uid)
        note = _publish(client, _tag(advisor_uid))
        _api_update_note(client, note['id'], _tag(advisor_uid, deleted_uid), expected_status_code=400)
        assert Note.find_by_id(note['id']).body == note['body']
        assert _active_tag_user_ids(note['id'], 'note') == [_user_id(advisor_uid)]

    def test_making_note_private_blocked_by_comment_tag(self, app, client, fake_auth):
        """Making a note private is refused when one of its comments tags a non-CE3 advisor."""
        fake_auth.login(ce3_writer_uid)
        note = _publish(client, '<p>Synthetic note with no tags</p>')
        _api_form_post(client, '/api/note/add_comment', {'parentNoteId': note['id'], 'body': _tag(advisor_uid)})
        api_json = _api_update_note(client, note['id'], note['body'], expected_status_code=400, is_private=True)
        assert api_json['invalidTags'] == [_invalid_tag(app, advisor_uid, 'private_note')]
        assert Note.find_by_id(note['id']).is_private is False

    def test_delete_note_soft_deletes_its_tags_and_its_comments_tags(self, client, fake_auth):
        """Deleting a note soft-deletes its tags and its comments' tags."""
        fake_auth.login(coe_advisor_uid)
        note = _publish(client, _tag(advisor_uid))
        comment = _api_form_post(client, '/api/note/add_comment', {'parentNoteId': note['id'], 'body': _tag(ce3_advisor_uid)})
        fake_auth.login(admin_uid)
        response = client.delete(f"/api/notes/delete/{note['id']}")
        assert response.status_code == 200
        assert _active_tag_user_ids(note['id'], 'note') == []
        assert _active_tag_user_ids(comment['id'], 'note') == []
        assert len(_all_tag_rows(comment['id'], 'note')) == 1

    def test_failed_sync_does_not_fail_the_save(self, client, fake_auth, monkeypatch):
        """If recording the tags fails, the note is still saved."""

        def _fail(*args, **kwargs):
            raise RuntimeError('Synthetic failure')

        monkeypatch.setattr(UserTag, 'create', _fail)
        fake_auth.login(coe_advisor_uid)
        note = _publish(client, _tag(advisor_uid))
        assert Note.find_by_id(note['id']).is_draft is False
        assert _active_tag_user_ids(note['id'], 'note') == []


@pytest.mark.usefixtures('db_session')
class TestNoteCommentSave:
    """Tags in note comments are checked against the parent note and synced on add and edit."""

    def test_add_and_edit_comment(self, client, fake_auth):
        """Adding a comment records its tags, and editing a tag out soft-deletes the row."""
        fake_auth.login(coe_advisor_uid)
        note = _publish(client, '<p>Synthetic note with no tags</p>')
        comment = _api_form_post(client, '/api/note/add_comment', {'parentNoteId': note['id'], 'body': _tag(advisor_uid)})
        assert _active_tag_user_ids(comment['id'], 'note') == [_user_id(advisor_uid)]
        _api_form_post(client, '/api/note/edit_comment', {'id': comment['id'], 'body': _tag(ce3_advisor_uid)})
        assert _active_tag_user_ids(comment['id'], 'note') == [_user_id(ce3_advisor_uid)]

    def test_comment_on_private_note_rejects_non_ce3_tag(self, app, client, fake_auth):
        """A comment on a private note cannot tag someone who can't read private notes."""
        fake_auth.login(ce3_writer_uid)
        note = _publish(client, '<p>Synthetic note with no tags</p>', is_private=True)
        api_json = _api_form_post(
            client,
            '/api/note/add_comment',
            {'parentNoteId': note['id'], 'body': _tag(advisor_uid)},
            expected_status_code=400,
        )
        assert api_json['invalidTags'] == [_invalid_tag(app, advisor_uid, 'private_note')]
        assert Note.get_note_comments_by_parent_ids([note['id']]) == []


@pytest.mark.usefixtures('db_session')
class TestPeerNoteSave:
    """Tags in peer advising notes follow the peer department rules."""

    def test_peer_advisor_cannot_tag_outside_group(self, app, client, fake_auth):
        """A peer advisor tagging an advisor outside their peer group gets 400 outside_peer_department."""
        fake_auth.login(eop_peer_advisor_uid)
        api_json = _api_create_peer_note(client, _tag(advisor_uid), expected_status_code=400)
        assert api_json['invalidTags'] == [_invalid_tag(app, advisor_uid, 'outside_peer_department')]

    def test_peer_advisor_tags_group_member(self, client, fake_auth):
        """A peer advisor may tag a member of their own peer group, and the row is recorded."""
        fake_auth.login(eop_peer_advisor_uid)
        note = _api_create_peer_note(client, _tag(eop_manager_uid))
        assert _active_tag_user_ids(note['id'], 'note') == [_user_id(eop_manager_uid)]

    def test_manager_resaves_peer_advisor_note(self, client, fake_auth):
        """A peer advisor manager re-saving a peer advisor's note keeps the tags already in it."""
        fake_auth.login(eop_peer_advisor_uid)
        note = _api_create_peer_note(client, _tag(eop_manager_uid))
        fake_auth.login(eop_manager_uid)
        _api_form_post(client, '/api/peer_advising/note/update', {
            'id': note['id'],
            'body': _tag(eop_manager_uid),
            'subject': 'Synthetic subject, edited',
            'topics': [],
        })
        assert _active_tag_user_ids(note['id'], 'note') == [_user_id(eop_manager_uid)]


@pytest.mark.usefixtures('db_session')
class TestAppointmentCommentSave:
    """Tags in appointment and eForm comments are recorded with object_type 'comment'."""

    def test_create_update_delete(self, client, fake_auth):
        """Creating a comment records its tag, editing replaces it, and deleting the comment soft-deletes it."""
        fake_auth.login(director_uid)
        comment = _api_form_post(client, '/api/comments/create', {
            'parentType': 'appointment',
            'parentId': APPOINTMENT_PARENT_ID,
            'body': _tag(advisor_uid),
        })
        assert _active_tag_user_ids(comment['id'], 'comment') == [_user_id(advisor_uid)]
        _api_form_post(client, '/api/comments/update', {'id': comment['id'], 'body': _tag(ce3_advisor_uid)})
        assert _active_tag_user_ids(comment['id'], 'comment') == [_user_id(ce3_advisor_uid)]
        fake_auth.login(admin_uid)
        response = client.delete(f"/api/comments/delete/{comment['id']}")
        assert response.status_code == 200
        assert _active_tag_user_ids(comment['id'], 'comment') == []

    def test_create_rejects_deleted_user(self, client, fake_auth):
        """An appointment comment cannot tag a deleted user."""
        fake_auth.login(director_uid)
        api_json = _api_form_post(
            client,
            '/api/comments/create',
            {'parentType': 'appointment', 'parentId': APPOINTMENT_PARENT_ID, 'body': _tag(deleted_uid)},
            expected_status_code=400,
        )
        assert [t['reason'] for t in api_json['invalidTags']] == ['deleted_user']
