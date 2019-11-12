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
from boac.api.util import advisor_required, appointments_feature_flag, drop_in_advisors_for_dept_code, scheduler_required
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import tolerant_jsonify
from boac.merged.student import get_distilled_student_profiles
from boac.models.appointment import Appointment
from boac.models.appointment_event import appointment_event_type, AppointmentEvent
from boac.models.appointment_read import AppointmentRead
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/appointments/waitlist/<dept_code>')
@appointments_feature_flag
@scheduler_required
def get_waitlist(dept_code):
    def _is_current_user_authorized():
        return current_user.is_admin or dept_code in _dept_codes_with_scheduler_privilege()

    dept_code = dept_code.upper()
    if dept_code not in BERKELEY_DEPT_CODE_TO_NAME:
        raise ResourceNotFoundError(f'Unrecognized department code: {dept_code}')
    elif _is_current_user_authorized():
        show_all_statuses = current_user.is_drop_in_advisor or current_user.is_admin
        statuses = appointment_event_type.enums if show_all_statuses else ['reserved', 'waiting']
        my_reserved = []
        others = []
        canceled = []
        for appointment in Appointment.get_waitlist(dept_code, statuses):
            a = appointment.to_api_json(current_user.get_id())
            if a['status'] == 'canceled':
                canceled.append(a)
            elif a['status'] == 'reserved' and a['statusBy']['id'] == current_user.get_id():
                my_reserved.append(a)
            else:
                others.append(a)
        waitlist = my_reserved + others + canceled
        _put_student_profile_per_appointment(waitlist)
        return tolerant_jsonify({
            'advisors': drop_in_advisors_for_dept_code(dept_code),
            'waitlist': waitlist,
        })
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage {dept_code} appointments.')


@app.route('/api/appointments/<appointment_id>')
@appointments_feature_flag
@advisor_required
def get_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not appointment:
        raise ResourceNotFoundError('Unknown path')
    api_json = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([api_json])
    return tolerant_jsonify(api_json)


