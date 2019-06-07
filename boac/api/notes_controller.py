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

import urllib.parse

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import current_user_profile, feature_flag_edit_notes, get_dept_codes, get_dept_role
from boac.lib.http import tolerant_jsonify
from boac.lib.util import is_int, process_input_from_rich_text_editor
from boac.merged.advising_note import get_boa_attachment_stream, get_legacy_attachment_stream, note_to_compatible_json
from boac.models.cohort_filter import CohortFilter
from boac.models.curated_group import CuratedGroup
from boac.models.note import Note
from boac.models.note_read import NoteRead
from boac.models.topic import Topic
from flask import current_app as app, request, Response
from flask_login import current_user, login_required


@app.route('/api/notes/<note_id>/mark_read', methods=['POST'])
@login_required
def mark_read(note_id):
    if NoteRead.find_or_create(current_user.id, note_id):
        return tolerant_jsonify({'status': 'created'}, status=201)
    else:
        raise BadRequestError(f'Failed to mark note {note_id} as read by user {current_user.uid}')


@app.route('/api/notes/create', methods=['POST'])
@login_required
@feature_flag_edit_notes
def create_note():
    is_batch_create = False
    params = request.form
    sids = set()
    sid = params.get('sid', None)
    if sid:
        sids.add(sid)
    else:
        # Batch note creation
        sids = _get_sids_for_batch_note_creation(params)
        is_batch_create = True
    subject = params.get('subject', None)
    body = params.get('body', None)
    topics = _get_topics(params)
    if not sids or not subject:
        raise BadRequestError('Note creation requires \'subject\' and \'sid\'')
    dept_codes = get_dept_codes(current_user)
    if current_user.is_admin or not len(dept_codes):
        raise ForbiddenRequestError('Sorry, Admin users cannot create advising notes')
    profile = current_user_profile()
    # TODO: We capture one 'role' and yet user could have multiple, one per dept.
    role = get_dept_role(current_user.department_memberships[0])
    attachments = _get_attachments(request.files, tolerate_none=True)

    def _create_note(_sid):
        return Note.create(
            author_uid=current_user.uid,
            author_name=_get_name(profile),
            author_role=role,
            author_dept_codes=dept_codes,
            subject=subject,
            body=process_input_from_rich_text_editor(body),
            topics=topics,
            sid=_sid,
            attachments=attachments,
        )
    if is_batch_create:
        for sid in sids:
            _create_note(sid)
        return tolerant_jsonify({'message': f'Note created for {len(sids)} students'}), 200

    note = _create_note(sids.pop())
    note_json = Note.find_by_id(note.id).to_api_json()
    return tolerant_jsonify(
        note_to_compatible_json(
            note=note_json,
            note_read=NoteRead.find_or_create(current_user.id, note.id),
            attachments=note_json.get('attachments'),
            topics=note_json.get('topics'),
        ),
    )


@app.route('/api/notes/update', methods=['POST'])
@login_required
@feature_flag_edit_notes
def update_note():
    params = request.form
    note_id = params.get('id', None)
    subject = params.get('subject', None)
    body = params.get('body', None)
    topics = _get_topics(params)
    delete_ids_ = params.get('deleteAttachmentIds') or []
    delete_ids_ = delete_ids_ if isinstance(delete_ids_, list) else str(delete_ids_).split(',')
    delete_attachment_ids = [int(id_) for id_ in delete_ids_]
    if not note_id or not subject:
        raise BadRequestError('Note requires \'id\' and \'subject\'')
    if Note.find_by_id(note_id=note_id).author_uid != current_user.uid:
        raise ForbiddenRequestError('Sorry, you are not the author of this note.')
    note = Note.update(
        note_id=note_id,
        subject=subject,
        body=process_input_from_rich_text_editor(body),
        topics=topics,
        attachments=_get_attachments(request.files, tolerate_none=True),
        delete_attachment_ids=delete_attachment_ids,
    )
    note_json = note.to_api_json()
    return tolerant_jsonify(
        note_to_compatible_json(
            note=note_json,
            note_read=NoteRead.find_or_create(current_user.id, note_id),
            attachments=note_json.get('attachments'),
            topics=note_json.get('topics'),
        ),
    )


@app.route('/api/notes/delete/<note_id>', methods=['DELETE'])
@login_required
@feature_flag_edit_notes
def delete_note(note_id):
    if not current_user.is_admin:
        raise ForbiddenRequestError('Sorry, you are not authorized to delete notes.')
    note = Note.find_by_id(note_id=note_id)
    if not note:
        raise ResourceNotFoundError('Note not found')
    Note.delete(note_id=note_id)
    return tolerant_jsonify({'message': f'Note {note_id} deleted'}), 200


