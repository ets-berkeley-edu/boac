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

from boac.api.decorators import advisor_or_peer_advisor_required
from boac.api.errors import BadRequestError, ResourceNotFoundError
from boac.api.util import get_user_tag_object_sid, get_user_tag_objects
from boac.externals.data_loch import get_students_by_sids
from boac.lib.http import tolerant_jsonify
from boac.lib.util import is_int, join_if_present
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from boac.models.note import Note
from boac.models.user_tag import UserTag


@app.route('/api/user_tag/archived')
@advisor_or_peer_advisor_required
def archived_user_tags():
    user_tags = UserTag.get_all_for_user(current_user.get_id(), archived=True)
    return tolerant_jsonify({'archived': _build_notifications_feed(user_tags)})


@app.route('/api/user_tag/list')
@advisor_or_peer_advisor_required
def list_user_tags():
    user_tags = UserTag.get_all_for_user(current_user.get_id())
    return tolerant_jsonify({'notifications': _build_notifications_feed(user_tags)})


# The fields PATCH /api/user_tag/<id> accepts. Every one of them changes the unread count.
UPDATABLE_FLAGS = {'archivedByUser', 'readByUser'}


@app.route('/api/user_tag/<user_tag_id>', methods=['PATCH'])
@advisor_or_peer_advisor_required
def update_user_tag(user_tag_id):
    if not is_int(user_tag_id):
        raise BadRequestError('Invalid user tag id')

    params = request.get_json(silent=True)
    if not isinstance(params, dict) or not params or set(params) - UPDATABLE_FLAGS:
        raise BadRequestError('Request body must contain archivedByUser, readByUser, or both, and nothing else')
    for key, value in params.items():
        if not isinstance(value, bool):
            raise BadRequestError(f'{key} must be true or false')

    user_id = current_user.get_id()
    user_tag = UserTag.update_flags(
        int(user_tag_id),
        user_id,
        read_by_user=params.get('readByUser'),
        archived_by_user=params.get('archivedByUser'),
    )
    if not user_tag:
        raise ResourceNotFoundError('User tag not found')

    api_json = user_tag.to_api_json()
    api_json['myUnreadMessageCount'] = UserTag.get_unread_count(user_id)
    return tolerant_jsonify(api_json)


def _build_notifications_feed(user_tags):
    comment_ids = []
    note_ids = []
    for tag in user_tags:
        if tag.object_type == 'comment':
            comment_ids.append(tag.object_id)
        elif tag.object_type == 'note':
            note_ids.append(tag.object_id)
    comments = {comment.id: comment for comment in Comment.fetch_by_ids(comment_ids)}
    parent_ids = {comment.comment_parent_id for comment in comments.values()}
    comment_parents = CommentParent.find_by_ids(parent_ids) if parent_ids else []

    notes = {note.id: note for note in Note.find_by_ids(note_ids)}
    # Each tag's object is the note, appointment or eForm the tag sits in, with all of that record's comments.
    # For a tag in a comment, objectId and objectType still name the tagged comment.
    objects = get_user_tag_objects(list(notes.values()), list(comments.values()), comment_parents)
    student_sids = {sid for sid in (get_user_tag_object_sid(o) for o in objects.values()) if sid}
    students_by_sid = {student.get('sid'): student for student in get_students_by_sids(list(student_sids))} if len(student_sids) else []

    feed = []
    for tag in user_tags:
        tag_object = objects.get((tag.object_type, tag.object_id))
        feed_item = {
            **tag.to_api_json(),
            'object': tag_object,
        }
        student_sid = get_user_tag_object_sid(tag_object)
        if (student_sid and students_by_sid.get(student_sid)):
            student = students_by_sid.get(student_sid)
            feed_item['object']['student'] = {
                'name': join_if_present(' ', [student.get('first_name'), student.get('last_name')]),
                'uid': student.get('uid'),
                'sid': student_sid,
            }
        feed.append(feed_item)
    return feed
