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

from flask import current_app as app
from flask import request
from flask_login import current_user

from boac.api.decorators import admin_required, advising_data_access_required
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import (
    get_note_attachments_from_http_post,
    get_note_author_profile_of_current_user,
    record_external_comment_read_state,
)
from boac.lib.http import tolerant_jsonify
from boac.lib.util import is_int, process_input_from_rich_text_editor
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent, comment_parent_type_enum


@app.route('/api/comments/create', methods=['POST'])
@advising_data_access_required
def create_comment():
    params = request.form
    parent_type = params.get('parentType')
    parent_id = params.get('parentId')
    body = process_input_from_rich_text_editor(params.get('body'))
    if (
            not parent_type
            or not parent_id
            or not body
            or not body.strip()
            or parent_type not in comment_parent_type_enum.enums
    ):
        raise BadRequestError('Request has missing or invalid request parameters')

    attachments = get_note_attachments_from_http_post(tolerate_none=True)
    attachment_limit = app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']
    if len(attachments) > attachment_limit:
        raise BadRequestError(f'No more than {attachment_limit} attachments may be uploaded at once.')

    comment_parent = CommentParent.find_or_create(parent_type=parent_type, parent_id=parent_id)
    comment = Comment.create(
        **get_note_author_profile_of_current_user(),
        comment_parent_id=comment_parent.id,
        body=body,
        attachments=attachments,
    )
    viewer_id = current_user.get_id()
    record_external_comment_read_state(comment, viewer_id, parent_type, parent_id)
    return tolerant_jsonify({
        **comment.to_api_json(read=True),
        'parentType': comment_parent.parent_type,
        'parentId': comment_parent.parent_id,
    })


def _comment_json_with_parent(comment, read=False):
    comment_parent = CommentParent.find_by_id(comment.comment_parent_id)
    if not comment_parent:
        raise ResourceNotFoundError('Comment not found')
    return {
        **comment.to_api_json(read=read),
        'parentType': comment_parent.parent_type,
        'parentId': comment_parent.parent_id,
    }


def _load_comment_for_mutation(comment_id):
    if not comment_id or not is_int(comment_id):
        raise BadRequestError('Request has missing or invalid request parameters')
    comment = Comment.find_by_id(int(comment_id))
    if not comment:
        raise ResourceNotFoundError('Comment not found')
    return comment


@app.route('/api/comments/update', methods=['POST'])
@advising_data_access_required
def update_comment():
    params = request.form
    comment = _load_comment_for_mutation(params.get('id'))
    if comment.author_uid != current_user.uid:
        raise ResourceNotFoundError('Comment not found')
    body = process_input_from_rich_text_editor(params.get('body'))
    if not body or not body.strip():
        raise BadRequestError('Request has missing or invalid request parameters')

    delete_ids_ = params.get('deleteAttachmentIds') or []
    delete_ids_ = delete_ids_ if isinstance(delete_ids_, list) else str(delete_ids_).split(',')
    delete_attachment_ids = [int(id_) for id_ in delete_ids_ if is_int(id_)]
    attachments = get_note_attachments_from_http_post(tolerate_none=True)
    attachment_limit = app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']
    existing_attachment_count = len(comment.attachments) - len(delete_attachment_ids)
    if existing_attachment_count + len(attachments) > attachment_limit:
        raise BadRequestError(f'No more than {attachment_limit} attachments may be uploaded at once.')

    comment.update(body=body, delete_attachment_ids=delete_attachment_ids, new_attachments=attachments)
    viewer_id = current_user.get_id()
    comment_parent = CommentParent.find_by_id(comment.comment_parent_id)
    if comment_parent:
        record_external_comment_read_state(
            comment,
            viewer_id,
            comment_parent.parent_type,
            comment_parent.parent_id,
            after_edit=True,
        )
    return tolerant_jsonify(_comment_json_with_parent(comment, read=True))


@app.route('/api/comments/delete/<comment_id>', methods=['DELETE'])
@admin_required
def delete_comment(comment_id):
    comment = _load_comment_for_mutation(comment_id)
    comment.soft_delete()
    return tolerant_jsonify({'message': f'Comment {comment_id} deleted'}), 200
