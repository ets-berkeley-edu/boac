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

import io
import json
import zipfile

import pytest

from boac.merged.calnet import get_calnet_user_for_uid
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.peer_advising_department import PeerAdvisingDepartment
from tests.util import mock_sis_note_attachment

# Fixture UIDs, described in .claude/docs/permissions.md.
director_uid = '6446'
advisor_uid = '1081940'
ce3_advisor_uid = '5405613'
eop_manager_uid = '3535'
eop_peer_advisor_uid = '1563405'
student_sid = '11667051'
# A UID no fixture or test user can have, so it stays plain text rather than a tag.
NOT_A_USER_UID = '999999999'
# The student the existing download tests use, whose legacy attachment the S3 mock serves.
DOWNLOAD_STUDENT_SID = '9000000000'


def _eop_id():
    return PeerAdvisingDepartment.get_department_by_name('Educational Opportunity Program').id


def _name(app, uid):
    # Fixture names are read from the mock CalNet record, never hard-coded in tests.
    return get_calnet_user_for_uid(app, uid)['name']


def _tag(uid):
    return f'<p>Synthetic note: ask @{uid}</p>'


def _create_note(
        author_uid,
        body,
        author_dept_codes=('UWASC',),
        is_private=False,
        parent_note_id=None,
        peer_advising_department_id=None,
        sid=student_sid,
):
    # Synthetic text only. The tests care about who is tagged and who may see the note.
    return Note.create(
        author_uid=author_uid,
        author_name='Synthetic Author',
        author_role='Advisor',
        author_dept_codes=list(author_dept_codes),
        sid=sid,
        subject='Synthetic subject',
        body=body,
        is_private=is_private,
        parent_note_id=parent_note_id,
        peer_advising_department_id=peer_advising_department_id,
    )


class _CallSpy:
    """Wraps a callable and counts its calls, so a test can assert how many lookups a response made."""

    def __init__(self, func):
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


