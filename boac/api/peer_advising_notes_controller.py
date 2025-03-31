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

import urllib.parse

from boac.api.decorators import advising_data_access_required, peer_advisor_or_peer_advisor_manager, \
    peer_advisor_required
from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import get_boac_note_as_compatible_json, get_note_attachments_from_http_post, \
    get_note_author_profile_of_current_user, get_note_topics_from_http_post, validate_note_contact_type
from boac.externals import data_loch
from boac.externals.data_loch import get_basic_student_data
from boac.lib.berkeley import is_peer_advisor, sis_term_id_for_name, term_name_for_sis_id
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, process_input_from_rich_text_editor, to_bool_or_none
from boac.merged.advising_note import get_author_uid, get_boa_attachment_stream
from boac.merged.sis_terms import future_term_id
from boac.merged.student import merge_enrollment_terms
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.note_attachment import NoteAttachment
from boac.models.note_read import NoteRead
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.peer_advising_topic import PeerAdvisingTopic
from boac.routes import login_manager
from flask import current_app as app, request, Response
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
    note_template_id = params.get('noteTemplateId', None)
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
        note_template_id=note_template_id,
    )
    NoteRead.find_or_create(note_id=note.id, viewer_id=current_user.get_id())
    return tolerant_jsonify(get_boac_note_as_compatible_json(note, note_read=True))


@app.route('/api/peer_advising/<sid>/enrollments')
@peer_advisor_required
def get_enrollment_terms_by_sid(sid):
    api_json = {}
    for term_id, enrollments in _get_enrollments_by_term_id(sid).items():
        season, year = term_name_for_sis_id(term_id).split()
        year = int(year)
        fall_year, spring_year = (year, year + 1) if season == 'Fall' else (year - 1, year)
        # Organize by academic calendar
        academic_calendar = f'Fall {fall_year} - Summer {spring_year}'
        if academic_calendar not in api_json:
            term_names = (f'Fall {fall_year}', f'Spring {spring_year}', f'Summer {spring_year}')
            api_json[academic_calendar] = dict((sis_term_id_for_name(term_name), []) for term_name in term_names)
        api_json[academic_calendar][term_id] = sorted(enrollments, key=lambda e: e['displayName'])
    return tolerant_jsonify(dict(sorted(api_json.items(), reverse=True)))


@app.route('/api/peer_advisor/note/<note_id>/attachments', methods=['POST'])
@peer_advisor_required
def add_peer_advising_attachments(note_id):
    note = Note.find_by_id(note_id=note_id)
    is_authorized = is_peer_advisor(current_user) and get_author_uid(note) == current_user.uid
    if not is_authorized:
        raise ForbiddenRequestError('Sorry, you are not the author of this note.')
    attachments = get_note_attachments_from_http_post()
    attachment_limit = app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']
    if len(attachments) + len(note.attachments) > attachment_limit:
        raise BadRequestError(f'No more than {attachment_limit} attachments may be uploaded at once.')
    for attachment in attachments:
        note = Note.add_attachment(
            note_id=note_id,
            attachment=attachment,
        )
    return tolerant_jsonify(
        get_boac_note_as_compatible_json(
            note=note,
            note_read=NoteRead.find_or_create(current_user.get_id(), note_id),
        ),
    )


@app.route('/api/peer_advisor/note/attachment/<attachment_id>', methods=['GET'])
@peer_advisor_required
def download_peer_advising_note_attachment(attachment_id):
    attachment_id = int(attachment_id)
    attachment = NoteAttachment.find_by_id(attachment_id)
    if not attachment or not attachment.note:
        raise ResourceNotFoundError('Note not found')
    # Auth check
    note = attachment.note
    if get_author_uid(note) != current_user.uid:
        return login_manager.unauthorized()
    stream_data = get_boa_attachment_stream(attachment)
    if not stream_data or not stream_data['stream']:
        return Response('Sorry, attachment not available.', mimetype='text/html', status=404)
    r = Response(stream_data['stream'])
    r.headers['Content-Type'] = 'application/octet-stream'
    encoding_safe_filename = urllib.parse.quote(stream_data['filename'].encode('utf8'))
    r.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoding_safe_filename}"
    return r


