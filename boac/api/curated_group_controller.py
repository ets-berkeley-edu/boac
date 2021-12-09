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

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import advisor_required, is_unauthorized_domain, response_with_students_csv_download
from boac.lib.berkeley import dept_codes_where_advising
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, get_benchmarker
from boac.merged import calnet
from boac.merged.admitted_student import get_admitted_students_by_sids
from boac.merged.student import get_student_query_scope as get_query_scope, get_summary_student_profiles
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.curated_group import CuratedGroup
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/curated_groups/all')
@advisor_required
def all_curated_groups():
    scope = get_query_scope(current_user)
    uids = AuthorizedUser.get_all_uids_in_scope(scope)
    groups_per_uid = dict((uid, []) for uid in uids)
    for group in CuratedGroup.get_groups_owned_by_uids(uids=uids):
        groups_per_uid[group['ownerUid']].append(group)
    api_json = []
    for uid, user in calnet.get_calnet_users_for_uids(app, uids).items():
        groups = groups_per_uid[uid]
        api_json.append({
            'user': user,
            'groups': sorted(groups, key=lambda g: g['name']),
        })
    api_json = sorted(api_json, key=lambda v: v['user']['name'] or f"UID: {v['user']['uid']}")
    return tolerant_jsonify(api_json)


@app.route('/api/curated_group/create', methods=['POST'])
@advisor_required
def create_curated_group():
    params = request.get_json()
    domain = get_param(params, 'domain', 'default')
    if is_unauthorized_domain(domain):
        raise ForbiddenRequestError(f'You are unauthorized to use the \'{domain}\' domain')
    name = params.get('name', None)
    if not name:
        raise BadRequestError('Curated group creation requires \'name\'')
    curated_group = CuratedGroup.create(domain=domain, name=name, owner_id=current_user.get_id())
    # Optionally, add students
    if 'sids' in params:
        sids = [sid for sid in set(params.get('sids')) if sid.isdigit()]
        CuratedGroup.add_students(curated_group_id=curated_group.id, sids=sids)
    return tolerant_jsonify(curated_group.to_api_json())


@app.route('/api/curated_group/delete/<curated_group_id>', methods=['DELETE'])
@advisor_required
def delete_curated_group(curated_group_id):
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'No curated group found with id: {curated_group_id}')
    if curated_group.owner_id != current_user.get_id():
        raise ForbiddenRequestError(f'Current user, {current_user.get_uid()}, does not own curated group {curated_group.id}')
    CuratedGroup.delete(curated_group_id)
    return tolerant_jsonify({'message': f'Curated group {curated_group_id} has been deleted'}), 200


@app.route('/api/curated_group/<curated_group_id>')
@advisor_required
def get_curated_group(curated_group_id):
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    order_by = get_param(request.args, 'orderBy', 'last_name')
    term_id = get_param(request.args, 'termId', None)
    curated_group = _curated_group_with_complete_student_profiles(
        curated_group_id=curated_group_id,
        limit=int(limit),
        offset=int(offset),
        order_by=order_by,
        term_id=term_id,
    )
    return tolerant_jsonify(curated_group)


@app.route('/api/curated_group/<curated_group_id>/download_csv', methods=['POST'])
@advisor_required
def download_csv(curated_group_id):
    benchmark = get_benchmarker(f'curated group {curated_group_id} download_csv')
    benchmark('begin')
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    params = request.get_json()
    fieldnames = get_param(params, 'csvColumnsSelected', [])
    if not curated_group:
        raise ResourceNotFoundError(f'No curated group found with id: {curated_group_id}')
    if not _can_current_user_view_curated_group(curated_group):
        raise ForbiddenRequestError(f'Current user, {current_user.get_uid()}, cannot view curated group {curated_group.id}')
    return response_with_students_csv_download(sids=CuratedGroup.get_all_sids(curated_group_id), fieldnames=fieldnames, benchmark=benchmark)


