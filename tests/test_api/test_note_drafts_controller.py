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
from boac.models.note_draft import NoteDraft
from boac.models.note_draft_attachment import NoteDraftAttachment
from sqlalchemy import and_
from tests.util import mock_advising_note_s3_bucket

admin_uid = '2040'
ce3_advisor_uid = '2525'
coe_advisor_uid = '1133399'
coe_advisor_no_advising_data_uid = '1022796'
l_s_major_advisor_uid = '242881'


class TestGetNoteDraft:

    @classmethod
    def _api_note_draft(cls, client, note_draft_id, expected_status_code=200):
        response = client.get(f'/api/note_draft/{note_draft_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client, mock_note_draft):
        """Returns 401 if not authenticated."""
        self._api_note_draft(client=client, note_draft_id=mock_note_draft.id, expected_status_code=401)

    def test_user_without_advising_data_access(self, client, fake_auth, mock_note_draft):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_note_draft(client=client, note_draft_id=mock_note_draft.id, expected_status_code=401)

    def test_unauthorized(self, app, client, fake_auth, mock_note_draft):
        """Returns 403 if user did not create the requested note template."""
        fake_auth.login(coe_advisor_uid)
        self._api_note_draft(client=client, note_draft_id=mock_note_draft.id, expected_status_code=403)

    def test_get_note_draft_by_id(self, app, client, fake_auth, mock_note_draft):
        """Returns note template in JSON."""
        fake_auth.login(l_s_major_advisor_uid)
        api_json = self._api_note_draft(client=client, note_draft_id=mock_note_draft.id)
        assert api_json.get('id') == mock_note_draft.id
        assert api_json.get('subject') == mock_note_draft.subject
        for key in ('attachments', 'body', 'topics', 'createdAt', 'updatedAt'):
            assert key in api_json


class TestMyNoteDrafts:

    @classmethod
    def _api_my_note_drafts(cls, client, expected_status_code=200):
        response = client.get('/api/note_drafts/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_my_note_drafts(client=client, expected_status_code=401)

    def test_user_without_advising_data_access(self, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_my_note_drafts(client=client, expected_status_code=401)

    def test_get_note_draft_by_id(self, app, client, fake_auth):
        """Returns note templates created by current user."""
        fake_auth.login(l_s_major_advisor_uid)
        creator_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        for i in range(0, 4):
            NoteDraft.create(
                contact_type=None,
                creator_id=creator_id,
                subject=f'Subject {i}',
                is_private=False,
                set_date=None,
                sids=['11667051'],
            )
        api_json = self._api_my_note_drafts(client=client)
        expected_order = [template['subject'] for template in api_json]
        expected_order.sort()
        assert expected_order == [template['subject'] for template in api_json]


class TestCreateNoteDraft:

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        _api_create_note_draft(
            app=app,
            client=client,
            expected_status_code=401,
            sids=['11667051', '2345678901'],
            subject='...but you can\'t come in',
        )

    def test_admin_is_unauthorized(self, app, client, fake_auth):
        """Returns 403 if user is an admin."""
        fake_auth.login(admin_uid)
        _api_create_note_draft(
            app=app,
            client=client,
            expected_status_code=403,
            sids=['11667051'],
            subject='Sorry \'bout it',
        )

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        _api_create_note_draft(
            app=app,
            client=client,
            expected_status_code=401,
            sids=['11667051'],
            subject='Nooooooope',
        )

    def test_create_note_draft(self, app, client, fake_auth):
        """Create a note template."""
        fake_auth.login(coe_advisor_uid)
        subject = 'I know it\'s good'
        base_dir = app.config['BASE_DIR']
        api_json = _api_create_note_draft(
            app=app,
            attachments=[
                f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt',
                f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt',
            ],
            body='The templates I write, you wish you would',
            client=client,
            sids=['11667051', '2345678901'],
            subject=subject,
            topics=['collaborative synergies', 'integrated architectures', 'vertical solutions'],
        )
        note_draft_id = api_json.get('id')
        note_draft = NoteDraft.find_by_id(note_draft_id)
        assert note_draft_id == note_draft.id
        assert len(note_draft.sids) == 2
        assert subject == note_draft.subject
        assert len(note_draft.topics) == 3
        assert len(note_draft.attachments) == 2


class TestUpdateNoteDraft:

    @classmethod
    def _api_note_draft_update(
            cls,
            app,
            client,
            note_draft_id,
            subject,
            attachments=(),
            body=None,
            delete_attachment_ids=(),
            expected_status_code=200,
            sids=None,
            topics=(),
    ):
        with mock_advising_note_s3_bucket(app):
            data = {
                'deleteAttachmentIds': delete_attachment_ids or [],
                'body': body,
                'id': note_draft_id,
                'sids': sids,
                'subject': subject,
                'topics': ','.join(topics),
            }
            for index, path in enumerate(attachments):
                data[f'attachment[{index}]'] = open(path, 'rb')
            response = client.post(
                '/api/note_draft/update',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
            assert response.status_code == expected_status_code
            return response.json

    def test_note_draft_update_not_authenticated(self, app, mock_note_draft, client):
        """Returns 401 if not authenticated."""
        self._api_note_draft_update(
            app=app,
            client=client,
            expected_status_code=401,
            note_draft_id=mock_note_draft.id,
            subject='Hack the subject!',
        )

    def test_user_without_advising_data_access(self, app, client, fake_auth, mock_note_draft):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._api_note_draft_update(
            app=app,
            client=client,
            expected_status_code=401,
            note_draft_id=mock_note_draft.id,
            subject='Nooooooope',
        )

    def test_unauthorized_note_draft_update(self, app, client, fake_auth, mock_note_draft):
        """Deny user's attempt to edit someone else's note template."""
        original_subject = mock_note_draft.subject
        fake_auth.login(coe_advisor_uid)
        assert self._api_note_draft_update(
            app=app,
            client=client,
            expected_status_code=403,
            note_draft_id=mock_note_draft.id,
            subject='Hack the subject!',
        )
        assert NoteDraft.find_by_id(mock_note_draft.id).subject == original_subject

    def test_update_note_draft_topics(self, app, client, fake_auth, mock_note_draft):
        """Update note template topics."""
        user = AuthorizedUser.find_by_id(mock_note_draft.creator_id)
        fake_auth.login(user.uid)
        expected_topics = ['this', 'that']
        api_json = self._api_note_draft_update(
            app=app,
            client=client,
            note_draft_id=mock_note_draft.id,
            subject=mock_note_draft.subject,
            topics=expected_topics,
        )
        assert len(api_json['topics']) == 2
        assert sorted(api_json['topics']) == ['That', 'This']

    def test_remove_note_draft_topics(self, app, client, fake_auth, mock_note_draft):
        """Delete note template topics."""
        user = AuthorizedUser.find_by_id(mock_note_draft.creator_id)
        fake_auth.login(user.uid)
        api_json = self._api_note_draft_update(
            app=app,
            body=mock_note_draft.body,
            client=client,
            note_draft_id=mock_note_draft.id,
            subject=mock_note_draft.subject,
            topics=(),
        )
        assert not api_json['topics']

    def test_update_note_draft_attachments(self, app, client, fake_auth, mock_note_draft):
        """Update note attachments."""
        user = AuthorizedUser.find_by_id(mock_note_draft.creator_id)
        fake_auth.login(user.uid)
        base_dir = app.config['BASE_DIR']
        attachment_id = mock_note_draft.attachments[0].id
        filename = 'mock_advising_note_attachment_2.txt'
        path_to_new_attachment = f'{base_dir}/fixtures/{filename}'
        updated_note = self._api_note_draft_update(
            app=app,
            attachments=[path_to_new_attachment],
            body=mock_note_draft.body,
            delete_attachment_ids=[attachment_id],
            client=client,
            note_draft_id=mock_note_draft.id,
            subject=mock_note_draft.subject,
        )
        assert mock_note_draft.id == updated_note['attachments'][0]['noteDraftId']
        assert len(updated_note['attachments']) == 1
        assert filename == updated_note['attachments'][0]['displayName']
        assert filename == updated_note['attachments'][0]['filename']
        assert updated_note['attachments'][0]['id'] != attachment_id
        # Verify db
        attachments = NoteDraftAttachment.query.filter(
            and_(
                NoteDraftAttachment.note_draft_id == mock_note_draft.id,
                NoteDraftAttachment.deleted_at == None,  # noqa: E711
            ),
        ).all()
        assert len(attachments) == 1
        assert filename in attachments[0].path_to_attachment
        assert not NoteDraftAttachment.find_by_id(attachment_id)


class TestDeleteNoteDraft:
    """Delete note template API."""

    def test_not_authenticated(self, client, mock_note_draft):
        """You must log in to delete a note."""
        response = client.delete(f'/api/note_draft/delete/{mock_note_draft.id}')
        assert response.status_code == 401

    def test_user_without_advising_data_access(self, client, fake_auth, mock_note_draft):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        response = client.delete(f'/api/note_draft/delete/{mock_note_draft.id}')
        assert response.status_code == 401

    def test_unauthorized_note_draft_deletion(self, client, fake_auth, mock_note_draft):
        """Advisor cannot delete another advisor's note template."""
        fake_auth.login(coe_advisor_uid)
        response = client.delete(f'/api/note_draft/delete/{mock_note_draft.id}')
        assert response.status_code == 403
        assert NoteDraft.find_by_id(mock_note_draft.id)

    def test_delete_note_draft_with_attachments(self, app, client, fake_auth):
        """Delete note template that has an attachment."""
        fake_auth.login(l_s_major_advisor_uid)
        base_dir = app.config['BASE_DIR']
        note_draft = _api_create_note_draft(
            app=app,
            attachments=[f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt'],
            client=client,
            sids=['11667051'],
            subject='I want to be free',
        )
        assert len(note_draft.get('attachments')) == 1
        attachment_id = note_draft.get('attachments')[0]['id']
        assert NoteDraftAttachment.find_by_id(attachment_id)

        note_draft_id = note_draft['id']
        response = client.delete(f'/api/note_draft/delete/{note_draft_id}')
        assert response.status_code == 200
        assert not NoteDraftAttachment.find_by_id(attachment_id)


def _api_create_note_draft(
        app,
        client,
        sids,
        subject,
        attachments=(),
        body=None,
        expected_status_code=200,
        topics=(),
):
    with mock_advising_note_s3_bucket(app):
        data = {
            'body': body,
            'sids': ','.join(sids),
            'subject': subject,
            'topics': ','.join(topics),
        }
        for index, path in enumerate(attachments):
            data[f'attachment[{index}]'] = open(path, 'rb')
        response = client.post(
            '/api/note_draft/create',
            buffered=True,
            content_type='multipart/form-data',
            data=data,
        )
        assert response.status_code == expected_status_code
        return response.json
