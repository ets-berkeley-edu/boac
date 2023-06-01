"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.note_template import NoteTemplate
from boac.models.note_template_attachment import NoteTemplateAttachment
import simplejson as json
from sqlalchemy import and_
from tests.util import mock_advising_note_s3_bucket

admin_uid = '2040'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'
coe_advisor_no_advising_data_uid = '1022796'
l_s_major_advisor_uid = '242881'


class TestGetNoteTemplate:

    @classmethod
    def _api_note_template(cls, client, note_template_id, expected_status_code=200):
        response = client.get(f'/api/note_template/{note_template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client, mock_note_template):
        """Returns 401 if not authenticated."""
        self._api_note_template(client=client, note_template_id=mock_note_template.id, expected_status_code=401)

    def test_user_without_advising_data_access(self, client, fake_auth, mock_note_template):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_note_template(client=client, note_template_id=mock_note_template.id, expected_status_code=401)

    def test_unauthorized(self, app, client, fake_auth, mock_note_template):
        """Returns 403 if user did not create the requested note template."""
        fake_auth.login(coe_advisor_uid)
        self._api_note_template(client=client, note_template_id=mock_note_template.id, expected_status_code=403)

    def test_get_note_template_by_id(self, app, client, fake_auth, mock_note_template):
        """Returns note template in JSON."""
        fake_auth.login(l_s_major_advisor_uid)
        api_json = self._api_note_template(client=client, note_template_id=mock_note_template.id)
        assert api_json.get('id') == mock_note_template.id
        assert api_json.get('title') == mock_note_template.title
        assert api_json.get('subject') == mock_note_template.subject
        for key in ('attachments', 'body', 'topics', 'createdAt', 'updatedAt'):
            assert key in api_json


class TestMyNoteTemplates:

    @classmethod
    def _api_my_note_templates(cls, client, expected_status_code=200):
        response = client.get('/api/note_templates/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_my_note_templates(client=client, expected_status_code=401)

    def test_user_without_advising_data_access(self, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_my_note_templates(client=client, expected_status_code=401)

    def test_get_note_template_by_id(self, app, client, fake_auth):
        """Returns note templates created by current user."""
        fake_auth.login(l_s_major_advisor_uid)
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        names = ['Johnny', 'Tommy', 'Joey', 'Dee Dee']
        for i in range(0, 4):
            NoteTemplate.create(creator_id=creator_id, title=f'{names[i]}', subject=f'Subject {i}')
        api_json = self._api_my_note_templates(client=client)
        expected_order = [template['title'] for template in api_json]
        expected_order.sort()
        assert expected_order == [template['title'] for template in api_json]


class TestCreateNoteTemplate:

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        _api_create_note_template(
            client=client,
            expected_status_code=401,
            note_id=1,
            title='Keep a knockin\'',
        )

    def test_admin_is_unauthorized(self, app, client, fake_auth):
        """Returns 403 if user is an admin."""
        fake_auth.login(admin_uid)
        _api_create_note_template(
            client=client,
            expected_status_code=403,
            note_id=1,
            title='Ain\'t gonna happen',
        )

    def test_user_without_advising_data_access(self, app, client, fake_auth, mock_note_draft):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        _api_create_note_template(
            client=client,
            expected_status_code=401,
            note_id=mock_note_draft.id,
            title='Nope',
        )

    def test_create_note_template(self, app, client, fake_auth, mock_advising_note):
        """Create a note template."""
        fake_auth.login(coe_advisor_uid)
        title = 'I get it, I got it'
        api_json = _api_create_note_template(
            client=client,
            note_id=mock_advising_note.id,
            title=title,
        )
        note_template_id = api_json.get('id')
        note_template = NoteTemplate.find_by_id(note_template_id)
        assert note_template_id == note_template.id
        assert note_template.is_private is False
        assert note_template.subject == mock_advising_note.subject
        assert note_template.title == title
        assert len(note_template.topics) == 3
        assert len(note_template.attachments) == 1


class TestUpdateNoteTemplate:

    @classmethod
    def _api_note_template_update(
            cls,
            app,
            client,
            note_template_id,
            subject,
            title,
            attachments=(),
            body=None,
            delete_attachment_ids=(),
            expected_status_code=200,
            is_private=False,
            topics=(),
    ):
        with mock_advising_note_s3_bucket(app):
            data = {
                'deleteAttachmentIds': delete_attachment_ids or [],
                'body': body,
                'id': note_template_id,
                'isPrivate': is_private,
                'subject': subject,
                'topics': ','.join(topics),
                'title': title,
            }
            for index, path in enumerate(attachments):
                data[f'attachment[{index}]'] = open(path, 'rb')
            response = client.post(
                '/api/note_template/update',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
            assert response.status_code == expected_status_code
            return response.json

    def test_note_template_update_not_authenticated(self, app, mock_note_template, client):
        """Returns 401 if not authenticated."""
        self._api_note_template_update(
            app=app,
            client=client,
            expected_status_code=401,
            note_template_id=mock_note_template.id,
            subject='Hack the subject!',
            title='Hack the title!',
        )

    def test_user_without_advising_data_access(self, app, client, fake_auth, mock_note_template):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_note_template_update(
            app=app,
            client=client,
            expected_status_code=401,
            note_template_id=mock_note_template.id,
            subject='Nooooooope',
            title='Nope',
        )

    def test_unauthorized_note_template_update(self, app, client, fake_auth, mock_note_template):
        """Deny user's attempt to edit someone else's note template."""
        original_subject = mock_note_template.subject
        fake_auth.login(coe_advisor_uid)
        assert self._api_note_template_update(
            app=app,
            client=client,
            expected_status_code=403,
            note_template_id=mock_note_template.id,
            subject='Hack the subject!',
            title='Hack the title!',
        )
        assert NoteTemplate.find_by_id(mock_note_template.id).subject == original_subject

    def test_update_note_template_topics(self, app, client, fake_auth, mock_note_template):
        """Update note template topics."""
        user = AuthorizedUser.find_by_id(mock_note_template.creator_id)
        fake_auth.login(user.uid)
        expected_topics = ['this', 'that']
        expected_is_private = not mock_note_template.is_private
        api_json = self._api_note_template_update(
            app=app,
            client=client,
            is_private=expected_is_private,
            note_template_id=mock_note_template.id,
            subject=mock_note_template.subject,
            title=mock_note_template.title,
            topics=expected_topics,
        )
        assert len(api_json['topics']) == 2
        assert sorted(api_json['topics']) == ['That', 'This']
        assert api_json['isPrivate'] is expected_is_private

    def test_remove_note_template_topics(self, app, client, fake_auth, mock_note_template):
        """Delete note template topics."""
        user = AuthorizedUser.find_by_id(mock_note_template.creator_id)
        fake_auth.login(user.uid)
        api_json = self._api_note_template_update(
            app=app,
            body=mock_note_template.body,
            client=client,
            note_template_id=mock_note_template.id,
            subject=mock_note_template.subject,
            title=mock_note_template.title,
            topics=(),
        )
        assert not api_json['topics']

    def test_update_note_template_attachments(self, app, client, fake_auth, mock_note_template):
        """Update note attachments."""
        user = AuthorizedUser.find_by_id(mock_note_template.creator_id)
        fake_auth.login(user.uid)
        base_dir = app.config['BASE_DIR']
        attachment_id = mock_note_template.attachments[0].id
        filename = 'mock_advising_note_attachment_2.txt'
        path_to_new_attachment = f'{base_dir}/fixtures/{filename}'
        updated_note = self._api_note_template_update(
            app=app,
            attachments=[path_to_new_attachment],
            body=mock_note_template.body,
            delete_attachment_ids=[attachment_id],
            client=client,
            note_template_id=mock_note_template.id,
            subject=mock_note_template.subject,
            title=mock_note_template.title,
        )
        assert mock_note_template.id == updated_note['attachments'][0]['noteTemplateId']
        assert len(updated_note['attachments']) == 1
        assert filename == updated_note['attachments'][0]['displayName']
        assert filename == updated_note['attachments'][0]['filename']
        assert updated_note['attachments'][0]['id'] != attachment_id
        # Verify db
        attachments = NoteTemplateAttachment.query.filter(
            and_(
                NoteTemplateAttachment.note_template_id == mock_note_template.id,
                NoteTemplateAttachment.deleted_at == None,  # noqa: E711
            ),
        ).all()
        assert len(attachments) == 1
        assert filename in attachments[0].path_to_attachment
        assert not NoteTemplateAttachment.find_by_id(attachment_id)


class TestRenameNoteTemplate:

    @classmethod
    def _api_note_template_rename(
            cls,
            client,
            note_template_id,
            title,
            expected_status_code=200,
    ):
        response = client.post(
            '/api/note_template/rename',
            data=json.dumps({
                'id': note_template_id,
                'title': title,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_rename_note_template_not_authenticated(self, app, mock_note_template, client):
        """Returns 401 if not authenticated."""
        self._api_note_template_rename(
            client,
            note_template_id=mock_note_template.id,
            title='Hack the title!',
            expected_status_code=401,
        )

    def test_user_without_advising_data_access(self, client, fake_auth, mock_note_template):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_note_template_rename(
            client,
            note_template_id=mock_note_template.id,
            title='Nopity Nope',
            expected_status_code=401,
        )

    def test_rename_note_template_unauthorized(self, app, client, fake_auth, mock_note_template):
        """Deny user's attempt to rename someone else's note template."""
        original_subject = mock_note_template.subject
        fake_auth.login(coe_advisor_uid)
        assert self._api_note_template_rename(
            client,
            note_template_id=mock_note_template.id,
            title='Hack the title!',
            expected_status_code=403,
        )
        assert NoteTemplate.find_by_id(mock_note_template.id).subject == original_subject

    def test_update_note_template_topics(self, app, client, fake_auth, mock_note_template):
        """Update note template title."""
        user = AuthorizedUser.find_by_id(mock_note_template.creator_id)
        fake_auth.login(user.uid)
        expected_title = 'As cool as Kim Deal'
        api_json = self._api_note_template_rename(
            client,
            note_template_id=mock_note_template.id,
            title=expected_title,
        )
        assert api_json['title'] == expected_title
        assert NoteTemplate.find_by_id(mock_note_template.id).title == expected_title


class TestDeleteNoteTemplate:
    """Delete note template API."""

    def test_not_authenticated(self, client, mock_note_template):
        """You must log in to delete a note."""
        response = client.delete(f'/api/note_template/delete/{mock_note_template.id}')
        assert response.status_code == 401

    def test_user_without_advising_data_access(self, client, fake_auth, mock_note_template):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        response = client.delete(f'/api/note_template/delete/{mock_note_template.id}')
        assert response.status_code == 401

    def test_unauthorized_note_template_deletion(self, client, fake_auth, mock_note_template):
        """Advisor cannot delete another advisor's note template."""
        fake_auth.login(coe_advisor_uid)
        response = client.delete(f'/api/note_template/delete/{mock_note_template.id}')
        assert response.status_code == 403
        assert NoteTemplate.find_by_id(mock_note_template.id)

    def test_delete_note_template_with_attachments(self, app, client, fake_auth, mock_note_draft):
        """Delete note template that has an attachment."""
        fake_auth.login(l_s_major_advisor_uid)
        note_template = _api_create_note_template(
            client=client,
            note_id=mock_note_draft.id,
            title='Delete me!',
        )
        assert len(note_template.get('attachments')) == 1
        attachment_id = note_template.get('attachments')[0]['id']
        assert NoteTemplateAttachment.find_by_id(attachment_id)

        note_template_id = note_template['id']
        response = client.delete(f'/api/note_template/delete/{note_template_id}')
        assert response.status_code == 200
        assert not NoteTemplateAttachment.find_by_id(attachment_id)


def _api_create_note_template(client, note_id, title, expected_status_code=200):
    response = client.post(
        '/api/note_template/create',
        content_type='application/json',
        data=json.dumps({'noteId': note_id, 'title': title}),
    )
    assert response.status_code == expected_status_code
    return response.json
