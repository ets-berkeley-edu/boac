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

from boac.api.decorators import advising_data_access_required
from boac.api.errors import BadRequestError
from boac.api.util import get_note_attachments_from_http_post, get_note_author_profile_of_current_user
from boac.lib.http import tolerant_jsonify
from boac.lib.util import process_input_from_rich_text_editor
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
    return tolerant_jsonify({
        **comment.to_api_json(),
        'parentType': comment_parent.parent_type,
        'parentId': comment_parent.parent_id,
    })
