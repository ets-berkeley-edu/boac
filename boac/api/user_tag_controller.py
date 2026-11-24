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
from flask_login import current_user

from boac.api.decorators import advisor_required
from boac.externals.data_loch import get_students_by_sids
from boac.lib.http import tolerant_jsonify
from boac.lib.util import join_if_present
from boac.models.comment import Comment
from boac.models.comment_parent import CommentParent
from boac.models.note import Note
from boac.models.user_tag import UserTag


@app.route('/api/user_tag/list')
@advisor_required
def list_user_tags():
    user_tags = UserTag.get_all_for_user(current_user.get_id())
    comment_ids = []
    note_ids = []
    for tag in user_tags:
        if tag.object_type == 'comment':
            comment_ids.append(tag.object_id)
        elif tag.object_type == 'note':
            note_ids.append(tag.object_id)
    comments = {comment.id: comment for comment in Comment.fetch_by_ids(comment_ids)}
    parent_ids = {comment.comment_parent_id for comment in comments.values()}
    parent_types = {parent.id: parent.parent_type for parent in CommentParent.find_by_ids(parent_ids)} if parent_ids else {}
    notes = {}
    student_sids = []
    for note in Note.find_by_ids(note_ids):
        notes[note.id] = note
        student_sids.append(note.sid)
    if len(student_sids):
        students_by_sid = {student.get('sid'): student for student in get_students_by_sids(student_sids)}
    else:
        students_by_sid = {}
    feed = []
    for tag in user_tags:
        message = comments.get(tag.object_id) if tag.object_type == 'comment' else notes.get(tag.object_id)
        feed_item = {
            **tag.to_api_json(),
            'object': message.to_api_json() if message else None,
        }
        if tag.object_type == 'comment' and message:
            feed_item['object']['parentType'] = parent_types.get(message.comment_parent_id)
        student_sid = feed_item['object'].get('sid') if feed_item['object'] else None
        if (student_sid and students_by_sid.get(student_sid)):
            student = students_by_sid.get(student_sid)
            feed_item['student'] = {
                'name': join_if_present(' ', [student.get('first_name'), student.get('last_name')]),
                'uid': student.get('uid'),
                'sid': student_sid,
            }
        feed.append(feed_item)
    return tolerant_jsonify({'notifications': feed})


@app.route('/api/user_tag/archived')
@advisor_required
def archived_user_tags():
    user_tags = UserTag.get_all_for_user(current_user.get_id(), archived=True)
    return tolerant_jsonify({'archived': [tag.to_api_json() for tag in user_tags]})
