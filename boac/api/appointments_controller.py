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

from boac.api.errors import BadRequestError
from boac.api.util import advisor_required, scheduler_required
from boac.lib.http import tolerant_jsonify
from boac.models.appointment import Appointment
from boac.models.topic import Topic
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/appointments/waitlist')
@scheduler_required
def get_waitlist():
    return tolerant_jsonify([a.to_api_json() for a in Appointment.get_waitlist()])


@app.route('/api/appointments/<appointment_id>/check_in', methods=['POST'])
@scheduler_required
def appointment_check_in(appointment_id):
    return tolerant_jsonify({'status': f'Appointment check-in (id: {appointment_id})'}, status=200)


@app.route('/api/appointments/create', methods=['POST'])
@scheduler_required
def create_appointment():
    params = request.get_json()
    advisor_dept_codes = params.get('advisorDeptCodes', None)
    advisor_name = params.get('advisorName', None)
    advisor_uid = params.get('advisorUid', None)
    sid = params.get('sid', None)
    topics = params.get('topics', None)
    if not advisor_name or not advisor_uid or not sid or not len(topics):
        raise BadRequestError('Appointment creation: required parameters were not provided')
    if not len(advisor_dept_codes) and not current_user.is_admin:
        raise BadRequestError('One or more departments required per advisor')
    appointment = Appointment.create(
        advisor_dept_codes=advisor_dept_codes,
        advisor_name=advisor_name,
        advisor_role=params.get('advisorRole', None),
        advisor_uid=advisor_uid,
        created_by=current_user.get_uid(),
        details=params.get('details', None),
        student_sid=sid,
        topics=topics,
    )
    return tolerant_jsonify(appointment.to_api_json())


@app.route('/api/appointments/<appointment_id>/mark_read', methods=['POST'])
@advisor_required
def mark_appointment_read(appointment_id):
    return tolerant_jsonify({'status': f'Marked as read (id: {appointment_id})'}, status=200)


@app.route('/api/appointments/topics')
@scheduler_required
def get_appointment_topics():
    topics = Topic.get_all(available_in_appointments=True)
    return tolerant_jsonify([topic.to_api_json() for topic in topics])
