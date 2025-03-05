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

from boac.api.decorators import peer_advisor_or_peer_advisor_manager, peer_advisor_required
from boac.api.errors import ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import get_boac_note_as_compatible_json, get_note_author_profile_of_current_user, \
    get_note_topics_from_http_post, validate_note_contact_type
from boac.externals import data_loch
from boac.externals.data_loch import get_basic_student_data
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, process_input_from_rich_text_editor, to_bool_or_none
from boac.merged.sis_terms import current_term_id
from boac.merged.student import merge_enrollment_terms
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_read import NoteRead
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.peer_advising_topic import PeerAdvisingTopic
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/peer_advising/note_topics')
@peer_advisor_or_peer_advisor_manager
def get_peer_advising_topics():
    return tolerant_jsonify([topic.to_api_json() for topic in PeerAdvisingTopic.get_all()])


@app.route('/api/peer_advising/note/create', methods=['POST'])
@peer_advisor_required
def create_peer_advising_note():
    params = request.get_json()
    body = params.get('body', None)
    contact_type = validate_note_contact_type(params.get('contactType'))
    peer_advising_department_id = get_param(params, 'peerAdvisingDepartmentId')
    sid = get_param(params, 'sid')
    subject = (params.get('subject', None) or '').strip()
    topics = get_note_topics_from_http_post()
    memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(current_user.get_id())
    matching_membership = next((m for m in memberships if m['peer_advising_department_id'] == peer_advising_department_id), None)
    if not matching_membership:
        raise ForbiddenRequestError('Unauthorized')
    note = Note.create(
        **get_note_author_profile_of_current_user(),
        body=body,
        contact_type=contact_type,
        subject=subject,
        topics=topics,
        peer_advising_department_id=peer_advising_department_id,
        sid=sid,
    )
    NoteRead.find_or_create(note_id=note.id, viewer_id=current_user.get_id())
    return tolerant_jsonify(get_boac_note_as_compatible_json(note, note_read=True))


@app.route('/api/peer_advising/<sid>/enrollments')
@peer_advisor_required
def get_enrollment_terms_by_sid(sid):
    term_id = request.args.get('termId')
    latest_term_id = term_id or current_term_id()
    enrollment_results = data_loch.get_enrollments_for_sid(sid, latest_term_id=latest_term_id)

    def extract(bloated_dict, keys_to_extract):
        return {key: bloated_dict[key] for key in keys_to_extract if key in bloated_dict}

    api_json = []
    for term in merge_enrollment_terms(enrollment_results):
        enrollments = []
        for enrollment in term['enrollments']:
            keys = ('displayName', 'title', 'units')
            enrollments.append(extract(enrollment, keys))
        api_json.append({
            **extract(term, ('termId', 'termName')),
            'enrollments': enrollments,
        })
    return tolerant_jsonify(api_json)


@app.route('/api/peer_advisor/<uid>/notes')
@peer_advisor_required
def get_notes_for_peer_advisor(uid):
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 50))
    include_students = to_bool_or_none(request.args.get('includeStudents')) or False
    user_id = AuthorizedUser.get_id_per_uid(uid)
    if not current_user.is_admin and user_id != current_user.get_id():
        raise ForbiddenRequestError('Unauthorized')
    memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=user_id)
    peer_advising_department_id = memberships[0]['peer_advising_department_id']
    notes, total_note_count = Note.get_notes_by_peer_advising_department(
        limit=limit,
        offset=offset,
        peer_advising_department_id=peer_advising_department_id,
    )
    students_by_sid = {}
    if include_students:
        sids = [note.sid for note in notes]
        for student in get_basic_student_data(sids=sids):
            students_by_sid[student['sid']] = {
                'sid': student['sid'],
                'uid': student['uid'],
                'firstName': student['first_name'],
                'lastName': student['last_name'],
            }
    notes_read_by_user = NoteRead.get_notes_read_by_user(
        note_ids=[str(note.id) for note in notes],
        viewer_id=current_user.get_id(),
    )
    api_json = {
        'notes': [],
        'totalNoteCount': total_note_count,
    }
    for note in notes:
        note_json = get_boac_note_as_compatible_json(note=note, note_read=note.id in notes_read_by_user)
        api_json['notes'].append(note_json)
        if include_students:
            note_json['student'] = students_by_sid[note.sid]
    return tolerant_jsonify(api_json)


@app.route('/api/peer_advising/note/update', methods=['POST'])
@peer_advisor_required
def update_peer_advising_note():
    params = request.form
    body = params.get('body', None)
    contact_type = validate_note_contact_type(params.get('contactType'))
    note_id = params.get('id', None)
    subject = (params.get('subject', None) or '').strip()
    topics = get_note_topics_from_http_post()
    # Fetch existing note
    note = Note.find_by_id(note_id=note_id) if note_id else None
    if not note or not _can_current_user_edit_peer_advising_note(note):
        raise ResourceNotFoundError('Note not found')
    note = Note.update(
        body=process_input_from_rich_text_editor(body),
        contact_type=contact_type,
        is_draft=False,
        note_id=note.id,
        sid=note.sid,
        subject=subject,
        topics=topics,
    )
    note_read = NoteRead.find_or_create(current_user.get_id(), note_id)
    api_json = get_boac_note_as_compatible_json(note=note, note_read=note_read)
    return tolerant_jsonify(api_json)


def _can_current_user_edit_peer_advising_note(note):
    return True
