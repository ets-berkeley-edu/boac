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

from boac.api.errors import BadRequestError
from boac.api.util import current_user_profile, feature_flag_create_notes, get_dept_codes, get_dept_role
from boac.lib.http import tolerant_jsonify
from boac.merged.student import note_to_compatible_json
from boac.models.note import Note
from boac.models.note_read import NoteRead
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/notes/<note_id>/mark_read', methods=['POST'])
@login_required
def mark_read(note_id):
    if NoteRead.create(current_user.id, note_id):
        return tolerant_jsonify({'status': 'created'}, status=201)
    else:
        raise BadRequestError(f'Failed to mark note {note_id} as read by user {current_user.uid}')


@app.route('/api/notes/create', methods=['POST'])
@login_required
@feature_flag_create_notes
def create_note():
    params = request.get_json()
    sid = params.get('sid', None)
    subject = params.get('subject', None)
    body = params.get('body', None)
    if not sid or not subject or not body:
        raise BadRequestError('Note creation requires \'subject\', \'body\', and \'sid\'')
    profile = current_user_profile()
    dept_codes = get_dept_codes(current_user)
    if len(dept_codes):
        # TODO: We capture one 'role' and yet user could have multiple, one per dept.
        role = get_dept_role(current_user.department_memberships[0])
    else:
        role = 'BOAC Admin User' if current_user.is_admin else None
    note = Note.create(
        author_uid=current_user.uid,
        author_name=_get_name(profile),
        author_role=role,
        author_dept_codes=dept_codes,
        subject=subject,
        body=body,
        sid=sid,
    )
    note_json = note_to_compatible_json(note.to_api_json())
    return tolerant_jsonify(note_json)


def _get_name(user):
    first_name = user.get('firstName')
    last_name = user.get('lastName')
    return '' if not (first_name or last_name) else (first_name if not last_name else f'{first_name} {last_name}')
