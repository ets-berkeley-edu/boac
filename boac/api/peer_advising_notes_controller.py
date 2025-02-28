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

from boac.api.decorators import peer_advisor_manager_required, peer_advisor_or_peer_advisor_manager, \
    peer_advisor_or_peer_advisor_manager_in_department, peer_advisor_required
from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import get_boac_note_as_compatible_json, get_note_author_profile_of_current_user, \
    get_note_topics_from_http_post, validate_note_contact_type
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, process_input_from_rich_text_editor
from boac.models.note import Note
from boac.models.note_read import NoteRead
from boac.models.note_template import NoteTemplate
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.peer_advising_topic import PeerAdvisingTopic
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/peer_advising/note_template/create', methods=['POST'])
@peer_advisor_manager_required
def create_peer_advising_note_template():
    params = request.get_json()
    peer_advising_department_id = params.get('peerAdvisingDeptId', None)
    note_body = params.get('body', None)
    topics = params.get('topics', None)
    title = params.get('title', None)
    if not peer_advising_department_id or not note_body or not title:
        raise BadRequestError('Invalid or missing parameters')
    user_dept_codes = dept_codes_where_advising(current_user.departments)
    if current_user.is_admin or not len(user_dept_codes):
        raise ForbiddenRequestError('Sorry, only advisors can create advising note templates')

    note_template = NoteTemplate.create(
        body=note_body,
        topics=topics,
        title=title,
        creator_id=current_user.get_id(),
        peer_advising_department_id=peer_advising_department_id,
    )

    return tolerant_jsonify(note_template.to_api_json())


@app.route('/api/peer_advising/note_topics')
@peer_advisor_or_peer_advisor_manager
def get_peer_advising_topics():
    return tolerant_jsonify([topic.to_api_json() for topic in PeerAdvisingTopic.get_all()])


@app.route('/api/peer_advising/note_template/<note_template_id>')
@peer_advisor_or_peer_advisor_manager
def get_peer_advising_note_template(note_template_id):
    note_template = NoteTemplate.find_by_id(note_template_id=note_template_id)
    if not note_template:
        raise ResourceNotFoundError('Template not found')
    if not PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
            user_id=current_user.get_id(),
            peer_advising_department_id=note_template.peer_advising_department_id):
        raise ForbiddenRequestError('Template not available')
    return tolerant_jsonify(note_template.to_api_json())


@app.route('/api/peer_advising/note_templates/peer_advising_department_id/<peer_advising_department_id>')
@peer_advisor_or_peer_advisor_manager_in_department
def get_note_templates_for_peer_advising_department(peer_advising_department_id):
    note_templates = NoteTemplate.get_templates_created_by_peer_advising_department(peer_advising_department_id=peer_advising_department_id)
    return tolerant_jsonify([t.to_api_json() for t in note_templates])


@app.route('/api/peer_advising/note_template/update', methods=['POST'])
@peer_advisor_manager_required
def update_peer_advising_note_template():
    params = request.get_json() or {}
    note_template_id = params.get('id', None)
    body = params.get('body', None)
    title = params.get('title', None)
    topics = params.get('topics', None)
    note_template = NoteTemplate.find_by_id(note_template_id=note_template_id)
    if not note_template:
        raise ResourceNotFoundError('Template not found')
    if not PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
            user_id=current_user.get_id(),
            peer_advising_department_id=note_template.peer_advising_department_id):
        raise ForbiddenRequestError('Template not available')
    note_template = NoteTemplate.update(
        body=process_input_from_rich_text_editor(body),
        note_template_id=note_template_id,
        topics=topics,
        title=title,
    )
    return tolerant_jsonify(note_template.to_api_json())


@app.route('/api/peer_advising/note_template/delete/<note_template_id>', methods=['DELETE'])
@peer_advisor_manager_required
def delete_peer_advising_note_template(note_template_id):
    note_template = NoteTemplate.find_by_id(note_template_id=note_template_id)
    if not note_template:
        raise ResourceNotFoundError('Template not found')
    if not PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
            user_id=current_user.get_id(),
            peer_advising_department_id=note_template.peer_advising_department_id):
        raise ForbiddenRequestError('Template not available')
    NoteTemplate.delete(note_template_id=note_template_id)
    return tolerant_jsonify({'message': f'Note template {note_template_id} deleted'}), 200


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


@app.route('/api/peer_advisor/notes')
@peer_advisor_required
def get_notes_for_peer_advisor():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 50))
    memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(current_user.get_id())
    notes = Note.get_notes_by_peer_advising_department(
        limit=limit,
        offset=offset,
        peer_advising_department_id=memberships[0]['peer_advising_department_id'],
    )
    notes_read_by_user = NoteRead.get_notes_read_by_user(
        note_ids=[str(note.id) for note in notes],
        viewer_id=current_user.get_id(),
    )
    api_json = []
    for note in notes:
        api_json.append(get_boac_note_as_compatible_json(
            note=note,
            note_read=note.id in notes_read_by_user),
        )
    return tolerant_jsonify(api_json)
