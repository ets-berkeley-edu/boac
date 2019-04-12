"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_attachment import NoteAttachment
import pytest
import simplejson as json
from tests.util import mock_advising_note_attachment

asc_advisor_uid = '6446'
coe_advisor_uid = '1133399'
admin_uid = '2040'

student = {
    'sid': '11667051',
    'uid': '61889',
}


@pytest.fixture()
def new_coe_note():
    return Note.create(
        author_uid=coe_advisor_uid,
        author_name='Balloon Man',
        author_role='Spherical',
        author_dept_codes='PHYSI',
        sid=student['sid'],
        subject='I was walking up Sixth Avenue',
        body='He spattered me with tomatoes, Hummus, chick peas',
    )


class TestCreateNotes:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
        assert _api_note_create(
            client,
            author_id=advisor.id,
            sid=student['sid'],
            subject='Rusholme Ruffians',
            body='This is the last night of the fair, And the grease in the hair',
            expected_status_code=401,
        )

    def test_admin_user_is_not_authorized(self, client, fake_auth):
        """Returns 401 if user is an admin."""
        fake_auth.login(admin_uid)
        admin = AuthorizedUser.find_by_uid(admin_uid)
        assert _api_note_create(
            client,
            author_id=admin.id,
            sid=student['sid'],
            subject='Rusholme Ruffians',
            body='This is the last night of the fair, And the grease in the hair',
            expected_status_code=403,
        )

    def test_create_note(self, app, client, fake_auth):
        """Create a note."""
        fake_auth.login(coe_advisor_uid)
        advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
        subject = 'Vicar in a Tutu'
        new_note = _api_note_create(
            client,
            author_id=advisor.id,
            sid=student['sid'],
            subject=subject,
            body='A scanty bit of a thing with a decorative ring',
        )
        note_id = new_note.get('id')
        assert new_note['read'] is True
        assert isinstance(note_id, int) and note_id > 0
        assert new_note['author']['uid'] == coe_advisor_uid
        assert 'name' in new_note['author']
        assert new_note['author']['role'] == 'Advisor'
        assert new_note['author']['departments'][0]['name'] == 'College of Engineering'
        # Get notes per SID and compare
        notes = _get_notes(client, student['uid'])
        match = next((n for n in notes if n['id'] == note_id), None)
        assert match and match['subject'] == subject

    def test_create_note_with_attachments(self, app, client, fake_auth):
        """Create a note, with two attachments."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            client,
            author_id=AuthorizedUser.find_by_uid(coe_advisor_uid).id,
            sid=student['sid'],
            subject='I come with attachments',
            body='I come correct',
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
        )
        assert len(note.get('attachments')) == 2


class TestMarkNoteRead:

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.post('/api/notes/11667051-00001/mark_read').status_code == 401

    def test_mark_note_read(self, app, client, fake_auth):
        """Marks a note as read."""
        fake_auth.login(coe_advisor_uid)
        all_notes_unread = _get_notes(client, 61889)
        assert len(all_notes_unread) == 4
        for note in all_notes_unread:
            assert note['read'] is False
        response = client.post('/api/notes/11667051-00001/mark_read')
        assert response.status_code == 201

        non_legacy_note_id = all_notes_unread[3]['id']
        response = client.post(f'/api/notes/{non_legacy_note_id}/mark_read')
        assert response.status_code == 201

        all_notes_one_read = _get_notes(client, 61889)
        assert len(all_notes_one_read) == 4
        assert all_notes_one_read[0]['id'] == '11667051-00001'
        assert all_notes_one_read[0]['read'] is True
        assert all_notes_one_read[1]['id'] == '11667051-00002'
        assert all_notes_one_read[1]['read'] is False
        assert all_notes_one_read[3]['id'] == non_legacy_note_id
        assert all_notes_one_read[3]['read'] is True


class TestUpdateNotes:

    @classmethod
    def _api_note_update(
            cls,
            client,
            note_id,
            subject,
            body,
            attachments=(),
            delete_attachment_ids=(),
            expected_status_code=200,
    ):
        response = client.post(
            '/api/notes/update',
            buffered=True,
            content_type='multipart/form-data',
            data={
                'id': note_id,
                'subject': subject,
                'body': body,
                'deleteAttachmentIds': list(delete_attachment_ids),
                'file[]': [open(file, 'rb') for file in attachments],
            },
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_note_update_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        note = Note.find_by_id(note_id=1)
        assert note
        assert self._api_note_update(
            client,
            note_id=note.id,
            subject='Hack the subject!',
            body='Hack the body!',
            expected_status_code=401,
        )

    def test_unauthorized_update_note(self, client, fake_auth, new_coe_note):
        """Forbidden to edit someone else's note."""
        original_subject = new_coe_note.subject
        fake_auth.login(asc_advisor_uid)
        assert self._api_note_update(
            client,
            note_id=new_coe_note.id,
            subject='Hack someone else\'s subject!',
            body='Hack someone else\'s body!',
            expected_status_code=403,
        )
        assert Note.find_by_id(note_id=new_coe_note.id).subject == original_subject

    def test_update_note(self, client, fake_auth, new_coe_note):
        """Successfully modifies a note subject and body."""
        fake_auth.login(new_coe_note.author_uid)
        expected_subject = 'There must have been a plague of them'
        expected_body = 'They were guzzling marshmallows'
        updated_note_response = self._api_note_update(
            client,
            note_id=new_coe_note.id,
            subject=expected_subject,
            body=expected_body,
        )
        assert updated_note_response['read'] is True
        updated_note = Note.find_by_id(note_id=new_coe_note.id)
        assert updated_note.subject == expected_subject
        assert updated_note.body == expected_body

    def test_update_note_with_attachments(self, app, client, fake_auth):
        """Create a note, with two attachments."""
        fake_auth.login(coe_advisor_uid)
        coe_advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            client,
            author_id=coe_advisor.id,
            sid='11667051',
            subject='My favourite buildings stretch upwards for miles',
            body='Like oak leaves in autumn, cascading on stiles',
            attachments=(
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
            ),
        )
        assert len(note['attachments']) == 1
        original_attachment_id = note['attachments'][0]['id']
        # Now remove one attachment
        updated_note = self._api_note_update(
            client,
            note_id=note['id'],
            subject=note['subject'],
            body=note['body'],
            attachments=[f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt'],
            delete_attachment_ids=[original_attachment_id],
        )
        assert len(updated_note['attachments']) == 1
        assert updated_note['attachments'][0]['id'] != original_attachment_id
        assert 'mock_advising_note_attachment_2.txt' in updated_note['attachments'][0]['filename']


class TestDeleteNote:
    """Delete note API."""

    def test_not_authenticated(self, client):
        """You must log in to delete a note."""
        response = client.delete('/api/notes/delete/123')
        assert response.status_code == 401

    def test_unauthorized(self, client, fake_auth, new_coe_note):
        """Advisor cannot delete the note of another."""
        fake_auth.login('6446')
        response = client.delete(f'/api/notes/delete/{new_coe_note.id}')
        assert response.status_code == 403
        assert Note.find_by_id(new_coe_note.id)

    def test_advisor_cannot_delete(self, client, fake_auth, new_coe_note):
        """Advisor cannot delete her own note."""
        fake_auth.login(new_coe_note.author_uid)
        response = client.delete(f'/api/notes/delete/{new_coe_note.id}')
        assert response.status_code == 403
        assert Note.find_by_id(new_coe_note.id)

    def test_admin_delete(self, client, fake_auth, new_coe_note):
        """Admin can delete another user's note."""
        original_count_per_sid = len(Note.get_notes_by_sid(new_coe_note.sid))
        fake_auth.login(admin_uid)
        note_id = new_coe_note.id
        response = client.delete(f'/api/notes/delete/{note_id}')
        assert response.status_code == 200
        assert not Note.find_by_id(note_id)
        assert 1 == original_count_per_sid - len(Note.get_notes_by_sid(new_coe_note.sid))
        assert not Note.update(note_id, 'Deleted note cannot be updated', 'Ditto')

    def test_delete_note_with_attachments(self, app, client, fake_auth):
        """Create a note, with two attachments."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            client,
            author_id=AuthorizedUser.find_by_uid(coe_advisor_uid).id,
            sid=student['sid'],
            subject='My little dog Lassie packed her bags and went out on to the porch',
            body='Then my little dog Lassie, she sailed off to the moon',
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
        )
        attachment_ids = [a['id'] for a in note.get('attachments')]
        assert len(attachment_ids) == 2
        assert NoteAttachment.find_by_id(attachment_ids[0]) and NoteAttachment.find_by_id(attachment_ids[1])

        # Log in as Admin and delete the note
        fake_auth.login(admin_uid)
        note_id = note['id']
        response = client.delete(f'/api/notes/delete/{note_id}')
        assert response.status_code == 200
        assert not NoteAttachment.find_by_id(attachment_ids[0])
        assert not NoteAttachment.find_by_id(attachment_ids[1])


class TestEditNoteFeatureFlag:

    def test_create_note_feature_flag_false(self, app, client, fake_auth):
        """Returns 404 if feature flag is false."""
        app.config['FEATURE_FLAG_EDIT_NOTES'] = False
        fake_auth.login(coe_advisor_uid)
        assert 404 == client.post(
            '/api/notes/create',
            buffered=True,
            content_type='multipart/form-data',
            data={
                'sid': student['sid'],
                'subject': 'A dreaded sunny day',
                'body': 'So I meet you at the cemetry gates',
            },
        ).status_code

    def test_edit_note_feature_flag_false(self, app, client, fake_auth):
        """Returns 404 if feature flag is false. TODO: Remove when feature is live."""
        app.config['FEATURE_FLAG_EDIT_NOTES'] = False
        note = Note.find_by_id(note_id=1)
        fake_auth.login(note.author_uid)
        data = {
            'id': note.id,
            'subject': 'Reel Around the Fountain',
            'body': 'You took a child and you made him old',
        }
        response = client.post('/api/notes/update', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 404

    def test_delete_note_feature_flag_false(self, app, client, fake_auth):
        """Returns 404 if feature flag is false. TODO: Remove when feature is live."""
        app.config['FEATURE_FLAG_EDIT_NOTES'] = False
        note = Note.find_by_id(note_id=1)
        fake_auth.login(note.author_uid)
        response = client.delete(f'/api/notes/delete/{note.id}')
        assert response.status_code == 404


class TestStreamNoteAttachments:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/notes/attachment/legacy/9000000000_00002_1.pdf').status_code == 401

    def test_stream_attachment(self, app, client, fake_auth):
        with mock_advising_note_attachment(app):
            fake_auth.login(coe_advisor_uid)
            response = client.get('/api/notes/attachment/legacy/9000000000_00002_1.pdf')
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'application/octet-stream'
            assert response.headers['Content-Disposition'] == 'attachment; filename=dog_eaten_homework.pdf'
            assert response.data == b'When in the course of human events, it becomes necessarf arf woof woof woof'

    def test_stream_attachment_reports_unauthorized_files_not_found(self, app, client, fake_auth):
        with mock_advising_note_attachment(app):
            fake_auth.login(asc_advisor_uid)
            response = client.get('/api/notes/attachment/legacy/9000000000_00002_1.pdf')
            assert response.status_code == 404

    def test_stream_attachment_reports_missing_files_not_found(self, app, client, fake_auth):
        with mock_advising_note_attachment(app):
            fake_auth.login(asc_advisor_uid)
            response = client.get('/api/notes/attachment/legacy/h0ax.lol')
            assert response.status_code == 404


class TestUploadNoteAttachment:
    """Note Attachment API."""

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        note_id = _asc_note_with_attachment().id
        file = (io.BytesIO(b'A bad seed.'), 'hack-S3-with-my-evil-attachment.txt')
        assert _api_attachment_upload(client, note_id, file).status_code == 401

    def test_unauthorized(self, app, client, fake_auth):
        """Returns 403 if user does not own the note."""
        fake_auth.login(coe_advisor_uid)
        note_id = _asc_note_with_attachment().id
        file = (io.BytesIO(b'Not me.'), 'attach-to-the-note-of-another.txt')
        assert _api_attachment_upload(client, note_id, file).status_code == 403

    def test_invalid_file(self, app, client, fake_auth):
        """Returns XXX if file is incomplete or missing."""
        fake_auth.login(asc_advisor_uid)
        note_id = _asc_note_with_attachment().id
        file = (io.BytesIO(b'Not me.'), '   ')
        assert _api_attachment_upload(client, note_id, file).status_code == 400

    def test_valid_upload(self, app, client, fake_auth):
        """Successfully put attachment to existing note."""
        fake_auth.login(asc_advisor_uid)
        note_id = _asc_note_with_attachment().id
        filename = 'expect-successful-upload.txt'
        file = (io.BytesIO(b'It\'s all good'), filename)
        response = _api_attachment_upload(client, note_id, file)
        assert response.status_code == 200
        note = response.json
        attachment = note.get('attachments')[0]
        attachment_id = attachment['id']
        assert attachment_id > 0
        assert attachment['uploadedBy'] == asc_advisor_uid
        # TODO: Uncomment the following when mock S3 upload is in place
        #     assert attachment['filename'] == filename
        note = Note.find_by_id(note_id)
        assert next((a for a in note.attachments if a.id == attachment_id), None)


class TestDeleteNoteAttachment:
    """Note Attachment API."""

    def test_not_authenticated(self, client):
        """You must log in to delete a note."""
        note = _asc_note_with_attachment()
        assert client.delete(f'/api/notes/attachment/delete/{note.attachments[0].id}').status_code == 401

    def test_current_user_did_not_upload_attachment(self, client, fake_auth, new_coe_note):
        """If the note author did not upload the attachment then s/he cannot delete the attachment."""
        attachment = _asc_note_with_attachment().attachments[0]
        assert attachment.uploaded_by_uid != coe_advisor_uid
        fake_auth.login(coe_advisor_uid)
        assert client.delete(f'/api/notes/attachment/delete/{attachment.id}').status_code == 403

    def test_delete_by_attachment_uploader(self, client, fake_auth, new_coe_note):
        """Attachment uploader can delete the attachment."""
        attachment = _asc_note_with_attachment().attachments[0]
        fake_auth.login(attachment.uploaded_by_uid)
        assert client.delete(f'/api/notes/attachment/delete/{attachment.id}').status_code == 200
        assert not NoteAttachment.find_by_id(attachment.id)

    def test_delete_by_admin(self, client, fake_auth, new_coe_note):
        """Admin can delete all note attachments."""
        attachment = _asc_note_with_attachment().attachments[0]
        assert attachment.uploaded_by_uid != coe_advisor_uid
        fake_auth.login(admin_uid)
        assert client.delete(f'/api/notes/attachment/delete/{attachment.id}').status_code == 200
        assert not NoteAttachment.find_by_id(attachment.id)


def _get_notes(client, uid):
    response = client.get(f'/api/student/{uid}')
    assert response.status_code == 200
    return response.json['notifications']['note']


def _asc_note_with_attachment():
    for note in Note.get_notes_by_sid('11667051'):
        if len(note.attachments):
            return note
    return None


def _api_note_create(client, author_id, sid, subject, body, attachments=(), expected_status_code=200):
    response = client.post(
        '/api/notes/create',
        buffered=True,
        content_type='multipart/form-data',
        data={
            'authorId': author_id,
            'sid': sid,
            'subject': subject,
            'body': body,
            'file[]': [open(path, 'rb') for path in attachments],
        },
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_attachment_upload(client, note_id, file):
    return client.post(
        '/api/notes/attachment/upload',
        buffered=True,
        content_type='multipart/form-data',
        data={
            'noteId': note_id,
            'file': file,
        },
    )
