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
from boac.api.util import sort_students_by_name
from boac.lib.http import tolerant_jsonify
from boac.merged.student import get_summary_student_profiles
from boac.models.alert import Alert
from boac.models.curated_cohort import CuratedCohort
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/curated_cohort/create', methods=['POST'])
@login_required
def create_curated_cohort():
    params = request.get_json()
    name = params.get('name', None)
    if not name:
        raise BadRequestError('Cohort creation requires \'name\'')
    curated_cohort = CuratedCohort.create(current_user.id, name)
    return tolerant_jsonify(curated_cohort.to_api_json())


@app.route('/api/curated_cohort/<curated_cohort_id>/add_student/<sid>')
@login_required
def add_student_to_curated_cohort(curated_cohort_id, sid):
    curated_cohort = CuratedCohort.find_by_id(curated_cohort_id)
    if not curated_cohort:
        raise ResourceNotFoundError(f'No cohort found with id: {curated_cohort_id}')
    if curated_cohort.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own cohort {curated_cohort.id}')
    CuratedCohort.add_student(curated_cohort.id, sid)
    return tolerant_jsonify(CuratedCohort.find_by_id(curated_cohort_id).to_api_json())


@app.route('/api/curated_cohort/delete/<curated_cohort_id>', methods=['DELETE'])
@login_required
def delete_curated_cohort(curated_cohort_id):
    curated_cohort = CuratedCohort.find_by_id(curated_cohort_id)
    if not curated_cohort:
        raise ResourceNotFoundError(f'No cohort found with id: {curated_cohort_id}')
    if curated_cohort.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own cohort {curated_cohort.id}')
    CuratedCohort.delete(curated_cohort_id)
    return tolerant_jsonify({'message': f'Cohort {curated_cohort_id} has been deleted'}), 200


@app.route('/api/curated_cohort/<curated_cohort_id>')
@login_required
def get_curated_cohort(curated_cohort_id):
    cohort = CuratedCohort.find_by_id(curated_cohort_id)
    if not cohort:
        raise ResourceNotFoundError(f'Sorry, no cohort found with id {curated_cohort_id}.')
    if cohort.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own cohort {cohort.id}')
    cohort = cohort.to_api_json(sids_only=True)
    sids = [s['sid'] for s in cohort['students']]
    cohort['students'] = sort_students_by_name(get_summary_student_profiles(sids))
    Alert.include_alert_counts_for_students(viewer_user_id=current_user.id, cohort=cohort)
    return tolerant_jsonify(cohort)


@app.route('/api/curated_cohort/<cohort_id>/students_with_alerts')
@login_required
def get_students_with_alerts(cohort_id):
    cohort = CuratedCohort.find_by_id(cohort_id)
    if not cohort:
        raise ResourceNotFoundError(f'Sorry, no cohort found with id {cohort_id}.')
    if cohort.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own cohort {cohort.id}')
    cohort = CuratedCohort.to_api_json(cohort, sids_only=True)
    students = Alert.include_alert_counts_for_students(viewer_user_id=current_user.id, cohort=cohort)
    alert_count_per_sid = {}
    for s in list(filter(lambda s: s.get('alertCount') > 0, students)):
        sid = s.get('sid')
        alert_count_per_sid[sid] = s.get('alertCount')
    sids = list(alert_count_per_sid.keys())
    students_with_alerts = get_summary_student_profiles(sids=sids)
    for student in students_with_alerts:
        student['alertCount'] = alert_count_per_sid[student['sid']]
    return tolerant_jsonify(sort_students_by_name(students_with_alerts))


@app.route('/api/curated_cohorts/my/<sid>')
@login_required
def curated_cohort_ids_per_sid(sid):
    return tolerant_jsonify(CuratedCohort.curated_cohort_ids_per_sid(user_id=current_user.id, sid=sid))


@app.route('/api/curated_cohort/<curated_cohort_id>/remove_student/<sid>', methods=['DELETE'])
@login_required
def remove_student_from_curated_cohort(curated_cohort_id, sid):
    curated_cohort = CuratedCohort.find_by_id(curated_cohort_id)
    if not curated_cohort:
        raise ResourceNotFoundError(f'No cohort found with id: {curated_cohort_id}')
    if curated_cohort.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own cohort {curated_cohort.id}')
    CuratedCohort.remove_student(curated_cohort_id, sid)
    return tolerant_jsonify(CuratedCohort.find_by_id(curated_cohort_id).to_api_json(include_students=False))


@app.route('/api/curated_cohort/students/add', methods=['POST'])
@login_required
def add_students_to_curated_cohort():
    params = request.get_json()
    curated_cohort_id = params.get('curatedCohortId')
    sids = [sid for sid in set(params.get('sids')) if sid.isdigit()]
    if not curated_cohort_id or not len(sids):
        raise BadRequestError('The required parameters are \'curatedCohortId\' and \'sids\'.')
    curated_cohort = CuratedCohort.find_by_id(curated_cohort_id)
    if not curated_cohort:
        raise ResourceNotFoundError(f'No cohort found where id={curated_cohort_id}')
    if curated_cohort.owner_id != current_user.id:
        raise ForbiddenRequestError(f'Current user, {current_user.uid}, does not own cohort {curated_cohort.id}')
    CuratedCohort.add_students(curated_cohort_id=curated_cohort_id, sids=sids)
    return tolerant_jsonify(CuratedCohort.find_by_id(curated_cohort_id).to_api_json(include_students=False))


@app.route('/api/curated_cohort/rename', methods=['POST'])
@login_required
def rename_curated_cohort():
    params = request.get_json()
    name = params['name']
    if not name:
        raise BadRequestError('Requested cohort label is empty or invalid')
    curated_cohort_id = params['id']
    curated_cohort = CuratedCohort.find_by_id(curated_cohort_id)
    if not curated_cohort or curated_cohort.owner_id != current_user.id:
        raise BadRequestError('Cohort does not exist or is not available to you')
    CuratedCohort.rename(curated_cohort_id=curated_cohort.id, name=name)
    return tolerant_jsonify(CuratedCohort.find_by_id(curated_cohort_id).to_api_json(include_students=False))