@app.route('/api/peer_advising/notes/authored_by', methods=['POST'])
@advising_data_access_required
def get_notes_authored_by():
    params = request.get_json()
    peer_advising_department_id = params.get('peerAdvisingDepartmentId')
    uid = params.get('uid')
    # The 'timeframe' param (optional) has two properties: year and month.
    timeframe = params.get('timeframe') or None
    if timeframe:
        month = timeframe['month']
        year = timeframe['year']
        timeframe = f"{year}-{f'0{month}' if month < 10 else month}"
    notes = Note.get_peer_advising_notes_authored_by(
        author_uid=uid,
        timeframe_month=timeframe,
        peer_advising_department_id=peer_advising_department_id,
    )
    sids = [note['sid'] for note in notes]
    students_by_sid = {student['sid']: student for student in data_loch.get_basic_student_data(sids)}
    for note in notes:
        student = students_by_sid.get(note['sid'])
        note['student'] = {
            'firstName': student['first_name'],
            'lastName': student['last_name'],
            'sid': student['sid'],
            'uid': student['uid'],
        }
    return tolerant_jsonify(notes)


@app.route('/api/peer_advising/note/<note_id>')
@peer_advisor_required
def get_peer_advising_note(note_id):
    note = Note.find_by_id(note_id=note_id)
    memberships = (
        PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=current_user.get_id())
    )
    user_peer_advising_department_id = memberships[0]['peer_advising_department_id']
    if not note or note.peer_advising_department_id != user_peer_advising_department_id:
        raise ResourceNotFoundError('Note not found')
    note_read = NoteRead.when_user_read_note(current_user.get_id(), str(note.id))
    return tolerant_jsonify(get_boac_note_as_compatible_json(note=note, note_read=note_read))


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
    note_template_id = params.get('noteTemplateId', None)
    # Fetch existing note
    note = Note.find_by_id(note_id=note_id) if note_id else None
    is_authorized = note and PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
        user_id=current_user.get_id(),
        peer_advising_department_id=note.peer_advising_department_id,
    )
    if not is_authorized:
        raise ResourceNotFoundError('Note not found')
    note = Note.update(
        body=process_input_from_rich_text_editor(body),
        contact_type=contact_type,
        is_draft=False,
        note_id=note.id,
        sid=note.sid,
        subject=subject,
        topics=topics,
        note_template_id=note_template_id,
    )
    note_read = NoteRead.find_or_create(current_user.get_id(), note_id)
    api_json = get_boac_note_as_compatible_json(note=note, note_read=note_read)
    return tolerant_jsonify(api_json)


def _get_enrollments_by_term_id(sid):
    def extract(bloated_dict, keys_to_extract):
        return {key: bloated_dict[key] for key in keys_to_extract if key in bloated_dict}
    enrollments_by_term_id = {}
    enrollments_for_sid = data_loch.get_enrollments_for_sid(sid, latest_term_id=future_term_id())
    for term in merge_enrollment_terms(enrollments_for_sid):
        term_id = term['termId']
        enrollments_by_term_id[term_id] = []
        for row in term['enrollments']:
            keys = ('displayName', 'title', 'units')
            enrollment = extract(row, keys)
            enrollment['sections'] = []
            for section in row['sections']:
                extracted = extract(section, ['component', 'enrollmentStatus', 'primary', 'sectionNumber'])
                extracted['sectionId'] = section['ccn']
                grade = section.get('grade') or ''
                extracted['isUncompletedPerGrade'] = grade.upper() in ['F', 'I', 'INCOMPLETE', 'M', 'NP', 'NR', 'RD']
                enrollment['sections'].append(extracted)
            enrollments_by_term_id[term_id].append(enrollment)
    return enrollments_by_term_id
