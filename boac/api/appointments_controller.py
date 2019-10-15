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
from boac.merged.student import get_distilled_student_profiles
from boac.models.appointment import Appointment
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
        waitlist = [a.to_api_json(current_user.get_id()) for a in Appointment.get_waitlist(dept_code)]
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
            checked_in_by=current_user.get_uid(),
            advisor_dept_codes=params.get('advisorDeptCodes', None),
            advisor_name=params.get('advisorName', None),
            advisor_role=params.get('advisorRole', None),
            advisor_uid=advisor_uid,
        )
        return tolerant_jsonify(appointment.to_api_json(current_user.get_id()))
    else:
        raise ForbiddenRequestError(f'You are unauthorized to manage {appointment.dept_code} appointments.')


@app.route('/api/appointments/create', methods=['POST'])
@scheduler_required
def create_appointment():
    params = request.get_json()
    dept_code = params.get('deptCode', None)
    sid = params.get('sid', None)
    topics = params.get('topics', None)
    if not dept_code or not sid or not len(topics):
        raise BadRequestError('Appointment creation: required parameters were not provided')
    appointment = Appointment.create(
        created_by=current_user.get_uid(),
        dept_code=dept_code,
        details=params.get('details', None),
        student_sid=sid,
        topics=topics,
    )
    AppointmentRead.find_or_create(current_user.get_id(), appointment.id)
    return tolerant_jsonify(appointment.to_api_json(current_user.get_id()))


@app.route('/api/appointments/<appointment_id>/mark_read', methods=['POST'])
@advisor_required
def mark_appointment_read(appointment_id):
    return tolerant_jsonify(AppointmentRead.find_or_create(current_user.get_id(), int(appointment_id)).to_api_json())


@app.route('/api/appointments/topics')
@scheduler_required
def get_appointment_topics():
    topics = Topic.get_all(available_in_appointments=True)
    return tolerant_jsonify([topic.to_api_json() for topic in topics])


def _dept_codes_with_scheduler_privilege():
    departments = [d for d in current_user.departments if d.get('isScheduler') or d.get('isDropInAdvisor')]
    return [d['code'] for d in departments]


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
