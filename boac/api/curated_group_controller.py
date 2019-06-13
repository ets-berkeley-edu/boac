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

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import get_my_curated_groups
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param
from boac.merged.student import get_summary_student_profiles
from boac.models.alert import Alert
from boac.models.curated_group import CuratedGroup
from flask import current_app as app, request
from flask_cors import cross_origin
from flask_login import current_user, login_required


@app.route('/api/curated_groups/my')
@login_required
def my_curated_groups():
    return tolerant_jsonify(get_my_curated_groups())


@app.route('/api/curated_group/create', methods=['POST'])
@login_required
def create_curated_group():
    params = request.get_json()
    name = params.get('name', None)
    if not name:
        raise BadRequestError('Curated group creation requires \'name\'')
    curated_group = CuratedGroup.create(current_user.id, name)
    # Optionally, add students
    if 'sids' in params:
        sids = [sid for sid in set(params.get('sids')) if sid.isdigit()]
        CuratedGroup.add_students(curated_group_id=curated_group.id, sids=sids)
    return tolerant_jsonify(curated_group.to_api_json())


@app.route('/api/curated_group/delete/<curated_group_id>', methods=['DELETE'])
@login_required
@cross_origin(allow_headers=['Content-Type'])
def delete_curated_group(curated_group_id):
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'No curated group found with id: {curated_group_id}')
    if curated_group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own curated group {curated_group.id}')
    CuratedGroup.delete(curated_group_id)
    return tolerant_jsonify({'message': f'Curated group {curated_group_id} has been deleted'}), 200


@app.route('/api/curated_group/<curated_group_id>')
@login_required
def get_curated_group(curated_group_id):
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    order_by = get_param(request.args, 'orderBy', 'last_name')
    curated_group = _curated_group_with_complete_student_profiles(curated_group_id, order_by, int(offset), int(limit))
    return tolerant_jsonify(curated_group)


@app.route('/api/curated_group/<curated_group_id>/students_with_alerts')
@login_required
def get_students_with_alerts(curated_group_id):
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'Sorry, no curated group found with id {curated_group_id}.')
    if curated_group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own curated group {curated_group.id}')
    students = Alert.include_alert_counts_for_students(
        viewer_user_id=current_user.id,
        group={'sids': CuratedGroup.get_all_sids(curated_group_id)},
        count_only=True,
        offset=offset,
        limit=limit,
    )
    alert_count_per_sid = {}
    for s in list(filter(lambda s: s.get('alertCount') > 0, students)):
        sid = s.get('sid')
        alert_count_per_sid[sid] = s.get('alertCount')
    sids = list(alert_count_per_sid.keys())
    students_with_alerts = get_summary_student_profiles(sids=sids)
    for student in students_with_alerts:
        student['alertCount'] = alert_count_per_sid[student['sid']]
    return tolerant_jsonify(students_with_alerts)


@app.route('/api/curated_groups/my/<sid>')
@login_required
def curated_group_ids_per_sid(sid):
    return tolerant_jsonify(CuratedGroup.curated_group_ids_per_sid(user_id=current_user.id, sid=sid))


@app.route('/api/curated_group/<curated_group_id>/remove_student/<sid>', methods=['DELETE'])
@login_required
@cross_origin(allow_headers=['Content-Type'])
def remove_student_from_curated_group(curated_group_id, sid):
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'No curated group found with id: {curated_group_id}')
    if curated_group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own curated group {curated_group.id}')
    CuratedGroup.remove_student(curated_group_id, sid)
    return tolerant_jsonify(curated_group.to_api_json())


@app.route('/api/curated_group/students/add', methods=['POST'])
@login_required
def add_students_to_curated_group():
    params = request.get_json()
    curated_group_id = params.get('curatedGroupId')
    return_student_profiles = params.get('returnStudentProfiles')
    sids = [sid for sid in set(params.get('sids')) if sid.isdigit()]
    if not curated_group_id or not len(sids):
        raise BadRequestError('The required parameters are \'curatedGroupId\' and \'sids\'.')
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'No curated group found where id={curated_group_id}')
    if curated_group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own curated group {curated_group.id}')
    CuratedGroup.add_students(curated_group_id=curated_group_id, sids=sids)
    if return_student_profiles:
        return tolerant_jsonify(_curated_group_with_complete_student_profiles(curated_group_id=curated_group_id))
    else:
        group = CuratedGroup.find_by_id(curated_group_id)
        return tolerant_jsonify(group.to_api_json())


@app.route('/api/curated_group/rename', methods=['POST'])
@login_required
def rename_curated_group():
    params = request.get_json()
    name = params['name']
    if not name:
        raise BadRequestError('Requested curated group name is empty or invalid')
    curated_group_id = params['id']
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group or curated_group.owner_id != current_user.id:
        raise BadRequestError('Curated group does not exist or is not available to you')
    CuratedGroup.rename(curated_group_id=curated_group.id, name=name)
    return tolerant_jsonify(CuratedGroup.find_by_id(curated_group_id).to_api_json())


def _curated_group_with_complete_student_profiles(curated_group_id, order_by='last_name', offset=0, limit=50):
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'Sorry, no curated group found with id {curated_group_id}.')
    if curated_group.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own curated group {curated_group.id}')
    api_json = curated_group.to_api_json(order_by=order_by, offset=offset, limit=limit)
    sids = [s['sid'] for s in api_json['students']]
    api_json['students'] = get_summary_student_profiles(sids)
    Alert.include_alert_counts_for_students(viewer_user_id=current_user.id, group=api_json)
    return api_json
