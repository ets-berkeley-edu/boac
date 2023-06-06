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

import urllib.parse

from boac import std_commit
from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import (
    advising_data_access_required,
    director_advising_data_access_required,
    get_note_attachments_from_http_post,
    get_note_topics_from_http_post,
    get_template_attachment_ids_from_http_post,
    validate_advising_note_set_date,
)
from boac.externals import data_loch
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.sis_advising import get_legacy_attachment_stream as get_sis_attachment_stream
from boac.lib.util import (
    get as get_param,
    is_int,
    localize_datetime,
    process_input_from_rich_text_editor,
    to_bool_or_none,
    utc_now,
)
from boac.merged.advising_note import (
    can_current_user_access_note,
    can_current_user_edit_note,
    get_advising_notes,
    get_author_uid,
    get_boa_attachment_stream,
    get_eop_attachment_stream,
    get_zip_stream,
    note_to_compatible_json,
)
from boac.merged.calnet import get_calnet_user_for_uid
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.note import Note, note_contact_type_enum
from boac.models.note_attachment import NoteAttachment
from boac.models.note_read import NoteRead
from boac.models.note_template import NoteTemplate
from flask import current_app as app, request, Response, stream_with_context
from flask_login import current_user

DEFAULT_DRAFT_NOTE_SUBJECT = '[DRAFT NOTE]'


@app.route('/api/note/<note_id>')
@advising_data_access_required
def get_note(note_id):
    note = Note.find_by_id(note_id=note_id)
    if not note or not can_current_user_access_note(note):
        raise ResourceNotFoundError('Note not found')
    note_read = NoteRead.when_user_read_note(current_user.get_id(), str(note.id))
    return tolerant_jsonify(_boa_note_to_compatible_json(note=note, note_read=note_read))


@app.route('/api/notes/<note_id>/mark_read', methods=['POST'])
@advising_data_access_required
def mark_note_read(note_id):
    if NoteRead.find_or_create(current_user.get_id(), note_id):
        return tolerant_jsonify({'status': 'created'}, status=201)
    else:
        raise BadRequestError(f'Failed to mark note {note_id} as read by user {current_user.uid}')


@app.route('/api/note/create_draft', methods=['POST'])
@advising_data_access_required
def create_draft_note():
    dept_codes = dept_codes_where_advising(current_user)
    if current_user.is_admin or not len(dept_codes):
        raise ForbiddenRequestError('Sorry, only advisors can create advising notes')
    params = request.get_json()
    sid = get_param(params, 'sid')
    note = Note.create(
        **_get_author_profile(),
        body=None,
        is_draft=True,
        sid=sid,
        subject=DEFAULT_DRAFT_NOTE_SUBJECT,
    )
    return tolerant_jsonify(_boa_note_to_compatible_json(note, note_read=True))


@app.route('/api/notes/update', methods=['POST'])
@advising_data_access_required
def update_note():
    params = request.form
    body = params.get('body', None)
    contact_type = _validate_contact_type(params)
    is_draft = to_bool_or_none(params.get('isDraft', False))
    is_private = to_bool_or_none(params.get('isPrivate', False))
    note_id = params.get('id', None)
    set_date = validate_advising_note_set_date(params)
    subject = (params.get('subject', None) or '').strip()
    topics = get_note_topics_from_http_post()
    # Fetch existing note
    note = Note.find_by_id(note_id=note_id) if note_id else None
    if not note or not can_current_user_edit_note(note):
        raise ResourceNotFoundError('Note not found')
    if (is_private is not note.is_private) and not current_user.can_access_private_notes:
        raise ForbiddenRequestError('Sorry, you are not authorized to manage note privacy')
    # A note is "published" when the 'is_draft' value goes from True to False.
    is_publishing_draft_note = note.is_draft and not is_draft
    if is_draft or is_publishing_draft_note:
        sids = _get_sids_for_note_creation()
    else:
        sids = [note.sid] if note.sid else []
    if is_draft:
        subject = subject or DEFAULT_DRAFT_NOTE_SUBJECT
        # Draft note can have zero or one SIDs. If multiple SIDs are present then ignore them.
        sids = None if len(sids) > 1 else sids
        if not note.is_draft:
            raise BadRequestError('A published note cannot revert to draft status.')
    else:
        if not subject or not len(sids):
            raise BadRequestError('Note update requires subject and one SID.')
    if is_publishing_draft_note and len(sids) > 1:
        # Create a batch of notes!
        api_json = Note.create_batch(
            **_get_author_profile(),
            attachments=note.attachments,
            author_id=current_user.to_api_json()['id'],
            body=body,
            contact_type=contact_type,
            is_private=is_private,
            set_date=set_date,
            sids=sids,
            subject=subject,
            template_attachment_ids=get_template_attachment_ids_from_http_post(),
            topics=topics,
        )
        # Delete the draft. It has served its purpose.
        Note.delete(note_id=note.id)
    else:
        note = Note.update(
            body=process_input_from_rich_text_editor(body),
            contact_type=contact_type,
            is_draft=is_draft,
            is_private=is_private,
            note_id=note.id,
            set_date=set_date,
            sid=sids[0] if sids else None,
            subject=subject,
            template_attachment_ids=get_template_attachment_ids_from_http_post(),
            topics=topics,
        )
        note_read = NoteRead.find_or_create(current_user.get_id(), note_id)
        api_json = _boa_note_to_compatible_json(note=note, note_read=note_read)
    return tolerant_jsonify(api_json)


