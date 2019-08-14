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
from boac.models.note_template import NoteTemplate
from boac.models.note_template_attachment import NoteTemplateAttachment
from tests.util import mock_advising_note_s3_bucket

admin_uid = '2040'
coe_advisor_uid = '1133399'
l_s_major_advisor_uid = '242881'


class TestGetNoteTemplate:

    @classmethod
    def _api_note_template(cls, client, note_template_id, expected_status_code=200):
        response = client.get(f'/api/note_template/{note_template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title='Lost cause', subject='Expect 401')
        self._api_note_template(client=client, note_template_id=note_template.id, expected_status_code=401)

    def test_unauthorized(self, app, client, fake_auth):
        """Returns 403 if user did not create the requested note template."""
        fake_auth.login(coe_advisor_uid)
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title='Leggo my eggo', subject='I, me, mine.')
        self._api_note_template(client=client, note_template_id=note_template.id, expected_status_code=403)

    def test_get_note_template_by_id(self, app, client, fake_auth):
        """Returns note template in JSON."""
        fake_auth.login(l_s_major_advisor_uid)
        title = 'Template for success'
        subject = 'Winning!'
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title=title, subject=subject)
        api_json = self._api_note_template(client=client, note_template_id=note_template.id)
        assert api_json.get('id') == note_template.id
        assert api_json.get('title') == title
        assert api_json.get('subject') == subject
        for key in ('attachments', 'body', 'topics', 'createdAt', 'updatedAt'):
            assert key in api_json


class TestMyNoteTemplates:

    @classmethod
    def _api_my_note_templates(cls, client, expected_status_code=200):
        response = client.get(f'/api/note_templates/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_my_note_templates(client=client, expected_status_code=401)

    def test_get_note_template_by_id(self, app, client, fake_auth):
        """Returns note templates created by current user."""
        fake_auth.login(l_s_major_advisor_uid)
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        names = ['Johnny', 'Tommy', 'Joey', 'Dee Dee']
        for i in range(0, 4):
            NoteTemplate.create(creator_id=creator_id, title=f'{names[i]}', subject=f'Subject {i}')
        api_json = self._api_my_note_templates(client=client)
        assert len(api_json) == 4
        assert ['Dee Dee', 'Joey', 'Johnny', 'Tommy'] == [template['title'] for template in api_json]


class TestNoteTemplateCreation:

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        _api_create_note_template(
            app=app,
            client=client,
            title='Keep a knockin\'',
            subject='...but you can\'t come in',
            expected_status_code=401,
        )

    def test_admin_is_unauthorized(self, app, client, fake_auth):
        """Returns 403 if user is an admin."""
        fake_auth.login(admin_uid)
        _api_create_note_template(
            app=app,
            client=client,
            title='Ain\'t gonna happen',
            subject='Sorry \'bout it',
            expected_status_code=403,
        )

    def test_create_note_template(self, app, client, fake_auth):
        """Create a note template."""
        fake_auth.login(coe_advisor_uid)
        title = 'I get it, I got it'
        subject = 'I know it\'s good'
        base_dir = app.config['BASE_DIR']
        api_json = _api_create_note_template(
            app,
            client,
            title=title,
            subject=subject,
            body='The templates I write, you wish you would',
            topics=['collaborative synergies', 'integrated architectures', 'vertical solutions'],
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
        )
        note_template_id = api_json.get('id')
        note_template = NoteTemplate.find_by_id(note_template_id)
        assert note_template_id == note_template.id
        assert title == note_template.title
        assert subject == note_template.subject
        assert len(note_template.topics) == 3
        assert len(note_template.attachments) == 2


class TestDeleteNoteTemplate:
    """Delete note template API."""

    def test_not_authenticated(self, client):
        """You must log in to delete a note."""
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title='Title TK', subject='Little Fury')
        response = client.delete(f'/api/note_template/delete/{note_template.id}')
        assert response.status_code == 401

    def test_unauthorized_note_template_deletion(self, client, fake_auth):
        """Advisor cannot delete another advisor's note template."""
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        note_template = NoteTemplate.create(creator_id=creator_id, title='Pacer', subject='Tipp City')
        fake_auth.login(coe_advisor_uid)
        response = client.delete(f'/api/note_template/delete/{note_template.id}')
        assert response.status_code == 403
        assert NoteTemplate.find_by_id(note_template.id)

    def test_delete_note_template_with_attachments(self, app, client, fake_auth):
        """Delete note template that has an attachment."""
        fake_auth.login(l_s_major_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note_template = _api_create_note_template(
            app,
            client,
            title='Delete me!',
            subject='I want to be free',
            attachments=[f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'],
        )
        assert len(note_template.get('attachments')) == 1
        attachment_id = note_template.get('attachments')[0]['id']
        assert NoteTemplateAttachment.find_by_id(attachment_id)

        note_template_id = note_template['id']
        response = client.delete(f'/api/note_template/delete/{note_template_id}')
        assert response.status_code == 200
        assert not NoteTemplateAttachment.find_by_id(attachment_id)


def _api_create_note_template(
        app,
        client,
        title,
        subject,
        body=None,
        topics=(),
        attachments=(),
        expected_status_code=200,
):
    with mock_advising_note_s3_bucket(app):
        data = {
            'title': title,
            'subject': subject,
            'body': body,
            'topics': ','.join(topics),
        }
        for index, path in enumerate(attachments):
            data[f'attachment[{index}]'] = open(path, 'rb')
        response = client.post(
            '/api/note_template/create',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json