@app.route('/api/appointments/<appointment_id>/check_in', methods=['POST'])
@appointments_feature_flag
@scheduler_required
def appointment_check_in(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not appointment:
        raise ResourceNotFoundError('Unknown path')
    if appointment.dept_code not in _dept_codes_with_scheduler_privilege():
        raise ForbiddenRequestError(f'You are unauthorized to manage {appointment.dept_code} appointments.')
    if not appointment.status_change_available():
        raise BadRequestError(appointment.to_api_json(current_user.get_id()))
    params = request.get_json()
    advisor_uid = params.get('advisorUid', None)
    if not advisor_uid:
        raise BadRequestError('Appointment check-in requires "advisor_uid"')
    appointment = Appointment.check_in(
        appointment_id=appointment_id,
        checked_in_by=current_user.get_id(),
        advisor_dept_codes=params.get('advisorDeptCodes', None),
        advisor_name=params.get('advisorName', None),
        advisor_role=params.get('advisorRole', None),
        advisor_uid=advisor_uid,
    )
    api_json = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([api_json])
    return tolerant_jsonify(api_json)


@app.route('/api/appointments/<appointment_id>/cancel', methods=['POST'])
@appointments_feature_flag
@scheduler_required
def cancel_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not appointment:
        raise ResourceNotFoundError('Unknown path')
    has_privilege = current_user.is_admin or appointment.dept_code in _dept_codes_with_scheduler_privilege()
    if not has_privilege:
        raise ForbiddenRequestError(f'You are unauthorized to manage {appointment.dept_code} appointments.')
    if not appointment.status_change_available():
        raise BadRequestError(appointment.to_api_json(current_user.get_id()))
    params = request.get_json()
    cancel_reason = params.get('cancelReason', None)
    cancel_reason_explained = params.get('cancelReasonExplained', None)
    appointment = Appointment.cancel(
        appointment_id=appointment_id,
        canceled_by=current_user.get_id(),
        cancel_reason=cancel_reason,
        cancel_reason_explained=cancel_reason_explained,
    )
    api_json = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([api_json])
    return tolerant_jsonify(api_json)


@app.route('/api/appointments/<appointment_id>/reserve', methods=['GET'])
@appointments_feature_flag
@scheduler_required
def reserve_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not appointment:
        raise ResourceNotFoundError('Unknown path')
    has_privilege = current_user.is_admin or appointment.dept_code in _dept_codes_with_scheduler_privilege()
    if not has_privilege:
        raise ForbiddenRequestError(f'You are unauthorized to manage appointment {appointment_id}.')
    if not appointment.status_change_available():
        raise BadRequestError(appointment.to_api_json(current_user.get_id()))
    appointment = Appointment.reserve(
        appointment_id=appointment_id,
        reserved_by=current_user.get_id(),
    )
    api_json = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([api_json])
    return tolerant_jsonify(api_json)


@app.route('/api/appointments/<appointment_id>/unreserve', methods=['GET'])
@appointments_feature_flag
@scheduler_required
def unreserve_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not appointment:
        raise ResourceNotFoundError('Unknown path')
    has_privilege = current_user.is_admin or appointment.dept_code in _dept_codes_with_scheduler_privilege()
    if not has_privilege:
        raise ForbiddenRequestError(f'You are unauthorized to manage appointment {appointment_id}.')
    if appointment.status != 'reserved':
        raise BadRequestError(appointment.to_api_json(current_user.get_id()))
    event = AppointmentEvent.get_most_recent_per_type(appointment.id, 'reserved')
    if event.user_id != current_user.get_id():
        raise ForbiddenRequestError(f'You did not reserve appointment {appointment_id}.')
    appointment = Appointment.unreserve(
        appointment_id=appointment_id,
        unreserved_by=current_user.get_id(),
    )
    api_json = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([api_json])
    return tolerant_jsonify(api_json)


@app.route('/api/appointments/create', methods=['POST'])
@appointments_feature_flag
@scheduler_required
def create_appointment():
    params = request.get_json()
    dept_code = params.get('deptCode', None)
    sid = params.get('sid', None)
    appointment_type = params.get('appointmentType', None)
    topics = params.get('topics', None)
    if not dept_code or not sid or not appointment_type or not len(topics):
        raise BadRequestError('Appointment creation: required parameters were not provided')
    dept_code = dept_code.upper()
    if dept_code not in BERKELEY_DEPT_CODE_TO_NAME:
        raise ResourceNotFoundError(f'Unrecognized department code: {dept_code}')
    if dept_code not in _dept_codes_with_scheduler_privilege():
        raise ForbiddenRequestError(f'You are unauthorized to manage {dept_code} appointments.')
    appointment = Appointment.create(
        advisor_dept_codes=params.get('advisorDeptCodes', None),
        advisor_name=params.get('advisorName', None),
        advisor_role=params.get('advisorRole', None),
        advisor_uid=params.get('advisorUid', None),
        appointment_type=appointment_type,
        created_by=current_user.get_id(),
        dept_code=dept_code,
        details=params.get('details', None),
        student_sid=sid,
        topics=topics,
    )
    AppointmentRead.find_or_create(current_user.get_id(), appointment.id)
    api_json = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([api_json])
    return tolerant_jsonify(api_json)


@app.route('/api/appointments/<appointment_id>/mark_read', methods=['POST'])
@appointments_feature_flag
@advisor_required
def mark_appointment_read(appointment_id):
    return tolerant_jsonify(AppointmentRead.find_or_create(current_user.get_id(), int(appointment_id)).to_api_json())


@app.route('/api/appointments/advisors/find_by_name', methods=['GET'])
@appointments_feature_flag
@advisor_required
def find_appointment_advisors_by_name():
    query = request.args.get('q')
    if not query:
        raise BadRequestError('Search query must be supplied')
    limit = request.args.get('limit')
    query_fragments = filter(None, query.upper().split(' '))
    advisors = Appointment.find_advisors_by_name(query_fragments, limit=limit)

    def _advisor_feed(a):
        return {
            'label': a.advisor_name,
            'uid': a.advisor_uid,
        }
    return tolerant_jsonify([_advisor_feed(a) for a in advisors])


def _dept_codes_with_scheduler_privilege():
    scheduler_dept_codes = [d['code'] for d in current_user.departments if d.get('isScheduler')]
    drop_in_advisor_dept_codes = [d['deptCode'] for d in current_user.drop_in_advisor_departments]
    return scheduler_dept_codes + drop_in_advisor_dept_codes


def _put_student_profile_per_appointment(waitlist):
    if len(waitlist):
        appointments_by_sid = {}
        for appointment in waitlist:
            sid = appointment['student']['sid']
            if sid not in appointments_by_sid:
                appointments_by_sid[sid] = []
            appointments_by_sid[sid].append(appointment)
        distinct_sids = list(appointments_by_sid.keys())
        for student in get_distilled_student_profiles(distinct_sids):
            sid = student['sid']
            for appointment in appointments_by_sid[sid]:
                appointment['student'] = student
