"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
from boac.models.comment import Comment
from boac.models.comment_attachment import CommentAttachment
from boac.models.comment_parent import CommentParent
from boac.models.comment_read import CommentRead
from boac.models.note_read import NoteRead
from tests.util import mock_advising_note_s3_bucket

coe_advisor_uid = '1133399'
coe_advisor_no_advising_data_uid = '1022796'
l_s_major_advisor_uid = '242881'
admin_uid = '2040'

APPOINTMENT_PARENT_ID = '11667051-00010'
EFORM_PARENT_ID = 'eform-10096'


@pytest.fixture
def mock_appointment_comment(db):
    comment_parent = CommentParent.find_or_create(parent_type='appointment', parent_id=APPOINTMENT_PARENT_ID)
    return Comment.create(
        author_uid=coe_advisor_uid,
        author_name='COE Advisor',
        author_role='advisor',
        author_dept_codes=['COENG'],
        comment_parent_id=comment_parent.id,
        body='A test comment body.',
    )


@pytest.fixture
def mock_eform_comment(db):
    comment_parent = CommentParent.find_or_create(parent_type='course_load_eform', parent_id=EFORM_PARENT_ID)
    return Comment.create(
        author_uid=coe_advisor_uid,
        author_name='COE Advisor',
        author_role='advisor',
        author_dept_codes=['COENG'],
        comment_parent_id=comment_parent.id,
        body='A test comment body.',
    )


