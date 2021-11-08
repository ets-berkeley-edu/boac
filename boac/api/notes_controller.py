"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import (
    advising_data_access_required,
    director_advising_data_access_required,
    get_note_attachments_from_http_post,
    get_note_topics_from_http_post,
    get_template_attachment_ids_from_http_post,
)
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.sis_advising import get_legacy_attachment_stream
from boac.lib.util import get_benchmarker, is_int, process_input_from_rich_text_editor, to_bool_or_none
from boac.merged.advising_note import (
    get_boa_attachment_stream,
    get_zip_stream_for_sid,
    note_to_compatible_json,
)
from boac.merged.calnet import get_calnet_user_for_uid
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.note import Note
from boac.models.note_attachment import NoteAttachment
from boac.models.note_read import NoteRead
from flask import current_app as app, request, Response
from flask_login import current_user


@app.route('/api/note/<note_id>')
@advising_data_access_required
def get_note(note_id):
    note = Note.find_by_id(note_id=note_id)
    if not note:
        raise ResourceNotFoundError('Note not found')
    note_read = NoteRead.when_user_read_note(current_user.get_id(), str(note.id))
    return tolerant_jsonify(_boa_note_to_compatible_json(note=note, note_read=note_read))


@app.route('/api/notes/<note_id>/mark_read', methods=['POST'])
@advising_data_access_required
def mark_note_read(note_id):
    if NoteRead.find_or_create(current_user.get_id(), note_id):
        return tolerant_jsonify({'status': 'created'}, status=201)
    else:
        raise BadRequestError(f'Failed to mark note {note_id} as read by user {current_user.get_uid()}')


@app.route('/api/notes/create', methods=['POST'])
@advising_data_access_required
def create_notes():
    benchmark = get_benchmarker('create_notes')
    params = request.form
    sids = _get_sids_for_note_creation()
    benchmark(f'SID count: {len(sids)}')
    body = params.get('body', None)
    is_private = to_bool_or_none(params.get('isPrivate', False))
    subject = params.get('subject', None)
    topics = get_note_topics_from_http_post()
    if not sids or not subject:
        benchmark('end (BadRequest)')
        raise BadRequestError('Note creation requires \'subject\' and \'sids\'')

    dept_codes = dept_codes_where_advising(current_user)
    if current_user.is_admin or not len(dept_codes):
        benchmark('end (Forbidden)')
        raise ForbiddenRequestError('Sorry, only advisors can create advising notes')
    if is_private and not current_user.can_access_private_notes:
        benchmark('end (Forbidden)')
        raise ForbiddenRequestError('Sorry, you are not authorized to manage note privacy.')

    attachments = get_note_attachments_from_http_post(tolerate_none=True)
    benchmark(f'Attachment count: {len(attachments)}')
    body = process_input_from_rich_text_editor(body)
    template_attachment_ids = get_template_attachment_ids_from_http_post()

    if len(sids) == 1:
        note = Note.create(
            **_get_author_profile(),
            attachments=attachments,
            body=body,
            is_private=is_private,
            sid=sids[0],
            subject=subject,
            template_attachment_ids=template_attachment_ids,
            topics=topics,
        )
        response = tolerant_jsonify(_boa_note_to_compatible_json(note, note_read=True))
    else:
        response = tolerant_jsonify(
            Note.create_batch(
                **_get_author_profile(),
                attachments=attachments,
                author_id=current_user.to_api_json()['id'],
                body=body,
                is_private=is_private,
                sids=sids,
                subject=subject,
                template_attachment_ids=template_attachment_ids,
                topics=topics,
            ),
        )
    benchmark('end')
    return response


@app.route('/api/notes/update', methods=['POST'])
@advising_data_access_required
def update_note():
    params = request.form
    body = params.get('body', None)
    is_private = to_bool_or_none(params.get('isPrivate', False))
    note_id = params.get('id', None)
    subject = params.get('subject', None)
    topics = get_note_topics_from_http_post()

    note = Note.find_by_id(note_id=note_id) if note_id else None
    if not note:
        raise ResourceNotFoundError('Note not found')
    if not subject:
        raise BadRequestError('Note subject is required')
    if note.author_uid != current_user.get_uid():
        raise ForbiddenRequestError('Sorry, you are not the author of this note.')
    if (is_private is not note.is_private) and not current_user.can_access_private_notes:
        raise ForbiddenRequestError('Sorry, you are not authorized to manage note privacy')

    note = Note.update(
        body=process_input_from_rich_text_editor(body),
        is_private=is_private,
        note_id=note_id,
        subject=subject,
        topics=topics,
    )
    note_read = NoteRead.find_or_create(current_user.get_id(), note_id)
    return tolerant_jsonify(_boa_note_to_compatible_json(note=note, note_read=note_read))


@app.route('/api/notes/delete/<note_id>', methods=['DELETE'])
@advising_data_access_required
def delete_note(note_id):
    if not current_user.is_admin:
        raise ForbiddenRequestError('Sorry, you are not authorized to delete notes.')
    note = Note.find_by_id(note_id=note_id)
    if not note:
        raise ResourceNotFoundError('Note not found')
    Note.delete(note_id=note_id)
    return tolerant_jsonify({'message': f'Note {note_id} deleted'}), 200


@app.route('/api/notes/<note_id>/attachments', methods=['POST'])
@advising_data_access_required
def add_attachments(note_id):
    note = Note.find_by_id(note_id=note_id)
    if note.author_uid != current_user.get_uid():
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
    if existing_note.author_uid != current_user.get_uid() and not current_user.is_admin:
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
        stream_data = get_legacy_attachment_stream(id_)
    else:
        attachment = NoteAttachment.find_by_id(id_)
        if attachment.note and attachment.note.is_private and not current_user.can_access_private_notes:
            raise ForbiddenRequestError('Unauthorized')
        stream_data = get_boa_attachment_stream(attachment)

    if not stream_data or not stream_data['stream']:
        return Response('Sorry, attachment not available.', mimetype='text/html', status=404)
    r = Response(stream_data['stream'])
    r.headers['Content-Type'] = 'application/octet-stream'
    encoding_safe_filename = urllib.parse.quote(stream_data['filename'].encode('utf8'))
    r.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoding_safe_filename}"
    return r


@app.route('/api/notes/download_for_sid/<sid>', methods=['GET'])
@director_advising_data_access_required
def download_notes_and_attachments(sid):
    stream_data = get_zip_stream_for_sid(sid)
    if not stream_data or not stream_data['stream']:
        return Response('Notes not available.', mimetype='text/html', status=404)
    r = Response(stream_data['stream'])
    r.headers['Content-Type'] = 'application/zip'
    r.headers['Content-Disposition'] = f"attachment; filename={stream_data['filename']}"
    return r


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
