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

from boac.models.appointment import Appointment
from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
import simplejson as json

coe_advisor_uid = '90412'
coe_scheduler_uid = '6972201'
l_s_college_advisor_uid = '188242'
l_s_college_drop_in_advisor_uid = '53791'
l_s_college_scheduler_uid = '19735'


class TestCreateAppointment:

    @classmethod
    def _create_appointment(cls, client, dept_code, details='', expected_status_code=200):
        data = {
            'appointmentType': 'Drop-in',
            'deptCode': dept_code,
            'details': details,
            'sid': '3456789012',
            'topics': ['Appointment Topic 1', 'Appointment Topic 3'],
        }
        response = client.post(
            '/api/appointments/create',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _get_waitlist(cls, client, dept_code):
        response = client.get(f'/api/appointments/waitlist/{dept_code}')
        assert response.status_code == 200
        return response.json

    def test_create_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._create_appointment(client, 'COENG', expected_status_code=401)

    def test_create_appointment_as_coe_scheduler(self, client, fake_auth):
        """Scheduler can create appointments."""
        fake_auth.login(coe_scheduler_uid)
        details = 'Aloysius has some questions.'
        appointment = self._create_appointment(client, 'COENG', details)
        waitlist = self._get_waitlist(client, 'COENG')
        matching = next((a for a in waitlist if a['details'] == details), None)
        assert appointment['id'] == matching['id']
        assert appointment['read'] is True
        assert appointment['student']['sid'] == '3456789012'
        assert appointment['student']['name'] == 'Paul Kerschen'
        assert appointment['student']['photoUrl']
        assert appointment['appointmentType'] == 'Drop-in'
        assert len(appointment['topics']) == 2

    def test_other_departments_forbidden(self, client, fake_auth):
        fake_auth.login(coe_scheduler_uid)
        self._create_appointment(client, 'UWASC', expected_status_code=403)

    def test_nonsense_department_not_found(self, client, fake_auth):
        fake_auth.login(coe_scheduler_uid)
        self._create_appointment(client, 'DINGO', expected_status_code=404)


class TestAppointmentCheckIn:

    @classmethod
    def _create_appointment(cls, client, appointment_id, expected_status_code=200):
        response = client.post(
            f'/api/appointments/{appointment_id}/check_in',
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._create_appointment(client, 1, expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is an advisor without drop_in responsibilities."""
        fake_auth.login(l_s_college_advisor_uid)
        self._create_appointment(client, 1, expected_status_code=401)


class TestAppointmentWaitlist:

    @classmethod
    def _get_waitlist(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/appointments/waitlist/{dept_code}')
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._get_waitlist(client, 'COENG', 401)

    def test_unrecognized_dept_code(self, app, client, fake_auth):
        """Returns 404 if requested dept_code is invalid."""
        fake_auth.login(l_s_college_scheduler_uid)
        self._get_waitlist(client, 'BOGUS', 404)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is an advisor without drop_in responsibilities."""
        fake_auth.login(l_s_college_advisor_uid)
        self._get_waitlist(client, 'QCADV', 401)

    def test_l_and_s_advisor_cannot_view_coe_waitlist(self, app, client, fake_auth):
        """L&S advisor cannot view COE appointments (waitlist)."""
        fake_auth.login(l_s_college_scheduler_uid)
        self._get_waitlist(client, 'COENG', 403)

    def test_coe_scheduler_waitlist(self, app, client, fake_auth):
        """COE advisor can only see COE appointments."""
        fake_auth.login(coe_scheduler_uid)
        appointments = self._get_waitlist(client, 'COENG')
        assert len(appointments) == 2

        appointment = appointments[0]
        assert appointment['id'] > 0
        assert appointment['advisorName'] == 'Johnny C. Lately'
        assert appointment['advisorUid'] == coe_advisor_uid
        assert appointment['advisorDepartments'] == [{'code': 'COENG', 'name': 'College of Engineering'}]
        assert appointment['createdAt'] is not None
        assert appointment['createdBy'] == coe_scheduler_uid
        assert 'crossroads' in appointment['details']
        assert appointment['appointmentType'] == 'Drop-in'
        assert appointment['student']['sid'] == '3456789012'
        assert appointment['student']['name'] == 'Paul Kerschen'
        assert len(appointment['topics']) == 1

    def test_l_and_s_advisor_waitlist(self, app, client, fake_auth):
        """L&S advisor can only see L&S appointments."""
        fake_auth.login(l_s_college_scheduler_uid)
        appointments = self._get_waitlist(client, 'QCADV')
        assert len(appointments) == 2

    def test_l_s_college_drop_in_advisor_uid_waitlist(self, app, client, fake_auth):
        """L&S drop-in advisor can only see L&S appointments."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        appointments = self._get_waitlist(client, 'QCADV')
        assert len(appointments) == 2


class TestMarkAppointmentRead:

    @classmethod
    def _mark_appointment_read(cls, client, appointment_id, expected_status_code=200):
        response = client.post(
            f'/api/appointments/{appointment_id}/mark_read',
            data=json.dumps({'appointmentId': appointment_id}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._mark_appointment_read(client, 1, expected_status_code=401)

    def test_advisor_read_appointment(self, app, client, fake_auth):
        """L&S advisor reads an appointment."""
        # Confirm that appointment is not read
        appointment = Appointment.create(
            created_by=coe_scheduler_uid,
            dept_code='COENG',
            details='A COE appointment.',
            student_sid='5678901234',
            appointment_type='Drop-in',
            topics=['Appointment Topic 2'],
        )
        user_id = AuthorizedUser.get_id_per_uid(l_s_college_advisor_uid)
        assert AppointmentRead.was_read_by(user_id, appointment.id) is False
        # Next, log in and verify API
        fake_auth.login(l_s_college_advisor_uid)
        api_json = self._mark_appointment_read(client, appointment.id)
        assert api_json['appointmentId'] == appointment.id
        assert api_json['viewerId'] == user_id
        assert AppointmentRead.was_read_by(user_id, appointment.id) is True


class TestAppointmentTopics:

    @classmethod
    def _get_topics(cls, client, expected_status_code=200):
        response = client.get('/api/appointments/topics')
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._get_topics(client, 401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is an advisor without drop_in responsibilities."""
        fake_auth.login(l_s_college_advisor_uid)
        self._get_topics(client, 401)

    def test_scheduler_get_topics(self, app, client, fake_auth):
        """COE scheduler can get topics."""
        fake_auth.login(coe_scheduler_uid)
        topics = self._get_topics(client)
        assert len(topics) == 5

    def test_advisor_get_topics(self, app, client, fake_auth):
        """COE advisor can get topics."""
        fake_auth.login(coe_advisor_uid)
        topics = self._get_topics(client)
        assert len(topics) == 5