@app.route('/api/curated_group/<curated_group_id>/students_with_alerts')
@advisor_required
def get_students_with_alerts(curated_group_id):
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    benchmark = get_benchmarker(f'curated group {curated_group_id} students_with_alerts')
    benchmark('begin')
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'Sorry, no curated group found with id {curated_group_id}.')
    if not _can_current_user_view_curated_group(curated_group):
        raise ForbiddenRequestError(f'Current user, {current_user.get_uid()}, cannot view curated group {curated_group.id}')
    students = Alert.include_alert_counts_for_students(
        benchmark=benchmark,
        viewer_user_id=current_user.get_id(),
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
    benchmark('begin profile query')
    students_with_alerts = get_summary_student_profiles(sids=sids)
    benchmark('end profile query')
    for student in students_with_alerts:
        student['alertCount'] = alert_count_per_sid[student['sid']]
    benchmark('end')
    return tolerant_jsonify(students_with_alerts)


@app.route('/api/curated_group/<curated_group_id>/remove_student/<sid>', methods=['DELETE'])
@advisor_required
def remove_student_from_curated_group(curated_group_id, sid):
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'No curated group found with id: {curated_group_id}')
    if curated_group.owner_id != current_user.get_id():
        raise ForbiddenRequestError(f'Current user, {current_user.get_uid()}, does not own curated group {curated_group.id}')
    CuratedGroup.remove_student(curated_group_id, sid)
    return tolerant_jsonify(curated_group.to_api_json())


@app.route('/api/curated_group/students/add', methods=['POST'])
@advisor_required
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
    if curated_group.owner_id != current_user.get_id():
        raise ForbiddenRequestError(f'Current user, {current_user.get_uid()}, does not own curated group {curated_group.id}')
    CuratedGroup.add_students(curated_group_id=curated_group_id, sids=sids)
    if return_student_profiles:
        return tolerant_jsonify(_curated_group_with_complete_student_profiles(curated_group_id=curated_group_id))
    else:
        group = CuratedGroup.find_by_id(curated_group_id)
        return tolerant_jsonify(group.to_api_json())


@app.route('/api/curated_group/rename', methods=['POST'])
@advisor_required
def rename_curated_group():
    params = request.get_json()
    name = params['name']
    if not name:
        raise BadRequestError('Requested curated group name is empty or invalid')
    curated_group_id = params['id']
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group or curated_group.owner_id != current_user.get_id():
        raise BadRequestError('Curated group does not exist or is not available to you')
    CuratedGroup.rename(curated_group_id=curated_group.id, name=name)
    return tolerant_jsonify(CuratedGroup.find_by_id(curated_group_id).to_api_json())


def _curated_group_with_complete_student_profiles(
        curated_group_id,
        order_by='last_name',
        term_id=None,
        offset=0,
        limit=50,
):
    benchmark = get_benchmarker(f'curated group {curated_group_id} with student profiles')
    benchmark('begin')
    curated_group = CuratedGroup.find_by_id(curated_group_id)
    if not curated_group:
        raise ResourceNotFoundError(f'Sorry, no curated group found with id {curated_group_id}.')
    if not _can_current_user_view_curated_group(curated_group):
        raise ForbiddenRequestError(f'Current user, {current_user.get_uid()}, cannot view curated group {curated_group.id}')
    api_json = curated_group.to_api_json(order_by=order_by, offset=offset, limit=limit)
    sids = [s['sid'] for s in api_json['students']]
    benchmark('begin profile query')
    if curated_group.domain == 'admitted_students':
        api_json['students'] = get_admitted_students_by_sids(sids)
    else:
        api_json['students'] = get_summary_student_profiles(sids, term_id=term_id, include_historical=True)
    Alert.include_alert_counts_for_students(benchmark=benchmark, viewer_user_id=current_user.get_id(), group=api_json)
    benchmark('begin get_referencing_cohort_ids')
    api_json['referencingCohortIds'] = curated_group.get_referencing_cohort_ids()
    benchmark('end')
    return api_json


def _can_current_user_view_curated_group(curated_group):
    if current_user.is_admin:
        return True
    owner = AuthorizedUser.find_by_id(curated_group.owner_id)
    if not owner:
        return False
    curated_group_dept_codes = [m.university_dept.dept_code for m in owner.department_memberships]
    if len(curated_group_dept_codes):
        user_dept_codes = dept_codes_where_advising(current_user)
        return len([c for c in user_dept_codes if c in curated_group_dept_codes])
    else:
        return False