@app.route('/api/notes/topics', methods=['GET'])
@login_required
def get_topics():
    return tolerant_jsonify([topic.to_api_json() for topic in Topic.get()])


@app.route('/api/notes/<note_id>/attachment', methods=['POST'])
@login_required
@feature_flag_edit_notes
def add_attachment(note_id):
    if Note.find_by_id(note_id=note_id).author_uid != current_user.uid:
        raise ForbiddenRequestError('Sorry, you are not the author of this note.')
    attachments = _get_attachments(request.files)
    if len(attachments) != 1:
        raise BadRequestError('A single attachment file must be supplied.')
    note = Note.add_attachment(
        note_id=note_id,
        attachment=attachments[0],
    )
    note_json = note.to_api_json()
    return tolerant_jsonify(
        note_to_compatible_json(
            note=note_json,
            note_read=NoteRead.find_or_create(current_user.id, note_id),
            attachments=note_json.get('attachments'),
            topics=note_json.get('topics'),
        ),
    )


@app.route('/api/notes/<note_id>/attachment/<attachment_id>', methods=['DELETE'])
@login_required
@feature_flag_edit_notes
def remove_attachment(note_id, attachment_id):
    existing_note = Note.find_by_id(note_id=note_id)
    if not existing_note:
        raise BadRequestError('Note id not found.')
    if existing_note.author_uid != current_user.uid and not current_user.is_admin:
        raise ForbiddenRequestError('You are not authorized to remove attachments from this note.')
    note = Note.delete_attachment(
        note_id=note_id,
        attachment_id=int(attachment_id),
    )
    note_json = note.to_api_json()
    return tolerant_jsonify(
        note_to_compatible_json(
            note=note_json,
            note_read=NoteRead.find_or_create(current_user.id, note_id),
            attachments=note_json.get('attachments'),
            topics=note_json.get('topics'),
        ),
    )


@app.route('/api/notes/attachment/<attachment_id>', methods=['GET'])
@login_required
def download_attachment(attachment_id):
    is_legacy = not is_int(attachment_id)
    id_ = attachment_id if is_legacy else int(attachment_id)
    stream_data = get_legacy_attachment_stream(id_) if is_legacy else get_boa_attachment_stream(id_)
    if not stream_data or not stream_data['stream']:
        return Response('Sorry, attachment not available.', mimetype='text/html', status=404)
    r = Response(stream_data['stream'])
    r.headers['Content-Type'] = 'application/octet-stream'
    encoding_safe_filename = urllib.parse.quote(stream_data['filename'].encode('utf8'))
    r.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoding_safe_filename}"
    return r


def _get_name(user):
    first_name = user.get('firstName')
    last_name = user.get('lastName')
    return '' if not (first_name or last_name) else (first_name if not last_name else f'{first_name} {last_name}')


def _get_topics(params):
    topics = params.get('topics', ())
    return topics if isinstance(topics, list) else list(filter(None, str(topics).split(',')))


def _get_sids_for_batch_note_creation(params):
    def _get_param_as_set(key):
        lst = [v for v in request.form.getlist(key) if v.isdigit()]
        return set(lst) if lst else {}

    sids = _get_param_as_set('sids') if 'sids' in params else set()
    cohort_ids = _get_param_as_set('cohortIds')
    sids = sids.union(_get_sids_per_cohorts(cohort_ids))
    curated_group_ids = _get_param_as_set('curatedGroupIds')
    return sids.union(_get_sids_per_curated_groups(curated_group_ids))


def _get_sids_per_cohorts(cohort_ids=None):
    sids = []
    for cohort_id in cohort_ids or ():
        sids.append(CohortFilter.get_sids(cohort_id))
    return sids


def _get_sids_per_curated_groups(curated_group_ids=None):
    sids = []
    for cohort_id in curated_group_ids or ():
        sids.append(CuratedGroup.get_all_sids(cohort_id))
    return sids


def _get_attachments(request_files, tolerate_none=False):
    attachments = []
    for index in range(app.config['NOTES_ATTACHMENTS_MAX_PER_NOTE']):
        attachment = request_files.get(f'attachment[{index}]')
        if attachment:
            attachments.append(attachment)
        else:
            break
    if not tolerate_none and not len(attachments):
        raise BadRequestError('request.files is empty')
    byte_stream_bundle = []
    for attachment in attachments:
        filename = attachment.filename and attachment.filename.strip()
        if not filename:
            raise BadRequestError(f'Invalid file in request form data: {attachment}')
        else:
            byte_stream_bundle.append({
                'name': filename.rsplit('/', 1)[-1],
                'byte_stream': attachment.read(),
            })
    return byte_stream_bundle