@app.route('/api/note/apply_template', methods=['POST'])
@advising_data_access_required
def apply_template():
    params = request.get_json()
    note_id = params.get('noteId', None)
    template_id = params.get('templateId', None)
    note = Note.find_by_id(note_id=note_id) if note_id else None
    if not note or not can_current_user_edit_note(note):
        raise ResourceNotFoundError('Note not found')
    note_template = NoteTemplate.find_by_id(note_template_id=template_id)
    if not note_template or note_template.deleted_at or note_template.creator_id != current_user.get_id():
        raise ResourceNotFoundError('Note template not found')
    note = Note.update(
        body=note_template.body,
        contact_type=note.contact_type,
        is_draft=note.is_draft,
        is_private=note_template.is_private,
        note_id=note.id,
        set_date=note.set_date,
        sid=note.sid,
        subject=note_template.subject,
        topics=[topic.topic for topic in note_template.topics],
    )
    for attachment in note.attachments:
        Note.delete_attachment(attachment_id=attachment.id, note_id=note_id)
    for attachment in note_template.attachments:
        note.attachments.append(
            NoteAttachment(
                note_id=note_id,
                path_to_attachment=attachment.path_to_attachment,
                uploaded_by_uid=current_user.uid,
            ),
        )
        std_commit()
    return tolerant_jsonify(_boa_note_to_compatible_json(note=Note.find_by_id(note_id), note_read=True))


@app.route('/api/notes/delete/<note_id>', methods=['DELETE'])
@advising_data_access_required
def delete_note(note_id):
    note = Note.find_by_id(note_id=note_id)
    if not note:
        raise ResourceNotFoundError('Note not found')
    can_user_delete = current_user.is_admin or (note.is_draft and can_current_user_edit_note(note))
    if not can_user_delete:
        raise ForbiddenRequestError('Sorry, you are not authorized to delete notes.')
    Note.delete(note_id=note_id)
    return tolerant_jsonify({'message': f'Note {note_id} deleted'}), 200


@app.route('/api/notes/my_drafts')
@advising_data_access_required
def get_my_note_drafts():
    api_json = []
    draft_notes = Note.get_draft_notes(None if current_user.is_admin else current_user.uid)
    all_sids = set([draft_note.sid for draft_note in draft_notes])
    students_by_sid = {student['sid']: student for student in data_loch.get_basic_student_data(sids=list(all_sids))}
    for draft_note in draft_notes:
        if not draft_note.subject:
            draft_note = Note.update_subject(note_id=draft_note.id, subject=DEFAULT_DRAFT_NOTE_SUBJECT)
        draft_note_json = _boa_note_to_compatible_json(note=draft_note, note_read=False)
        student = students_by_sid[draft_note.sid] if draft_note.sid else None
        draft_note_json['student'] = {
            'sid': student['sid'],
            'uid': student['uid'],
            'firstName': student['first_name'],
            'lastName': student['last_name'],
        } if student else None
        api_json.append(draft_note_json)
    return tolerant_jsonify(api_json)


@app.route('/api/notes/my_draft_note_count')
@advising_data_access_required
def my_draft_note_count():
    return tolerant_jsonify(Note.get_draft_note_count(None if current_user.is_admin else current_user.uid))


@app.route('/api/notes/<note_id>/attachments', methods=['POST'])
@advising_data_access_required
def add_attachments(note_id):
    note = Note.find_by_id(note_id=note_id)
    if not can_current_user_edit_note(note):
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
        _boa_note_to_compatible_json(
            note=note,
            note_read=NoteRead.find_or_create(current_user.get_id(), note_id),
        ),
    )


@app.route('/api/notes/<note_id>/attachment/<attachment_id>', methods=['DELETE'])
@advising_data_access_required
def remove_attachment(note_id, attachment_id):
    existing_note = Note.find_by_id(note_id=note_id)
    if not existing_note:
        raise BadRequestError('Note id not found.')
    if not can_current_user_edit_note(existing_note):
        raise ForbiddenRequestError('You are not authorized to remove attachments from this note.')
    note = Note.delete_attachment(
        note_id=note_id,
        attachment_id=int(attachment_id),
    )
    return tolerant_jsonify(
        _boa_note_to_compatible_json(
            note=note,
            note_read=NoteRead.find_or_create(current_user.get_id(), note_id),
        ),
    )


