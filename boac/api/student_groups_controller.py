"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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
import boac.api.util as api_util
from boac.lib.http import tolerant_jsonify
from boac.merged import member_details
from boac.models.student_group import StudentGroup
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/group/my_primary')
@login_required
def my_primary():
    group = StudentGroup.get_or_create_my_primary(current_user.id)
    decorated = _decorate_groups([group.to_api_json()], include_analytics=True)
    return tolerant_jsonify(decorated[0])


@app.route('/api/group/create', methods=['POST'])
@login_required
def create_group():
    params = request.get_json()
    name = params.get('name', None)
    if not name:
        raise BadRequestError('Group creation requires \'name\'')
    group = StudentGroup.create(current_user.id, name)
    return tolerant_jsonify(group.to_api_json())


@app.route('/api/group/<group_id>/add_student/<sid>')
@login_required
def add_student_to_group(group_id, sid):
    group = StudentGroup.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundError(f'No group found with id: {group_id}')
    if group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own group {group.id}')
    StudentGroup.add_student(group.id, sid)
    return tolerant_jsonify({'message': f'SID {sid} added to group \'{group_id}\''}), 200


@app.route('/api/group/delete/<group_id>', methods=['DELETE'])
@login_required
def delete_group(group_id):
    group = StudentGroup.find_by_id(group_id)
    if group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own group {group.id}')
    StudentGroup.delete(group_id)
    return tolerant_jsonify({'message': f'Group {group_id} has been deleted'}), 200


@app.route('/api/group/<group_id>')
@login_required
def get_group(group_id):
    group = StudentGroup.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundError(f'Sorry, no group found with id {group_id}.')
    if group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own group {group.id}')
    decorated = _decorate_groups([group.to_api_json()], include_analytics=True)
    return tolerant_jsonify(decorated[0])


@app.route('/api/group/<group_id>/remove_student/<sid>', methods=['DELETE'])
@login_required
def remove_student_from_group(group_id, sid):
    group = StudentGroup.find_by_id(group_id)
    if group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own group {group.id}')
    StudentGroup.remove_student(group_id, sid)
    return tolerant_jsonify({'message': f'SID {sid} has been removed from group {group_id}'}), 200


@app.route('/api/groups/my')
@login_required
def my_groups():
    groups = StudentGroup.get_groups_by_owner_id(current_user.id)
    return tolerant_jsonify(_decorate_groups([g.to_api_json() for g in groups], include_analytics=False))


@app.route('/api/group/students/add', methods=['POST'])
@login_required
def add_students_to_group():
    params = request.get_json()
    group_id = params.get('groupId')
    sids = params.get('sids')
    if not group_id or not len(sids):
        raise BadRequestError('The required parameters are \'groupId\' and \'sids\'.')
    group = StudentGroup.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundError(f'No group found where id={group_id}')
    if group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own group {group.id}')
    StudentGroup.add_students(group_id, sids)
    return tolerant_jsonify({'message': f'Successfully added students to group \'{group_id}\''}), 200


@app.route('/api/group/update', methods=['POST'])
@login_required
def update_group():
    params = request.get_json()
    name = params['name']
    if not name:
        raise BadRequestError('Requested cohort label is empty or invalid')
    group = StudentGroup.find_by_id(params['id'])
    if not group or group.owner_id != current_user.id:
        raise BadRequestError('Cohort does not exist or is not available to you')
    return tolerant_jsonify(StudentGroup.update(group_id=group.id, name=name).to_api_json())


def _decorate_groups(groups, include_analytics):
    for group in groups:
        member_details.merge_all(group['students'], include_analytics=include_analytics)
    return api_util.decorate_student_groups(current_user_id=current_user.id, groups=groups)