class TestCreateComment:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body='Hello world',
            expected_status_code=401,
        )

    def test_user_without_advising_data_access(self, client, fake_auth):
        """Denies access to a user who cannot access advising data."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body='Hello world',
            expected_status_code=401,
        )

    def test_missing_parent_type(self, client, fake_auth):
        """Returns 400 if parentType is missing."""
        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type=None,
            parent_id=APPOINTMENT_PARENT_ID,
            body='Hello world',
            expected_status_code=400,
        )

    def test_missing_parent_id(self, client, fake_auth):
        """Returns 400 if parentId is missing."""
        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=None,
            body='Hello world',
            expected_status_code=400,
        )

    def test_missing_body(self, client, fake_auth):
        """Returns 400 if body is missing."""
        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body=None,
            expected_status_code=400,
        )

    def test_empty_body(self, client, fake_auth):
        """Returns 400 if body is whitespace only."""
        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body='   ',
            expected_status_code=400,
        )

    def test_invalid_parent_type(self, client, fake_auth):
        """Returns 400 if parentType is not a valid enum value."""
        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type='not_a_valid_type',
            parent_id=APPOINTMENT_PARENT_ID,
            body='Hello world',
            expected_status_code=400,
        )

    def test_create_comment_on_appointment(self, client, fake_auth):
        """Advisor can create a comment on an appointment."""
        fake_auth.login(coe_advisor_uid)
        body = 'This is a comment on an appointment.'
        api_json = _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body=body,
        )
        assert api_json['id']
        assert api_json['body'].strip().replace(' ', '') == body.strip().replace(' ', '')
        assert api_json['parentType'] == 'appointment'
        assert api_json['parentId'] == APPOINTMENT_PARENT_ID
        assert api_json['author']['uid'] == coe_advisor_uid
        assert api_json['read'] is True
        assert api_json['updatedAt'] is None
        assert api_json['createdAt'] is not None

    def test_create_comment_on_eform(self, client, fake_auth):
        """Advisor can create a comment on an eForm."""
        fake_auth.login(coe_advisor_uid)
        body = 'This is a comment on a course load eform.'
        api_json = _api_create_comment(
            client=client,
            parent_type='course_load_eform',
            parent_id=EFORM_PARENT_ID,
            body=body,
        )
        assert api_json['id']
        assert api_json['parentType'] == 'course_load_eform'
        assert api_json['parentId'] == EFORM_PARENT_ID

    def test_all_eform_parent_types_accepted(self, client, fake_auth):
        """All valid eform parent types are accepted."""
        fake_auth.login(coe_advisor_uid)
        for parent_type in ('course_load_eform', 'cpp_change_eform', 'late_drop_eform'):
            api_json = _api_create_comment(
                client=client,
                parent_type=parent_type,
                parent_id=f'fake-{parent_type}-99',
                body=f'Comment on a {parent_type}.',
            )
            assert api_json['parentType'] == parent_type

    def test_create_comment_marked_read_for_author(self, client, fake_auth):
        """Comment is marked read for its author on creation."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body='A comment that should be auto-read.',
        )
        author_id = AuthorizedUser.get_id_per_uid(coe_advisor_uid)
        comments_read = CommentRead.get_comments_read_by_user(
            viewer_id=author_id,
            comment_ids=[api_json['id']],
        )
        assert len(comments_read) == 1

    def test_create_comment_appointment_marked_unread(self, client, fake_auth):
        """Appointment is marked unread by everyone except the comment author."""
        # First mark the appointment read for other users
        l_s_major_advisor_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        AppointmentRead.find_or_create(viewer_id=l_s_major_advisor_id, appointment_id=APPOINTMENT_PARENT_ID)
        admin_id = AuthorizedUser.get_id_per_uid(admin_uid)
        AppointmentRead.find_or_create(viewer_id=admin_id, appointment_id=APPOINTMENT_PARENT_ID)
        for user_id in [l_s_major_advisor_id, admin_id] :
            appointments_read = AppointmentRead.get_appointments_read_by_user(
                viewer_id=user_id,
                appointment_ids=[APPOINTMENT_PARENT_ID],
            )
            assert len(appointments_read) == 1

        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body='Adding a new comment makes the appointment unread.',
        )
        for user_id in [l_s_major_advisor_id, admin_id] :
            appointments_read = AppointmentRead.get_appointments_read_by_user(
                viewer_id=user_id,
                appointment_ids=[APPOINTMENT_PARENT_ID],
            )
            assert len(appointments_read) == 0

    def test_create_comment_eform_marked_unread(self, client, fake_auth):
        """Eform is marked unread by everyone except the comment author."""
        # First mark the eForm read for other users
        l_s_major_advisor_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        NoteRead.find_or_create(viewer_id=l_s_major_advisor_id, note_ids=[EFORM_PARENT_ID])
        admin_id = AuthorizedUser.get_id_per_uid(admin_uid)
        NoteRead.find_or_create(viewer_id=admin_id, note_ids=[EFORM_PARENT_ID])
        for user_id in [l_s_major_advisor_id, admin_id] :
            eforms_read = NoteRead.get_notes_read_by_user(
                viewer_id=user_id,
                note_ids=[EFORM_PARENT_ID],
            )
            assert len(eforms_read) == 1

        fake_auth.login(coe_advisor_uid)
        _api_create_comment(
            client=client,
            parent_type='course_load_eform',
            parent_id=EFORM_PARENT_ID,
            body='Adding a new comment makes the eForm unread.',
        )
        for user_id in [l_s_major_advisor_id, admin_id] :
            eforms_read = NoteRead.get_notes_read_by_user(
                viewer_id=user_id,
                note_ids=[EFORM_PARENT_ID],
            )
            assert len(eforms_read) == 0

    def test_create_comment_with_raw_url_in_body(self, client, fake_auth):
        """URL in comment body is wrapped in an anchor tag."""
        fake_auth.login(coe_advisor_uid)
        api_json = _api_create_comment(
            client=client,
            parent_type='appointment',
            parent_id=APPOINTMENT_PARENT_ID,
            body='Visit registrar.berkeley.edu for more info',
        )
        assert 'href' in api_json['body']

    def test_create_comment_with_attachment(self, app, client, fake_auth):
        """Advisor can create a comment with an attachment."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        with mock_advising_note_s3_bucket(app):
            data = {
                'parentType': 'appointment',
                'parentId': APPOINTMENT_PARENT_ID,
                'body': 'A comment with an attachment.',
                'attachment[0]': open(f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt', 'rb'),
            }
            response = client.post(
                '/api/comments/create',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
        assert response.status_code == 200
        assert len(response.json['attachments']) == 1
        assert response.json['attachments'][0]['filename'] == 'mock_advising_note_attachment_1.txt'


class TestUpdateComment:

    def test_not_authenticated(self, client, mock_appointment_comment):
        """Returns 401 if not authenticated."""
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='Updated body',
            expected_status_code=401,
        )

    def test_user_without_advising_data_access(self, client, fake_auth, mock_appointment_comment):
        """Denies access to a user who cannot access advising data."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='Updated body',
            expected_status_code=401,
        )

    def test_missing_comment_id(self, client, fake_auth):
        """Returns 400 if comment ID is missing."""
        fake_auth.login(coe_advisor_uid)
        _api_update_comment(
            client=client,
            comment_id=None,
            body='Updated body',
            expected_status_code=400,
        )

    def test_invalid_comment_id(self, client, fake_auth):
        """Returns 400 if comment ID is not an integer."""
        fake_auth.login(coe_advisor_uid)
        _api_update_comment(
            client=client,
            comment_id='not-an-int',
            body='Updated body',
            expected_status_code=400,
        )

    def test_nonexistent_comment(self, client, fake_auth):
        """Returns 404 if the comment does not exist."""
        fake_auth.login(coe_advisor_uid)
        _api_update_comment(
            client=client,
            comment_id=9999999,
            body='Updated body',
            expected_status_code=404,
        )

    def test_cannot_update_another_users_comment(self, client, fake_auth, mock_appointment_comment):
        """Returns 404 when a user tries to edit another user's comment."""
        assert mock_appointment_comment.author_uid != l_s_major_advisor_uid
        original_body = mock_appointment_comment.body
        fake_auth.login(l_s_major_advisor_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='Unauthorized update attempt',
            expected_status_code=404,
        )
        assert Comment.find_by_id(mock_appointment_comment.id).body == original_body

    def test_missing_body(self, client, fake_auth, mock_appointment_comment):
        """Returns 400 if the updated body is missing."""
        fake_auth.login(mock_appointment_comment.author_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body=None,
            expected_status_code=400,
        )

    def test_empty_body(self, client, fake_auth, mock_appointment_comment):
        """Returns 400 if the updated body is whitespace only."""
        fake_auth.login(mock_appointment_comment.author_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='   ',
            expected_status_code=400,
        )

    def test_update_comment(self, client, fake_auth, mock_appointment_comment):
        """Author can update the body of their own comment."""
        fake_auth.login(mock_appointment_comment.author_uid)
        new_body = 'This is the updated comment body.'
        api_json = _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body=new_body,
        )
        assert api_json['id'] == mock_appointment_comment.id
        assert api_json['body'].strip().replace(' ', '') == new_body.strip().replace(' ', '')
        assert api_json['parentType'] == 'appointment'
        assert api_json['parentId'] == APPOINTMENT_PARENT_ID
        assert api_json['read'] is True

    def test_update_comment_with_raw_url_in_body(self, client, fake_auth, mock_appointment_comment):
        """URL in updated body is wrapped in an anchor tag."""
        fake_auth.login(mock_appointment_comment.author_uid)
        api_json = _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='See registrar.berkeley.edu for details',
        )
        assert 'href' in api_json['body']

    def test_update_comment_marked_read_for_author(self, client, fake_auth, mock_appointment_comment):
        """Updated comment is marked read for its author."""
        fake_auth.login(mock_appointment_comment.author_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='Updated body.',
        )
        author_id = AuthorizedUser.get_id_per_uid(mock_appointment_comment.author_uid)
        comments_read = CommentRead.get_comments_read_by_user(
            viewer_id=author_id,
            comment_ids=[mock_appointment_comment.id],
        )
        assert len(comments_read) == 1

    def test_update_invalidates_read_for_others(self, client, fake_auth, mock_appointment_comment):
        """Editing a comment removes the comment read marker for all other viewers."""
        other_user_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        CommentRead.find_or_create(viewer_id=other_user_id, comment_ids=[mock_appointment_comment.id])
        assert len(CommentRead.get_comments_read_by_user(viewer_id=other_user_id, comment_ids=[mock_appointment_comment.id])) == 1

        fake_auth.login(mock_appointment_comment.author_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='An edit that others have not yet read.',
        )

        assert len(CommentRead.get_comments_read_by_user(viewer_id=other_user_id, comment_ids=[mock_appointment_comment.id])) == 0

    def test_edit_comment_appointment_marked_unread(self, client, fake_auth, mock_appointment_comment):
        """Appointment is marked unread by everyone except the comment author."""
        # First mark the appointment read for other users
        l_s_major_advisor_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        AppointmentRead.find_or_create(viewer_id=l_s_major_advisor_id, appointment_id=APPOINTMENT_PARENT_ID)
        admin_id = AuthorizedUser.get_id_per_uid(admin_uid)
        AppointmentRead.find_or_create(viewer_id=admin_id, appointment_id=APPOINTMENT_PARENT_ID)
        for user_id in [l_s_major_advisor_id, admin_id] :
            appointments_read = AppointmentRead.get_appointments_read_by_user(
                viewer_id=user_id,
                appointment_ids=[APPOINTMENT_PARENT_ID],
            )
            assert len(appointments_read) == 1

        fake_auth.login(coe_advisor_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_appointment_comment.id,
            body='Editing a comment makes the appointment unread.',
        )
        for user_id in [l_s_major_advisor_id, admin_id] :
            appointments_read = AppointmentRead.get_appointments_read_by_user(
                viewer_id=user_id,
                appointment_ids=[APPOINTMENT_PARENT_ID],
            )
            assert len(appointments_read) == 0

    def test_create_comment_eform_marked_unread(self, client, fake_auth, mock_eform_comment):
        """Eform is marked unread by everyone except the comment author."""
        # First mark the eForm read for other users
        l_s_major_advisor_id = AuthorizedUser.get_id_per_uid(l_s_major_advisor_uid)
        NoteRead.find_or_create(viewer_id=l_s_major_advisor_id, note_ids=[EFORM_PARENT_ID])
        admin_id = AuthorizedUser.get_id_per_uid(admin_uid)
        NoteRead.find_or_create(viewer_id=admin_id, note_ids=[EFORM_PARENT_ID])
        for user_id in [l_s_major_advisor_id, admin_id] :
            eforms_read = NoteRead.get_notes_read_by_user(
                viewer_id=user_id,
                note_ids=[EFORM_PARENT_ID],
            )
            assert len(eforms_read) == 1

        fake_auth.login(coe_advisor_uid)
        _api_update_comment(
            client=client,
            comment_id=mock_eform_comment.id,
            body='Editing a comment makes the eForm unread.',
        )
        for user_id in [l_s_major_advisor_id, admin_id] :
            eforms_read = NoteRead.get_notes_read_by_user(
                viewer_id=user_id,
                note_ids=[EFORM_PARENT_ID],
            )
            assert len(eforms_read) == 0

    def test_update_comment_add_attachment(self, app, client, fake_auth, mock_appointment_comment):
        """Author can add an attachment when updating a comment."""
        fake_auth.login(mock_appointment_comment.author_uid)
        base_dir = app.config['BASE_DIR']
        with mock_advising_note_s3_bucket(app):
            data = {
                'id': mock_appointment_comment.id,
                'body': 'Updated with an attachment.',
                'attachment[0]': open(f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt', 'rb'),
            }
            response = client.post(
                '/api/comments/update',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
        assert response.status_code == 200
        assert len(response.json['attachments']) == 1

    def test_update_comment_delete_attachment(self, app, client, fake_auth):
        """Author can delete an attachment when updating a comment."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        with mock_advising_note_s3_bucket(app):
            create_data = {
                'parentType': 'appointment',
                'parentId': APPOINTMENT_PARENT_ID,
                'body': 'Comment with attachments.',
                'attachment[0]': open(f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt', 'rb'),
                'attachment[1]': open(f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt', 'rb'),
            }
            create_response = client.post(
                '/api/comments/create',
                buffered=True,
                content_type='multipart/form-data',
                data=create_data,
            )
            assert create_response.status_code == 200
            comment_id = create_response.json['id']
            attachment_id_to_delete = create_response.json['attachments'][0]['id']
            attachment_id_to_keep = create_response.json['attachments'][1]['id']

            update_data = {
                'id': comment_id,
                'body': 'Now with one fewer attachment.',
                'deleteAttachmentIds': str(attachment_id_to_delete),
            }
            update_response = client.post(
                '/api/comments/update',
                buffered=True,
                content_type='multipart/form-data',
                data=update_data,
            )
        assert update_response.status_code == 200
        remaining = update_response.json['attachments']
        assert len(remaining) == 1
        assert remaining[0]['id'] == attachment_id_to_keep


class TestDeleteComment:

    def test_not_authenticated(self, client, mock_appointment_comment):
        """Returns 401 if not authenticated."""
        response = client.delete(f'/api/comments/delete/{mock_appointment_comment.id}')
        assert response.status_code == 401

    def test_non_admin_cannot_delete(self, client, fake_auth, mock_appointment_comment):
        """Non-admin user cannot delete a comment."""
        fake_auth.login(coe_advisor_uid)
        response = client.delete(f'/api/comments/delete/{mock_appointment_comment.id}')
        assert response.status_code == 401
        assert Comment.find_by_id(mock_appointment_comment.id) is not None

    def test_invalid_comment_id(self, client, fake_auth):
        """Returns 400 for a non-integer comment ID."""
        fake_auth.login(admin_uid)
        response = client.delete('/api/comments/delete/not-an-int')
        assert response.status_code == 400

    def test_nonexistent_comment(self, client, fake_auth):
        """Returns 404 if the comment does not exist."""
        fake_auth.login(admin_uid)
        response = client.delete('/api/comments/delete/9999999')
        assert response.status_code == 404

    def test_admin_delete_comment(self, client, fake_auth, mock_appointment_comment):
        """Admin can soft-delete a comment."""
        fake_auth.login(admin_uid)
        comment_id = mock_appointment_comment.id
        response = client.delete(f'/api/comments/delete/{comment_id}')
        assert response.status_code == 200
        assert Comment.find_by_id(comment_id) is None

    def test_admin_delete_comment_with_attachments(self, app, client, fake_auth):
        """Admin can delete a comment along with its attachments."""
        fake_auth.login(coe_advisor_uid)
        base_dir = app.config['BASE_DIR']
        with mock_advising_note_s3_bucket(app):
            data = {
                'parentType': 'appointment',
                'parentId': APPOINTMENT_PARENT_ID,
                'body': 'A comment with two attachments.',
                'attachment[0]': open(f'{base_dir}/fixtures/mock_advising_note_attachment_1.txt', 'rb'),
                'attachment[1]': open(f'{base_dir}/fixtures/mock_advising_note_attachment_2.txt', 'rb'),
            }
            response = client.post(
                '/api/comments/create',
                buffered=True,
                content_type='multipart/form-data',
                data=data,
            )
        assert response.status_code == 200
        comment_id = response.json['id']
        attachment_ids = [a['id'] for a in response.json['attachments']]
        assert len(attachment_ids) == 2

        fake_auth.login(admin_uid)
        delete_response = client.delete(f'/api/comments/delete/{comment_id}')
        assert delete_response.status_code == 200
        assert Comment.find_by_id(comment_id) is None
        assert CommentAttachment.find_by_id(attachment_ids[0]) is None
        assert CommentAttachment.find_by_id(attachment_ids[1]) is None


def _api_create_comment(client, parent_type, parent_id, body, expected_status_code=200):
    data = {}
    if parent_type is not None:
        data['parentType'] = parent_type
    if parent_id is not None:
        data['parentId'] = parent_id
    if body is not None:
        data['body'] = body
    response = client.post(
        '/api/comments/create',
        buffered=True,
        content_type='multipart/form-data',
        data=data,
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_update_comment(client, comment_id, body, expected_status_code=200):
    data = {}
    if comment_id is not None:
        data['id'] = comment_id
    if body is not None:
        data['body'] = body
    response = client.post(
        '/api/comments/update',
        buffered=True,
        content_type='multipart/form-data',
        data=data,
    )
    assert response.status_code == expected_status_code
    return response.json