@app.route('/api/notes/attachment/<attachment_id>', methods=['GET'])
@advising_data_access_required
def download_attachment(attachment_id):
    is_legacy = not is_int(attachment_id)
    id_ = attachment_id if is_legacy else int(attachment_id)
    if is_legacy:
        can_access_note = current_user.is_admin or current_user.can_access_advising_data
        stream_data = _get_legacy_attachment_stream(id_)
    else:
        attachment = NoteAttachment.find_by_id(id_)
        note = attachment and attachment.note
        if not note:
            raise ResourceNotFoundError('Note not found')
        can_access_note = (current_user.is_admin or current_user.can_access_advising_data) \
            and (not note.is_draft or get_author_uid(note) == current_user.uid) \
            and (not note.is_private or current_user.can_access_private_notes)
        stream_data = get_boa_attachment_stream(attachment)
    if not can_access_note or not stream_data or not stream_data['stream']:
        return Response('Sorry, attachment not available.', mimetype='text/html', status=404)
    r = Response(stream_data['stream'])
    r.headers['Content-Type'] = 'application/octet-stream'
    encoding_safe_filename = urllib.parse.quote(stream_data['filename'].encode('utf8'))
    r.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoding_safe_filename}"
    return r


@app.route('/api/notes/<sid>/download', methods=['GET'])
@director_advising_data_access_required
def download_notes(sid):
    download_type = get_param(request.args, 'type', 'note')
    students = data_loch.get_basic_student_data([sid])
    student = students[0] if students else None
    notes = get_advising_notes(exclude_draft_notes=True, sid=sid) if student else []

    if not student or not notes:
        return Response('Not found', status=404)

    filename = '_'.join([
        f'advising_{download_type}s',
        student.get('first_name', '').lower(),
        student.get('last_name', '').lower(),
        localize_datetime(utc_now()).strftime('%Y%m%d'),
    ])

    def generator():
        for chunk in get_zip_stream(
                download_type=download_type,
                filename=filename,
                notes=notes,
                student=student,
        ):
            yield chunk

    response = Response(stream_with_context(generator()), mimetype='application/zip')
    encoding_safe_filename = urllib.parse.quote(f'{filename}.zip'.encode('utf8'))
    response.headers['Content-Disposition'] = f'attachment; filename={encoding_safe_filename}'
    return response


def _get_sids_for_note_creation():
    def _get_param_as_set(key):
        values = set()
        for entry in request.form.getlist(key):
            # The use of 'form.getlist' might give us a list with one entry: comma-separated values
            split = str(entry).split(',')
            for value in list(filter(None, split)):
                values.add(value)
        return values

    cohort_ids = set(_get_param_as_set('cohortIds'))
    curated_group_ids = set(_get_param_as_set('curatedGroupIds'))
    sids = _get_param_as_set('sids')
    sids = sids.union(_get_sids_per_cohorts(cohort_ids))
    return list(sids.union(_get_sids_per_curated_groups(curated_group_ids)))


def _get_sids_per_cohorts(cohort_ids=None):
    sids = set()
    for cohort_id in cohort_ids or ():
        if cohort_id:
            sids = sids.union(CohortFilter.get_sids(cohort_id))
    return sids


def _get_sids_per_curated_groups(curated_group_ids=None):
    sids = set()
    for curated_group_id in curated_group_ids or ():
        if curated_group_id:
            sids = sids.union(CuratedGroup.get_all_sids(curated_group_id))
    return sids


def _get_author_profile():
    author = current_user.to_api_json()
    calnet_profile = get_calnet_user_for_uid(app, author['uid'])
    if calnet_profile and calnet_profile.get('departments'):
        dept_codes = [dept.get('code') for dept in calnet_profile.get('departments')]
    else:
        dept_codes = dept_codes_where_advising(current_user)
    if calnet_profile and calnet_profile.get('title'):
        role = calnet_profile['title']
    elif current_user.departments:
        role = current_user.departments[0]['role']
    else:
        role = None

    return {
        'author_uid': author['uid'],
        'author_name': author['name'],
        'author_role': role,
        'author_dept_codes': dept_codes,
    }


def _get_legacy_attachment_stream(attachment_id):
    if attachment_id.startswith('eop_advising_note'):
        return get_eop_attachment_stream(attachment_id)
    return get_sis_attachment_stream(attachment_id)


def _validate_contact_type(params):
    contact_type = params.get('contactType') or None
    if contact_type and contact_type not in note_contact_type_enum.enums:
        raise BadRequestError('Unrecognized contact type')
    return contact_type


def _boa_note_to_compatible_json(note, note_read):
    return {
        **note_to_compatible_json(
            note=note.__dict__,
            note_read=note_read,
            attachments=[a.to_api_json() for a in note.attachments if not a.deleted_at],
            topics=[t.topic for t in note.topics if not t.deleted_at],
        ),
        **{
            'message': note.body,
            'type': 'note',
        },
    }
