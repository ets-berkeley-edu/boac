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

from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_attachment import NoteAttachment
import pytest
import simplejson as json
from tests.util import mock_advising_note_s3_bucket, mock_legacy_note_attachment

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

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
        assert _api_note_create(
            app,
            client,
            author_id=advisor.id,
            sid=student['sid'],
            subject='Rusholme Ruffians',
            body='This is the last night of the fair, And the grease in the hair',
            expected_status_code=401,
        )

    def test_admin_user_is_not_authorized(self, app, client, fake_auth):
        """Returns 401 if user is an admin."""
        fake_auth.login(admin_uid)
        admin = AuthorizedUser.find_by_uid(admin_uid)
        assert _api_note_create(
            app,
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
            app,
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

    def test_create_note_with_topics(self, app, client, fake_auth):
        """Create a note with topics."""
        fake_auth.login(coe_advisor_uid)
        note = _api_note_create(
            app,
            client,
            author_id=AuthorizedUser.find_by_uid(coe_advisor_uid).id,
            sid=student['sid'],
            subject='Incubate transparent web services',
            body='Facilitate value-added initiatives',
            topics=['collaborative synergies', 'integrated architectures', 'vertical solutions'],
        )
        assert len(note.get('topics')) == 3
        assert note.get('topics')[0] == 'Collaborative Synergies'
        assert note.get('topics')[1] == 'Integrated Architectures'
        assert note.get('topics')[2] == 'Vertical Solutions'

    def test_create_note_with_attachments(self, app, client, fake_auth):
        """Create a note, with two attachments."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            app,
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

    def test_add_attachment(self, app, client, fake_auth):
        """Add an attachment to an existing note."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            app,
            client,
            author_id=AuthorizedUser.find_by_uid(coe_advisor_uid).id,
            sid=student['sid'],
            subject='No attachments yet',
            body='I travel light',
        )
        note_id = note['id']
        with mock_advising_note_s3_bucket(app):
            data = {}
            data['attachment[0]'] = open(f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt', 'rb')
            response = client.post(
                f'/api/notes/{note_id}/attachment',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
        assert response.status_code == 200
        assert len(response.json['attachments']) == 1
        assert response.json['attachments'][0]['filename'] == 'mock_advising_note_attachment_1.txt'

    def test_remove_attachment(self, app, client, fake_auth):
        """Remove an attachment from an existing note."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            app,
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
        note_id = note['id']
        id_to_delete = note['attachments'][0]['id']
        id_to_keep = note['attachments'][1]['id']
        delete_response = client.delete(f'/api/notes/{note_id}/attachment/{id_to_delete}')
        assert delete_response.status_code == 200
        assert len(delete_response.json['attachments']) == 1
        assert delete_response.json['attachments'][0]['filename'] == 'mock_advising_note_attachment_2.txt'
        notes = _get_notes(client, student['uid'])
        match = next((n for n in notes if n['id'] == note_id), None)
        assert len(match.get('attachments')) == 1
        assert match['attachments'][0]['id'] == id_to_keep
        assert match['attachments'][0]['filename'] == 'mock_advising_note_attachment_2.txt'


class TestMarkNoteRead:

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.post('/api/notes/11667051-00001/mark_read').status_code == 401

    def test_mark_note_read(self, app, client, fake_auth):
        """Marks a note as read."""
        fake_auth.login(coe_advisor_uid)
        all_notes_unread = _get_notes(client, 61889)
        assert len(all_notes_unread) == 5
        for note in all_notes_unread:
            assert note['read'] is False
        response = client.post('/api/notes/11667051-00001/mark_read')
        assert response.status_code == 201

        non_legacy_note_id = all_notes_unread[2]['id']
        response = client.post(f'/api/notes/{non_legacy_note_id}/mark_read')
        assert response.status_code == 201

        response = client.post('/api/notes/11667051-139379/mark_read')
        assert response.status_code == 201

        all_notes_after_read = _get_notes(client, 61889)
        assert len(all_notes_after_read) == 5
        assert all_notes_after_read[0]['id'] == '11667051-00001'
        assert all_notes_after_read[0]['read'] is True
        assert all_notes_after_read[1]['id'] == '11667051-00002'
        assert all_notes_after_read[1]['read'] is False
        assert all_notes_after_read[2]['id'] == non_legacy_note_id
        assert all_notes_after_read[2]['read'] is True
        assert all_notes_after_read[3]['id'] == '11667051-139362'
        assert all_notes_after_read[3]['read'] is False
        assert all_notes_after_read[4]['id'] == '11667051-139379'
        assert all_notes_after_read[4]['read'] is True


class TestUpdateNotes:

    @classmethod
    def _api_note_update(
            cls,
            app,
            client,
            note_id,
            subject,
            body,
            topics=(),
            attachments=(),
            delete_attachment_ids=(),
            expected_status_code=200,
    ):
        with mock_advising_note_s3_bucket(app):
            data = {
                'id': note_id,
                'subject': subject,
                'body': body,
                'topics': ','.join(topics),
                'deleteAttachmentIds': delete_attachment_ids or [],
            }
            for index, path in enumerate(attachments):
                data[f'attachment[{index}]'] = open(path, 'rb')
            response = client.post(
                '/api/notes/update',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
            assert response.status_code == expected_status_code
            return response.json

    def test_note_update_not_authenticated(self, app, coe_advising_note_with_attachment, client):
        """Returns 401 if not authenticated."""
        self._api_note_update(
            app,
            client,
            note_id=coe_advising_note_with_attachment.id,
            subject='Hack the subject!',
            body='Hack the body!',
            expected_status_code=401,
        )

    def test_unauthorized_update_note(self, app, client, fake_auth, new_coe_note):
        """Forbidden to edit someone else's note."""
        original_subject = new_coe_note.subject
        fake_auth.login(asc_advisor_uid)
        assert self._api_note_update(
            app,
            client,
            note_id=new_coe_note.id,
            subject='Hack someone else\'s subject!',
            body='Hack someone else\'s body!',
            expected_status_code=403,
        )
        assert Note.find_by_id(note_id=new_coe_note.id).subject == original_subject

    def test_update_note(self, app, client, fake_auth, new_coe_note):
        """Successfully modifies a note subject and body."""
        fake_auth.login(new_coe_note.author_uid)
        expected_subject = 'There must have been a plague of them'
        expected_body = 'They were guzzling marshmallows'
        updated_note_response = self._api_note_update(
            app,
            client,
            note_id=new_coe_note.id,
            subject=expected_subject,
            body=expected_body,
        )
        assert updated_note_response['read'] is True
        updated_note = Note.find_by_id(note_id=new_coe_note.id)
        assert updated_note.subject == expected_subject
        assert updated_note.body == expected_body

    def test_update_note_with_topics(self, app, client, fake_auth, new_coe_note, asc_advising_note):
        """Update a note: delete existing topic and add a new one."""
        fake_auth.login(asc_advising_note.author_uid)
        expected_topics = ['no color no contrast', 'joyful mask']
        updated_note_response = self._api_note_update(
            app,
            client,
            note_id=asc_advising_note.id,
            subject=asc_advising_note.subject,
            body=asc_advising_note.body,
            topics=expected_topics,
        )
        assert updated_note_response['read'] is True
        assert len(updated_note_response['topics']) == 2
        assert updated_note_response['topics'][0] == 'No Color No Contrast'
        assert updated_note_response['topics'][1] == 'Joyful Mask'
        updated_note = Note.find_by_id(note_id=asc_advising_note.id)
        assert len(updated_note.topics) == 2

    def test_update_note_with_attachments(self, app, client, coe_advising_note_with_attachment, fake_auth):
        """Update a note: delete existing attachment and add a new one."""
        fake_auth.login(coe_advising_note_with_attachment.author_uid)
        base_dir = app.config['BASE_DIR']
        note_id = coe_advising_note_with_attachment.id
        attachment_id = coe_advising_note_with_attachment.attachments[0].id
        filename = 'mock_advising_note_attachment_2.txt'
        path_to_new_attachment = f'{base_dir}/fixtures/{filename}'
        updated_note = self._api_note_update(
            app,
            client,
            note_id=note_id,
            subject=coe_advising_note_with_attachment.subject,
            body=coe_advising_note_with_attachment.body,
            attachments=[path_to_new_attachment],
            delete_attachment_ids=[attachment_id],
        )
        assert note_id == updated_note['attachments'][0]['noteId']
        assert len(updated_note['attachments']) == 1
        assert filename == updated_note['attachments'][0]['displayName']
        assert filename == updated_note['attachments'][0]['filename']
        assert updated_note['attachments'][0]['id'] != attachment_id
        # Verify db
        attachments = NoteAttachment.find_by_note_id(note_id)
        assert len(attachments) == 1
        assert filename in attachments[0].path_to_attachment
        assert not NoteAttachment.find_by_id(attachment_id)


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

    def test_delete_note_with_topics(self, app, client, fake_auth):
        """Delete a note with topics."""
        fake_auth.login(coe_advisor_uid)
        note = _api_note_create(
            app,
            client,
            author_id=AuthorizedUser.find_by_uid(coe_advisor_uid).id,
            sid=student['sid'],
            subject='Recontextualize open-source supply-chains',
            body='Conveniently repurpose enterprise-wide action items',
            topics=['strategic interfaces'],
        )
        note_id = note.get('id')
        # Log in as Admin and delete the note
        fake_auth.login(admin_uid)
        note_id = note['id']
        response = client.delete(f'/api/notes/delete/{note_id}')
        assert response.status_code == 200
        # TODO: add deleted_at column to NoteTopic and populate it when parent Note is deleted.
        # assert not NoteTopic.find_by_note_id(note_id)

    def test_delete_note_with_attachments(self, app, client, fake_auth):
        """Delete a note with two attachments."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note = _api_note_create(
            app,
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

    def test_edit_note_feature_flag_false(self, app, asc_advising_note, client, fake_auth):
        """Returns 404 if feature flag is false. TODO: Remove when feature is live."""
        app.config['FEATURE_FLAG_EDIT_NOTES'] = False
        fake_auth.login(asc_advising_note.author_uid)
        data = {
            'id': asc_advising_note.id,
            'subject': 'Reel Around the Fountain',
            'body': 'You took a child and you made him old',
        }
        response = client.post('/api/notes/update', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 404

    def test_delete_note_feature_flag_false(self, app, asc_advising_note, client, fake_auth):
        """Returns 404 if feature flag is false. TODO: Remove when feature is live."""
        app.config['FEATURE_FLAG_EDIT_NOTES'] = False
        fake_auth.login(asc_advising_note.author_uid)
        response = client.delete(f'/api/notes/delete/{asc_advising_note.id}')
        assert response.status_code == 404


class TestStreamNoteAttachments:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/notes/attachment/9000000000_00002_1.pdf').status_code == 401

    def test_stream_attachment(self, app, client, fake_auth):
        with mock_legacy_note_attachment(app):
            fake_auth.login(coe_advisor_uid)
            response = client.get('/api/notes/attachment/9000000000_00002_1.pdf')
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'application/octet-stream'
            assert response.headers['Content-Disposition'] == "attachment; filename*=UTF-8''dog_eaten_homework.pdf"
            assert response.data == b'When in the course of human events, it becomes necessarf arf woof woof woof'

    def test_stream_attachment_reports_unauthorized_files_not_found(self, app, client, fake_auth):
        with mock_legacy_note_attachment(app):
            fake_auth.login(asc_advisor_uid)
            response = client.get('/api/notes/attachment/9000000000_00002_1.pdf')
            assert response.status_code == 404
            assert response.data == b'Sorry, attachment not available.'

    def test_stream_attachment_reports_missing_files_not_found(self, app, client, fake_auth):
        with mock_legacy_note_attachment(app):
            fake_auth.login(asc_advisor_uid)
            response = client.get('/api/notes/attachment/h0ax.lol')
            assert response.status_code == 404
            assert response.data == b'Sorry, attachment not available.'


def _get_notes(client, uid):
    response = client.get(f'/api/student/{uid}')
    assert response.status_code == 200
    return response.json['notifications']['note']


def _asc_note_with_attachment():
    for note in Note.get_notes_by_sid('11667051'):
        if len(note.attachments):
            return note
    return None


def _api_note_create(app, client, author_id, sid, subject, body, topics=(), attachments=(), expected_status_code=200):
    with mock_advising_note_s3_bucket(app):
        data = {
            'authorId': author_id,
            'sid': sid,
            'subject': subject,
            'body': body,
            'topics': ','.join(topics),
        }
        for index, path in enumerate(attachments):
            data[f'attachment[{index}]'] = open(path, 'rb')
        response = client.post(
            '/api/notes/create',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json