@pytest.mark.usefixtures('db_session')
class TestNoteTaggedUsers:
    """The taggedUsers map in BOA note JSON."""

    def test_note_has_tagged_users(self, app, client, fake_auth):
        """A note's JSON names the people tagged in its body, and the body keeps the UID."""
        note = _create_note(director_uid, _tag(advisor_uid))
        fake_auth.login(director_uid)
        response = client.get(f'/api/note/{note.id}')
        assert response.status_code == 200
        assert response.json['taggedUsers'] == {advisor_uid: {'name': _name(app, advisor_uid)}}
        assert f'@{advisor_uid}' in response.json['body']

    def test_untagged_note_has_empty_map(self, client, fake_auth):
        """A note with no tags has an empty map."""
        note = _create_note(director_uid, '<p>Synthetic note, nobody tagged</p>')
        fake_auth.login(director_uid)
        assert client.get(f'/api/note/{note.id}').json['taggedUsers'] == {}

    def test_private_note_hidden_from_non_ce3(self, client, fake_auth):
        """A private note's body is hidden from a non-CE3 advisor, so no names are given either."""
        note = _create_note(ce3_advisor_uid, _tag(advisor_uid), author_dept_codes=('ZCEEE',), is_private=True)
        fake_auth.login(director_uid)
        response = client.get(f'/api/note/{note.id}')
        assert response.status_code == 200
        assert response.json['body'] is None
        # The message field repeats the body, so it must be hidden too or the raw text and its UIDs would leak.
        assert response.json['message'] is None
        assert response.json['taggedUsers'] == {}

    def test_nested_comment_has_own_map(self, client, fake_auth):
        """Each note comment carries its own map, separate from its parent's."""
        note = _create_note(director_uid, _tag(advisor_uid))
        _create_note(director_uid, _tag(ce3_advisor_uid), parent_note_id=note.id)
        fake_auth.login(director_uid)
        api_json = client.get(f'/api/note/{note.id}').json
        assert set(api_json['taggedUsers'].keys()) == {advisor_uid}
        assert set(api_json['comments'][0]['taggedUsers'].keys()) == {ce3_advisor_uid}

    def test_timeline_tagged_users_and_one_lookup(self, app, client, fake_auth, monkeypatch):
        """The student timeline names every tag and makes one lookup however many tagged notes it holds."""
        note_one = _create_note(director_uid, _tag(advisor_uid))
        note_two = _create_note(director_uid, _tag(ce3_advisor_uid))
        comment = _create_note(director_uid, _tag(advisor_uid), parent_note_id=note_one.id)
        private_note = _create_note(ce3_advisor_uid, _tag(advisor_uid), author_dept_codes=('ZCEEE',), is_private=True)
        spy = _CallSpy(AuthorizedUser.get_existing_uids)
        monkeypatch.setattr(AuthorizedUser, 'get_existing_uids', spy)
        fake_auth.login(director_uid)
        response = client.get(f'/api/student/by_sid/{student_sid}')
        assert response.status_code == 200
        notes_by_id = {n['id']: n for n in response.json['notifications']['note']}
        assert notes_by_id[note_one.id]['taggedUsers'] == {advisor_uid: {'name': _name(app, advisor_uid)}}
        assert notes_by_id[note_two.id]['taggedUsers'] == {ce3_advisor_uid: {'name': _name(app, ce3_advisor_uid)}}
        nested = notes_by_id[note_one.id]['comments']
        assert [c['id'] for c in nested] == [comment.id]
        assert nested[0]['taggedUsers'] == {advisor_uid: {'name': _name(app, advisor_uid)}}
        assert notes_by_id[private_note.id]['taggedUsers'] == {}
        assert spy.calls == 1

    def test_peer_advisor_note_lists_have_tagged_users(self, app, client, fake_auth):
        """The peer advisor and department note lists include each note's tagged names."""
        note = _create_note(
            eop_peer_advisor_uid,
            _tag(advisor_uid),
            author_dept_codes=('ZCEEE',),
            peer_advising_department_id=_eop_id(),
        )
        expected = {advisor_uid: {'name': _name(app, advisor_uid)}}
        fake_auth.login(eop_peer_advisor_uid)
        own_notes = client.get(f'/api/peer_advisor/{eop_peer_advisor_uid}/notes').json['notes']
        assert next(n for n in own_notes if n['id'] == note.id)['taggedUsers'] == expected
        fake_auth.login(eop_manager_uid)
        department_notes = client.get(f'/api/peer_advising/{_eop_id()}/notes').json['notes']
        assert next(n for n in department_notes if n['id'] == note.id)['taggedUsers'] == expected

    def test_peer_lists_resolve_comment_tags_once(self, app, client, fake_auth, monkeypatch):
        """The peer note lists name the tags of every note and its comments with one lookup, not one per note."""
        expected = {advisor_uid: {'name': _name(app, advisor_uid)}}
        note_ids = []
        for _ in range(2):
            note = _create_note(
                eop_peer_advisor_uid,
                _tag(advisor_uid),
                author_dept_codes=('ZCEEE',),
                peer_advising_department_id=_eop_id(),
            )
            _create_note(
                eop_peer_advisor_uid,
                _tag(advisor_uid),
                author_dept_codes=('ZCEEE',),
                parent_note_id=note.id,
                peer_advising_department_id=_eop_id(),
            )
            note_ids.append(note.id)
        spy = _CallSpy(AuthorizedUser.get_existing_uids)
        monkeypatch.setattr(AuthorizedUser, 'get_existing_uids', spy)
        fake_auth.login(eop_manager_uid)
        department_notes = client.get(f'/api/peer_advising/{_eop_id()}/notes').json['notes']
        assert spy.calls == 1
        for note_id in note_ids:
            listed = next(n for n in department_notes if n['id'] == note_id)
            assert listed['taggedUsers'] == expected
            assert listed['comments'][0]['taggedUsers'] == expected
        spy.calls = 0
        response = client.post(
            '/api/peer_advising/notes/authored_by',
            content_type='application/json',
            data=json.dumps({'peerAdvisingDepartmentId': _eop_id(), 'uid': eop_peer_advisor_uid, 'timeframe': None}),
        )
        assert response.status_code == 200
        assert spy.calls == 1
        for note_id in note_ids:
            listed = next(n for n in response.json if n['id'] == note_id)
            assert listed['comments'][0]['taggedUsers'] == expected

    def test_peer_notes_authored_by_have_tagged_users(self, app, client, fake_auth):
        """The notes-authored-by list, which builds its notes by hand, includes tagged names too."""
        note = _create_note(
            eop_peer_advisor_uid,
            _tag(advisor_uid),
            author_dept_codes=('ZCEEE',),
            peer_advising_department_id=_eop_id(),
        )
        fake_auth.login(eop_manager_uid)
        response = client.post(
            '/api/peer_advising/notes/authored_by',
            content_type='application/json',
            data=json.dumps({'peerAdvisingDepartmentId': _eop_id(), 'uid': eop_peer_advisor_uid, 'timeframe': None}),
        )
        assert response.status_code == 200
        listed = next(n for n in response.json if n['id'] == note.id)
        assert listed['taggedUsers'] == {advisor_uid: {'name': _name(app, advisor_uid)}}


