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

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import (
    advising_data_access_required,
    get_note_attachments_from_http_post,
    get_note_topics_from_http_post,
    validate_advising_note_set_date,
)
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.util import process_input_from_rich_text_editor, to_bool_or_none
from boac.models.note_draft import NoteDraft
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/note_draft/create', methods=['POST'])
@advising_data_access_required
def create_note_draft():
    params = request.form
    body = params.get('body', None)
    contact_type = params.get('contactType', None)
    is_private = to_bool_or_none(params.get('isPrivate', False))
    set_date = validate_advising_note_set_date(params)
    subject = params.get('subject', None)
    sids = _get_sids_from_http_post()
    topics = get_note_topics_from_http_post()
    if not sids or not subject:
        raise BadRequestError('Required parameters are missing')
    user_dept_codes = dept_codes_where_advising(current_user)
    if current_user.is_admin or not len(user_dept_codes):
        raise ForbiddenRequestError('Sorry, only advisors can create advising notes')

    attachments = get_note_attachments_from_http_post(tolerate_none=True)

    note_draft = NoteDraft.create(
        attachments=attachments,
        body=process_input_from_rich_text_editor(body),
        contact_type=contact_type,
        creator_id=current_user.get_id(),
        is_private=is_private,
        set_date=set_date,
        sids=sids,
        subject=subject,
        topics=topics,
    )
    return tolerant_jsonify(note_draft.to_api_json(include_students=True))


@app.route('/api/note_draft/<note_draft_id>')
@advising_data_access_required
def get_note_draft(note_draft_id):
    note_draft = NoteDraft.find_by_id(note_draft_id=note_draft_id)
    if not note_draft:
        raise ResourceNotFoundError('Draft not found')
    if note_draft.creator_id != current_user.get_id():
        raise ForbiddenRequestError('Draft not available')
    return tolerant_jsonify(note_draft.to_api_json())


@app.route('/api/note_drafts/my')
@advising_data_access_required
def get_my_note_drafts():
    user_id = current_user.get_id()
    note_drafts = NoteDraft.get_all_draft_notes() if current_user.is_admin else NoteDraft.get_drafts_created_by(creator_id=user_id)
    return tolerant_jsonify([t.to_api_json(include_students=True) for t in note_drafts])


@app.route('/api/note_draft/update', methods=['POST'])
@advising_data_access_required
def update_note_draft():
    params = request.form
    note_draft_id = params.get('id', None)
    subject = params.get('subject', None)
    if not subject:
        raise BadRequestError('Requires \'subject\'')
    body = params.get('body', None)
    delete_ids_ = params.get('deleteAttachmentIds') or []
    delete_ids_ = delete_ids_ if isinstance(delete_ids_, list) else str(delete_ids_).split(',')
    delete_attachment_ids = [int(id_) for id_ in delete_ids_]
    sids = _get_sids_from_http_post()
    topics = get_note_topics_from_http_post()
    note_draft = NoteDraft.find_by_id(note_draft_id=note_draft_id)
    if not note_draft:
        raise ResourceNotFoundError('Draft not found')
    if note_draft.creator_id != current_user.get_id():
        raise ForbiddenRequestError('Draft not available.')
    note_draft = NoteDraft.update(
        attachments=get_note_attachments_from_http_post(tolerate_none=True),
        contact_type=None,
        body=process_input_from_rich_text_editor(body),
        delete_attachment_ids=delete_attachment_ids,
        note_draft_id=note_draft_id,
        is_private=False,
        set_date=None,
        sids=sids,
        subject=subject,
        topics=topics,
    )
    return tolerant_jsonify(note_draft.to_api_json())


@app.route('/api/note_draft/delete/<note_draft_id>', methods=['DELETE'])
@advising_data_access_required
def delete_note_draft(note_draft_id):
    note_draft = NoteDraft.find_by_id(note_draft_id=note_draft_id)
    if not note_draft:
        raise ResourceNotFoundError('Draft not found')
    if note_draft.creator_id != current_user.get_id():
        raise ForbiddenRequestError('Draft not available')
    NoteDraft.delete(note_draft_id=note_draft_id)
    return tolerant_jsonify({'message': f'Note draft {note_draft_id} deleted'}), 200


def _get_sids_from_http_post():
    sids = request.form.get('sids', ())
    return sids if isinstance(sids, list) else list(filter(None, str(sids).split(',')))
