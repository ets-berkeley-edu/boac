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
from boac.api.util import advisor_required, scheduler_required
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.merged.student import get_distilled_student_profiles
from boac.models.appointment import Appointment
from boac.models.appointment_event import AppointmentEvent
from boac.models.appointment_read import AppointmentRead
from boac.models.topic import Topic
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/appointments/waitlist/<dept_code>')
@scheduler_required
def get_waitlist(dept_code):
    def _is_current_user_authorized():
        if current_user.is_admin:
            return True
        else:
            return dept_code in _dept_codes_with_scheduler_privilege()

    dept_code = dept_code.upper()
    if dept_code not in BERKELEY_DEPT_CODE_TO_NAME:
        raise ResourceNotFoundError(f'Unrecognized department code: {dept_code}')
    elif _is_current_user_authorized():
        include_resolved = to_bool_or_none(request.args.get('includeResolved'))
        waitlist = [a.to_api_json(current_user.get_id()) for a in Appointment.get_waitlist(dept_code, include_resolved)]
        _put_student_profile_per_appointment(waitlist)
        return tolerant_jsonify(waitlist)
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage {dept_code} appointments.')


@app.route('/api/appointments/<appointment_id>/check_in', methods=['POST'])
@scheduler_required
def appointment_check_in(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if appointment.dept_code in _dept_codes_with_scheduler_privilege():
        params = request.get_json()
        advisor_uid = params.get('advisorUid', None)
        if not advisor_uid:
            raise BadRequestError('Appointment check-in requires \'advisor_uid\'')
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
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage {appointment.dept_code} appointments.')


@app.route('/api/appointments/<appointment_id>/cancel', methods=['POST'])
@scheduler_required
def cancel_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if current_user.is_admin or appointment.dept_code in _dept_codes_with_scheduler_privilege():
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
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage {appointment.dept_code} appointments.')


@app.route('/api/appointments/<appointment_id>/reserve', methods=['GET'])
@scheduler_required
def reserve_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not app.config['FEATURE_FLAG_ADVISOR_APPOINTMENTS'] or not appointment:
        raise ResourceNotFoundError('Unknown path')

    has_privilege = current_user.is_admin or appointment.dept_code in _dept_codes_with_scheduler_privilege()
    if has_privilege and appointment.status in ('reserved', 'waiting'):
        appointment = Appointment.reserve(
            appointment_id=appointment_id,
            reserved_by=current_user.get_id(),
        )
        api_json = appointment.to_api_json(current_user.get_id())
        _put_student_profile_per_appointment([api_json])
        return tolerant_jsonify(api_json)
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage appointment {appointment_id}.')


@app.route('/api/appointments/<appointment_id>/unreserve', methods=['GET'])
@scheduler_required
def unreserve_appointment(appointment_id):
    appointment = Appointment.find_by_id(appointment_id)
    if not app.config['FEATURE_FLAG_ADVISOR_APPOINTMENTS'] or not appointment:
        raise ResourceNotFoundError('Unknown path')

    has_privilege = current_user.is_admin or appointment.dept_code in _dept_codes_with_scheduler_privilege()
    if has_privilege and appointment.status == 'reserved':
        event = AppointmentEvent.get_most_recent_per_type(appointment.id, 'reserved')
        if event.user_id == current_user.get_id():
            appointment = Appointment.unreserve(
                appointment_id=appointment_id,
                unreserved_by=current_user.get_id(),
            )
            api_json = appointment.to_api_json(current_user.get_id())
            _put_student_profile_per_appointment([api_json])
            return tolerant_jsonify(api_json)
        else:
            raise ForbiddenRequestError(f'You did not reserve appointment {appointment_id}.')
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage appointment {appointment_id}.')


@app.route('/api/appointments/create', methods=['POST'])
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
        created_by=current_user.get_id(),
        dept_code=dept_code,
        details=params.get('details', None),
        appointment_type=appointment_type,
        student_sid=sid,
        topics=topics,
    )
    AppointmentRead.find_or_create(current_user.get_id(), appointment.id)
    appointment_feed = appointment.to_api_json(current_user.get_id())
    _put_student_profile_per_appointment([appointment_feed])
    return tolerant_jsonify(appointment_feed)


@app.route('/api/appointments/<appointment_id>/mark_read', methods=['POST'])
@advisor_required
def mark_appointment_read(appointment_id):
    return tolerant_jsonify(AppointmentRead.find_or_create(current_user.get_id(), int(appointment_id)).to_api_json())


@app.route('/api/appointments/advisors/find_by_name', methods=['GET'])
@advisor_required
def find_appointment_advisors_by_name():
    if not app.config['FEATURE_FLAG_ADVISOR_APPOINTMENTS']:
        raise ResourceNotFoundError('Unknown path')
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


@app.route('/api/appointments/topics', methods=['GET'])
@scheduler_required
def get_appointment_topics():
    if not app.config['FEATURE_FLAG_ADVISOR_APPOINTMENTS']:
        raise ResourceNotFoundError('Unknown path')
    include_deleted = to_bool_or_none(request.args.get('includeDeleted'))
    topics = Topic.get_all(available_in_appointments=True, include_deleted=include_deleted)
    return tolerant_jsonify([topic.to_api_json() for topic in topics])


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
