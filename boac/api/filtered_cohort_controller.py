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
from boac.api.util import decorate_cohort, strip_analytics
from boac.lib import util
from boac.lib.berkeley import can_view_cohort, get_dept_codes
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.merged.student import get_summary_student_profiles
from boac.models.cohort_filter import CohortFilter
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/filtered_cohorts/all')
@login_required
def all_cohorts():
    cohorts_per_uid = {}
    for cohort in CohortFilter.all_cohorts():
        if can_view_cohort(current_user, cohort):
            for authorized_user in cohort.owners:
                uid = authorized_user.uid
                if uid not in cohorts_per_uid:
                    cohorts_per_uid[uid] = []
                cohorts_per_uid[uid].append(decorate_cohort(cohort, include_students=False))
    owners = []
    for uid in cohorts_per_uid.keys():
        owner = calnet.get_calnet_user_for_uid(app, uid)
        owner.update({
            'cohorts': sorted(cohorts_per_uid[uid], key=lambda c: c['name']),
        })
        owners.append(owner)
    owners = sorted(owners, key=lambda o: (o['firstName'], o['lastName']))
    return tolerant_jsonify(owners)


@app.route('/api/filtered_cohorts/my')
@login_required
def my_cohorts():
    uid = current_user.get_id()
    cohorts = [decorate_cohort(c, include_alerts_for_uid=uid, include_students=False) for c in CohortFilter.all_owned_by(uid)]
    alert_sids = []
    for cohort in cohorts:
        alert_sids += [a['sid'] for a in cohort.get('alerts', [])]
    alert_profiles = get_summary_student_profiles(alert_sids)
    alert_profiles_by_sid = {p['sid']: p for p in alert_profiles}
    for cohort in cohorts:
        for alert in cohort.get('alerts', []):
            alert.update(alert_profiles_by_sid[alert['sid']])
            strip_analytics(alert)
    return tolerant_jsonify(cohorts)


@app.route('/api/filtered_cohort/<cohort_id>')
@login_required
def get_cohort(cohort_id):
    order_by = util.get(request.args, 'orderBy', None)
    offset = util.get(request.args, 'offset', 0)
    limit = util.get(request.args, 'limit', 50)
    cohort = CohortFilter.find_by_id(int(cohort_id))
    if cohort and can_view_cohort(current_user, cohort):
        cohort = decorate_cohort(cohort, order_by, int(offset), int(limit), include_profiles=True)
        return tolerant_jsonify(cohort)
    else:
        raise ResourceNotFoundError(f'No cohort found with identifier: {cohort_id}')


@app.route('/api/filtered_cohort/create', methods=['POST'])
@login_required
def create_cohort():
    params = request.get_json()
    label = util.get(params, 'label', None)
    advisor_ldap_uids = util.get(params, 'advisorLdapUids')
    coe_prep_statuses = util.get(params, 'coePrepStatuses')
    genders = util.get(params, 'genders')
    gpa_ranges = util.get(params, 'gpaRanges')
    group_codes = util.get(params, 'groupCodes')
    levels = util.get(params, 'levels')
    majors = util.get(params, 'majors')
    unit_ranges = util.get(params, 'unitRanges')
    in_intensive_cohort = util.to_bool_or_none(util.get(params, 'inIntensiveCohort'))
    is_inactive_asc = util.get(params, 'isInactiveAsc')
    coe_authorized = current_user.is_admin or 'COENG' in get_dept_codes(current_user)
    if not label:
        raise BadRequestError('Cohort creation requires \'label\'')
    if not coe_authorized and (advisor_ldap_uids or coe_prep_statuses):
        raise ForbiddenRequestError(f'You are unauthorized to use COE-specific search criteria.')
    asc_authorized = current_user.is_admin or 'UWASC' in get_dept_codes(current_user)
    if not asc_authorized and (in_intensive_cohort is not None or is_inactive_asc is not None):
        raise ForbiddenRequestError('You are unauthorized to use ASC-specific search criteria.')
    cohort = CohortFilter.create(
        uid=current_user.get_id(),
        label=label,
        advisor_ldap_uids=advisor_ldap_uids,
        coe_prep_statuses=coe_prep_statuses,
        genders=genders,
        gpa_ranges=gpa_ranges,
        group_codes=group_codes,
        levels=levels,
        majors=majors,
        unit_ranges=unit_ranges,
        in_intensive_cohort=in_intensive_cohort,
        is_inactive_asc=is_inactive_asc,
    )
    return tolerant_jsonify(decorate_cohort(cohort))


@app.route('/api/filtered_cohort/rename', methods=['POST'])
@login_required
def update_cohort():
    params = request.get_json()
    cohort_id = int(params['id'])
    uid = current_user.get_id()
    label = params['label']
    if not label:
        raise BadRequestError('Requested cohort label is empty or invalid')
    cohort = next((c for c in CohortFilter.all_owned_by(uid) if c.id == cohort_id), None)
    if not cohort:
        raise BadRequestError(f'Cohort does not exist or is not owned by {uid}')
    cohort = decorate_cohort(CohortFilter.rename(cohort_id=cohort.id, label=label), include_students=False)
    return tolerant_jsonify(cohort)


@app.route('/api/filtered_cohort/delete/<cohort_id>', methods=['DELETE'])
@login_required
def delete_cohort(cohort_id):
    if cohort_id.isdigit():
        cohort_id = int(cohort_id)
        uid = current_user.get_id()
        cohort = next((c for c in CohortFilter.all_owned_by(uid) if c.id == cohort_id), None)
        if cohort:
            CohortFilter.delete(cohort_id)
            return tolerant_jsonify({'message': f'Cohort deleted (id={cohort_id})'}), 200
        else:
            raise BadRequestError(f'User {uid} does not own cohort_filter with id={cohort_id}')
    else:
        raise ForbiddenRequestError(f'Programmatic deletion of canned cohorts is not allowed (id={cohort_id})')