def _api_comment(client, endpoint, data):
    response = client.post(endpoint, buffered=True, content_type='multipart/form-data', data=data)
    assert response.status_code == 200
    return response.json


# An appointment that exists for the fixture student in the data loch fixtures.
APPOINTMENT_PARENT_ID = '11667051-00010'


@pytest.mark.usefixtures('db_session')
class TestExternalCommentTaggedUsers:
    """The taggedUsers map in appointment and eForm comment JSON."""

    def test_create_returns_tagged_users(self, app, client, fake_auth):
        """Creating an appointment comment answers with the names behind its tags."""
        fake_auth.login(director_uid)
        api_json = _api_comment(client, '/api/comments/create', {
            'parentType': 'appointment',
            'parentId': APPOINTMENT_PARENT_ID,
            'body': _tag(advisor_uid),
        })
        assert api_json['taggedUsers'] == {advisor_uid: {'name': _name(app, advisor_uid)}}

    def test_update_returns_tagged_users(self, app, client, fake_auth):
        """Editing a comment answers with the names for its new tags only."""
        fake_auth.login(director_uid)
        created = _api_comment(client, '/api/comments/create', {
            'parentType': 'appointment',
            'parentId': APPOINTMENT_PARENT_ID,
            'body': _tag(advisor_uid),
        })
        updated = _api_comment(client, '/api/comments/update', {'id': created['id'], 'body': _tag(ce3_advisor_uid)})
        assert updated['taggedUsers'] == {ce3_advisor_uid: {'name': _name(app, ce3_advisor_uid)}}

    def test_timeline_comments_have_tagged_users(self, app, client, fake_auth):
        """Comments on a timeline appointment carry their tagged names."""
        fake_auth.login(director_uid)
        _api_comment(client, '/api/comments/create', {
            'parentType': 'appointment',
            'parentId': APPOINTMENT_PARENT_ID,
            'body': _tag(advisor_uid),
        })
        response = client.get(f'/api/student/by_sid/{student_sid}')
        assert response.status_code == 200
        appointment = next(a for a in response.json['notifications']['appointment'] if str(a['id']) == APPOINTMENT_PARENT_ID)
        assert appointment['comments'][0]['taggedUsers'] == {advisor_uid: {'name': _name(app, advisor_uid)}}


@pytest.mark.usefixtures('db_session')
class TestTaggedNamesInExports:
    """Downloads show @Name where the stored body holds @<UID>."""

    def test_notes_zip_shows_names(self, app, client, fake_auth):
        """The notes zip's CSV shows a tagged person's name, and leaves other @digits text alone."""
        _create_note(director_uid, f'<p>Ask @{advisor_uid} and @{NOT_A_USER_UID}</p>', sid=DOWNLOAD_STUDENT_SID)
        fake_auth.login(director_uid)
        # This student's legacy attachment is the one the S3 mock serves, as in the existing download tests.
        with mock_sis_note_attachment(app):
            response = client.get(f'/api/notes/{DOWNLOAD_STUDENT_SID}/download')
        assert response.status_code == 200
        with zipfile.ZipFile(io.BytesIO(response.data)) as archive:
            csv_name = next(name for name in archive.namelist() if name.endswith('.csv'))
            csv_text = archive.read(csv_name).decode('utf-8')
        assert f'@{_name(app, advisor_uid)}' in csv_text
        assert f'@{advisor_uid}' not in csv_text
        assert f'@{NOT_A_USER_UID}' in csv_text

    def test_peer_csv_shows_names(self, app, client, fake_auth):
        """The peer advising notes CSV shows a tagged person's name instead of their UID."""
        _create_note(
            eop_peer_advisor_uid,
            _tag(advisor_uid),
            author_dept_codes=('ZCEEE',),
            peer_advising_department_id=_eop_id(),
        )
        fake_auth.login(eop_manager_uid)
        response = client.post(f'/api/peer_advising/{_eop_id()}/notes/csv')
        assert response.status_code == 200
        csv_text = response.data.decode('utf-8')
        assert f'@{_name(app, advisor_uid)}' in csv_text
        assert f'@{advisor_uid}' not in csv_text
