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

from boac import std_commit
from boac.lib.util import localize_datetime, utc_now
from boac.models.appointment import Appointment
from boac.models.appointment_availability import AppointmentAvailability
from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
from boac.models.authorized_user_extension import DropInAdvisor
import pytest
import simplejson as json
from sqlalchemy import and_
from tests.util import mock_legacy_appointment_attachment, override_config


coe_advisor_uid = '211159'
coe_advisor_no_advising_data_uid = '1022796'
coe_drop_in_advisor_uid = '90412'
coe_drop_in_advisor_2_uid = '1133399'
coe_scheduler_uid = '6972201'
l_s_college_advisor_uid = '188242'
l_s_college_drop_in_advisor_uid = '53791'
l_s_college_scheduler_uid = '19735'
student_sid = '3456789012'


@pytest.fixture()
def coe_advisor_id():
    return AuthorizedUser.get_id_per_uid(coe_advisor_uid)


@pytest.fixture()
def l_s_advisor_id():
    return AuthorizedUser.get_id_per_uid(l_s_college_advisor_uid)


class AppointmentTestUtil:

    @classmethod
    def get_appointment(cls, client, appointment_id, expected_status_code=200):
        response = client.get(f'/api/appointments/{appointment_id}')
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def cancel_appointment(
            cls,
            client,
            appointment_id,
            cancel_reason,
            cancel_reason_explained=None,
            expected_status_code=200,
    ):
        data = {
            'cancelReason': cancel_reason,
            'cancelReasonExplained': cancel_reason_explained,
        }
        response = client.post(
            f'/api/appointments/{appointment_id}/cancel',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code

    @classmethod
    def check_in_appointment(cls, client, appointment_id, advisor_uid=None, expected_status_code=200):
        data = {
            'advisorUid': advisor_uid,
        }
        response = client.post(
            f'/api/appointments/{appointment_id}/check_in',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code

    @classmethod
    def get_scheduled_today(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/appointments/today/{dept_code}')
        assert response.status_code == expected_status_code
        if response.status_code == 200:
            return response.json

    @classmethod
    def _create_appointment(
            cls,
            client,
            appointment_type,
            dept_code,
            details=None,
            advisor_uid=None,
            scheduled_time=None,
            student_contact_info=None,
            student_contact_type=None,
            expected_status_code=200,
    ):
        data = {
            'advisorUid': advisor_uid,
            'appointmentType': appointment_type,
            'deptCode': dept_code,
            'details': details or '',
            'scheduledTime': scheduled_time,
            'studentContactInfo': student_contact_info,
            'studentContactType': student_contact_type,
            'sid': student_sid,
            'topics': ['Topic for appointments, 1', 'Topic for appointments, 4'],
        }
        response = client.post(
            '/api/appointments/create',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def create_drop_in_appointment(cls, client, dept_code, details=None, **kwargs):
        return cls._create_appointment(client, 'Drop-in', dept_code, details, **kwargs)

    @classmethod
    def create_scheduled_appointment(cls, client, dept_code, scheduled_time, advisor_uid, details=None, **kwargs):
        today = localize_datetime(utc_now()).strftime('%Y-%m-%d')
        kwargs.update({
            'scheduled_time': f'{today}T{scheduled_time}:00',
            'student_contact_info': '+15108675309',
            'student_contact_type': 'phone',
        })
        return cls._create_appointment(client, 'Scheduled', dept_code, details, advisor_uid, **kwargs)

    @classmethod
    def reserve_appointment(cls, client, appointment_id, advisor_uid, expected_status_code=200):
        data = {
            'advisorUid': advisor_uid,
        }
        response = client.post(
            f'/api/appointments/{appointment_id}/reserve',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code


class TestCreateDropInAppointment:

    @classmethod
    def _get_waitlist(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/appointments/waitlist/{dept_code}')
        assert response.status_code == expected_status_code
        if response.status_code == 200:
            return response.json['waitlist']

    def test_create_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            AppointmentTestUtil.create_drop_in_appointment(client, 'COENG', expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.create_drop_in_appointment(client, 'COENG', expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(coe_scheduler_uid)
        AppointmentTestUtil.create_drop_in_appointment(client, 'COENG', expected_status_code=401)

    def test_create_drop_in_appointment_as_coe_scheduler(self, app, client, fake_auth):
        """Scheduler can create appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            details = 'Aloysius has some questions.'
            appointment = AppointmentTestUtil.create_drop_in_appointment(client, 'COENG', details)
            appointment_id = appointment['id']
            waitlist = self._get_waitlist(client, 'COENG')
            matching = next((a for a in waitlist['unresolved'] if a['details'] == details), None)
            assert matching
            assert appointment_id == matching['id']
            assert appointment['read'] is True
            assert appointment['status'] == 'waiting'
            assert appointment['statusBy']['uid'] == coe_scheduler_uid
            assert appointment['student']['sid'] == student_sid
            assert appointment['student']['name'] == 'Pauline Kerschen'
            assert appointment['student']['photoUrl']
            assert appointment['appointmentType'] == 'Drop-in'
            assert len(appointment['topics']) == 2
            # Verify that a deleted appointment is off the waitlist
            Appointment.delete(appointment_id)
            waitlist = self._get_waitlist(client, 'COENG')
            assert next((a for a in waitlist['unresolved'] if a['details'] == details), None) is None

    def test_create_pre_reserved_appointment_for_specific_advisor(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            details = 'Aloysius has some questions.'
            appointment = AppointmentTestUtil.create_drop_in_appointment(
                client=client,
                dept_code='COENG',
                details=details,
                advisor_uid=coe_drop_in_advisor_uid,
            )
            appointment_id = appointment['id']
            waitlist = self._get_waitlist(client, 'COENG')
            matching = next((a for a in waitlist['unresolved'] if a['details'] == details), None)
            assert appointment_id == matching['id']
            assert 'COENG' in [d['code'] for d in appointment['advisorDepartments']]
            assert appointment['advisorName'] == 'COE Add Visor'
            assert appointment['advisorRole'] == 'Advisor'
            assert appointment['advisorUid'] == coe_drop_in_advisor_uid
            assert appointment['advisorId'] is not None
            assert appointment['read'] is True
            assert appointment['status'] == 'reserved'
            assert appointment['statusBy']['uid'] == coe_scheduler_uid

    def test_log_resolved_issue_as_coe_scheduler(self, app, client, fake_auth):
        """Scheduler can resolve issues on their own."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            details = 'Turns out Aloysius just needed directions to La Val\'s.'
            appointment = AppointmentTestUtil.create_drop_in_appointment(
                client=client,
                dept_code='COENG',
                details=details,
                advisor_uid=coe_scheduler_uid,
            )
            appointment_id = appointment['id']

            fake_auth.login(coe_drop_in_advisor_uid)
            student_feed = client.get(f'/api/student/by_sid/{student_sid}').json
            appointments = student_feed['notifications']['appointment']
            appointment = next((a for a in appointments if a['id'] == appointment_id), None)
            assert appointment['advisor']['title'] == 'Intake Desk'
            assert appointment['advisor']['uid'] == coe_scheduler_uid
            assert appointment['details'] == details
            assert appointment['status'] == 'checked_in'
            assert appointment['statusBy']['uid'] == coe_scheduler_uid

    def test_other_departments_forbidden(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            AppointmentTestUtil.create_drop_in_appointment(client, 'UWASC', expected_status_code=403)

    def test_nonsense_department_not_found(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            AppointmentTestUtil.create_drop_in_appointment(client, 'DINGO', expected_status_code=404)


class TestCreateScheduledAppointment:

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.create_scheduled_appointment(
                client=client,
                dept_code='COENG',
                details='failed attempt',
                scheduled_time='13:00',
                advisor_uid=coe_advisor_no_advising_data_uid,
                expected_status_code=401,
            )

    def test_create_scheduled_appointment_as_coe_scheduler(self, app, client, fake_auth, coe_advisor_id):
        """Scheduler can create appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            today = localize_datetime(utc_now()).strftime('%a')
            AppointmentAvailability.create(coe_advisor_id, 'COENG', '13:00', '14:00', today)
            schedule_today = AppointmentTestUtil.get_scheduled_today(client, 'COENG')
            assert len(schedule_today['openings']) == 2

            details = 'Aloysius has some questions.'
            appointment = AppointmentTestUtil.create_scheduled_appointment(
                client=client,
                dept_code='COENG',
                details=details,
                scheduled_time='13:00',
                advisor_uid=coe_advisor_uid,
            )
            appointment_id = appointment['id']
            schedule_today = AppointmentTestUtil.get_scheduled_today(client, 'COENG')
            assert len(schedule_today['openings']) == 1

            matching = next((a for a in schedule_today['appointments'] if a['details'] == details), None)
            assert matching
            assert appointment_id == matching['id']
            assert appointment['read'] is True
            assert appointment['status'] == 'reserved'
            assert appointment['statusBy']['uid'] == coe_scheduler_uid
            assert appointment['student']['sid'] == student_sid
            assert appointment['student']['name'] == 'Pauline Kerschen'
            assert appointment['student']['photoUrl']
            assert appointment['appointmentType'] == 'Scheduled'
            assert appointment['scheduledTime'].startswith(localize_datetime(utc_now()).strftime('%Y-%m-%d'))
            assert appointment['scheduledTime'].endswith('+00:00')
            # UTC time representation will vary dependending on time of year.
            assert '20:00:00' in appointment['scheduledTime'] or '21:00:00' in appointment['scheduledTime']
            assert appointment['studentContactInfo'] == '+15108675309'
            assert appointment['studentContactType'] == 'phone'
            assert len(appointment['topics']) == 2

            # Verify that a deleted appointment is off the waitlist.
            Appointment.delete(appointment_id)
            schedule_today = AppointmentTestUtil.get_scheduled_today(client, 'COENG')
            assert next((a for a in schedule_today['appointments'] if a['details'] == details), None) is None
            assert len(schedule_today['openings']) == 2


class TestGetAppointment:

    def test_not_authenticated(self, client, app):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            AppointmentTestUtil.get_appointment(client, 'COENG', expected_status_code=401)

    def test_not_authorized(self, client, app, fake_auth):
        """Returns 401 if user is scheduler."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            AppointmentTestUtil.get_appointment(client, 1, 401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.get_appointment(client, 1, 401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(coe_scheduler_uid)
        AppointmentTestUtil.get_appointment(client, 1, 401)

    def test_get_appointment(self, client, app, fake_auth):
        """Get appointment."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_uid)
            appointment = AppointmentTestUtil.get_appointment(client, 1)
            assert appointment
            assert appointment['id'] == 1
            assert appointment['status'] is not None


class TestAppointmentUpdate:

    @classmethod
    def _api_appointment_update(
            cls,
            client,
            appointment_id,
            details,
            topics=(),
            scheduled_time=None,
            expected_status_code=200,
    ):
        data = {
            'id': appointment_id,
            'details': details,
            'topics': topics,
            'scheduledTime': scheduled_time,
        }
        response = client.post(
            f'/api/appointments/{appointment_id}/update',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            self._api_appointment_update(client, 1, 'Hack the appointment!', expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            self._api_appointment_update(client, 1, 'Advise the appointment!', expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is a non-dropin advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._api_appointment_update(client, 1, 'Advise the appointment!', expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        self._api_appointment_update(client, 1, 'Advise the appointment!', expected_status_code=401)

    def test_appointment_not_found(self, app, client, fake_auth):
        """Returns 404 if appointment is not found."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            self._api_appointment_update(client, 99999999, 'Drop in the appointment!', expected_status_code=404)

    def test_update_appointment_details(self, app, client, fake_auth):
        """Allows drop-in advisor to update appointment details."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            created = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            expected_details = 'Why lookst thou so? - With my crossbow I shot the albatross.'
            self._api_appointment_update(
                client,
                created['id'],
                expected_details,
                created['topics'],
            )
            updated_appt = Appointment.find_by_id(appointment_id=created['id'])
            assert updated_appt.details == expected_details

    def test_update_appointment_topics(self, app, client, fake_auth):
        """Allows drop-in advisor to update appointment topics."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            created = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            expected_topics = ['Practice Makes Perfect', 'French Film Blurred']
            details = created['details']
            appt_id = created['id']
            updated = self._api_appointment_update(client, appt_id, details, expected_topics)
            assert len(updated['topics']) == 2
            assert set(updated['topics']) == set(expected_topics)

            # Remove topics
            removed = self._api_appointment_update(client, appt_id, details, ['Practice Makes Perfect'])
            std_commit(allow_test_environment=True)
            assert len(removed['topics']) == 1

            # Finally, re-add topics
            restored = self._api_appointment_update(client, appt_id, details, expected_topics)
            std_commit(allow_test_environment=True)
            assert set(restored['topics']) == set(expected_topics)

    def test_reschedule_appointment(self, app, client, fake_auth, coe_advisor_id):
        """Scheduler can reschedule appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS', ['COENG']):
            today = localize_datetime(utc_now()).strftime('%a')
            AppointmentAvailability.create(coe_advisor_id, 'COENG', '13:00', '16:00', today)
            fake_auth.login(coe_scheduler_uid)

            openings = AppointmentTestUtil.get_scheduled_today(client, 'COENG')['openings']
            assert len(openings) == 6

            details = 'Aloysius has some questions.'
            appointment = AppointmentTestUtil.create_scheduled_appointment(
                client=client,
                dept_code='COENG',
                details=details,
                scheduled_time='13:00',
                advisor_uid=coe_advisor_uid,
            )
            # UTC time representation will vary depending on time of year.
            scheduled_time = appointment['scheduledTime']
            assert '20:00:00' in scheduled_time or '21:00:00' in scheduled_time
            appointment_id = appointment['id']

            openings = AppointmentTestUtil.get_scheduled_today(client, 'COENG')['openings']
            assert len(openings) == 5
            assert next((o for o in openings if o['startTime'] == scheduled_time), None) is None

            today = localize_datetime(utc_now()).strftime('%Y-%m-%d')
            updated = self._api_appointment_update(client, appointment_id, details, scheduled_time=f'{today}T15:00:00')
            updated_scheduled_time = updated['scheduledTime']
            assert '22:00:00' in updated_scheduled_time or '23:00:00' in updated_scheduled_time

            openings = AppointmentTestUtil.get_scheduled_today(client, 'COENG')['openings']
            assert len(openings) == 5
            assert next((o for o in openings if o['startTime'] == scheduled_time), None) is not None
            assert next((o for o in openings if o['startTime'] == updated_scheduled_time), None) is None


class TestAppointmentAvailability:

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.get_scheduled_today(client, 'COENG', expected_status_code=401)

    def test_per_department_schedule(self, app, client, fake_auth, l_s_advisor_id):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_SAME_DAY_APPTS', ['QCADV', 'QCADVMAJ']):
            fake_auth.login(l_s_college_scheduler_uid)
            today = localize_datetime(utc_now()).strftime('%a')
            AppointmentAvailability.create(l_s_advisor_id, 'QCADV', '10:00', '12:00', today)
            AppointmentAvailability.create(l_s_advisor_id, 'QCADVMAJ', '12:00', '13:00', today)
            AppointmentAvailability.create(l_s_advisor_id, 'QCADV', '14:00', '15:30', today)
            openings = AppointmentTestUtil.get_scheduled_today(client, 'QCADV')['openings']
            assert len(openings) == 7
            for o in openings:
                assert o['uid'] == l_s_college_advisor_uid
            if '17:00:00+00:00' in openings[0]['startTime']:
                assert '17:30:00+00:00' in openings[0]['endTime']
                assert '17:30:00+00:00' in openings[1]['startTime']
                assert '18:00:00+00:00' in openings[1]['endTime']
                assert '22:00:00+00:00' in openings[6]['startTime']
                assert '22:30:00+00:00' in openings[6]['endTime']
            else:
                assert '18:00:00+00:00' in openings[0]['startTime']
                assert '18:30:00+00:00' in openings[0]['endTime']
                assert '18:30:00+00:00' in openings[1]['startTime']
                assert '19:00:00+00:00' in openings[1]['endTime']
                assert '23:00:00+00:00' in openings[6]['startTime']
                assert '23:30:00+00:00' in openings[6]['endTime']


class TestAppointmentCancel:

    def test_mark_read_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            AppointmentTestUtil.cancel_appointment(client, 1, 'Cancelled by student', expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.cancel_appointment(client, 1, 'Cancelled by advisor', expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is an advisor without drop_in responsibilities."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            AppointmentTestUtil.cancel_appointment(client, 1, 'Cancelled by advisor', expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        AppointmentTestUtil.cancel_appointment(client, 1, 'Cancelled by advisor', expected_status_code=401)

    def test_double_cancel_conflict(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            AppointmentTestUtil.cancel_appointment(client, waiting['id'], 'Cancelled by weasels')
            fake_auth.login(l_s_college_scheduler_uid)
            AppointmentTestUtil.cancel_appointment(client, waiting['id'], 'Cancelled by stoats', expected_status_code=400)

    def test_check_in_cancel_conflict(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            AppointmentTestUtil.check_in_appointment(client, waiting['id'], l_s_college_drop_in_advisor_uid)
            fake_auth.login(l_s_college_scheduler_uid)
            AppointmentTestUtil.cancel_appointment(client, waiting['id'], 'Cancelled by wolves', expected_status_code=400)

    def test_appointment_cancel(self, app, client, fake_auth):
        """Drop-in advisor can cancel appointment."""
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            advisor = DropInAdvisor.advisors_for_dept_code(dept_code)[0]
            user = AuthorizedUser.find_by_id(advisor.authorized_user_id)
            fake_auth.login(user.uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(
                client=client,
                dept_code=dept_code,
                details='Minor in Klingon',
                advisor_uid=user.uid,
            )
            AppointmentTestUtil.cancel_appointment(client, waiting['id'], 'Cancelled by wolves')
            # Verify
            appointment = AppointmentTestUtil.get_appointment(client, appointment_id=waiting['id'])
            appointment_id = appointment['id']
            assert appointment_id == waiting['id']
            assert appointment['advisorDepartments'] is None
            assert appointment['advisorName'] is None
            assert appointment['advisorRole'] is None
            assert appointment['advisorUid'] is None
            assert appointment['advisorId'] is None
            assert appointment['status'] == 'cancelled'
            assert appointment['statusBy']['id'] == user.id
            assert appointment['statusBy']['uid'] == user.uid
            assert appointment['statusDate'] is not None
            Appointment.delete(appointment_id)


class TestAppointmentCheckIn:

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            AppointmentTestUtil.check_in_appointment(client, 1, l_s_college_advisor_uid, expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.check_in_appointment(client, 1, coe_advisor_no_advising_data_uid, expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is not a drop-in advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            AppointmentTestUtil.check_in_appointment(client, 1, l_s_college_advisor_uid, expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        AppointmentTestUtil.check_in_appointment(client, 1, l_s_college_drop_in_advisor_uid, expected_status_code=401)

    def test_double_check_in_conflict(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            AppointmentTestUtil.check_in_appointment(client, waiting['id'], l_s_college_drop_in_advisor_uid)
            fake_auth.login(l_s_college_scheduler_uid)
            AppointmentTestUtil.check_in_appointment(client, waiting['id'], l_s_college_scheduler_uid, expected_status_code=400)

    def test_cancel_check_in_conflict(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            AppointmentTestUtil.cancel_appointment(client, waiting['id'], 'Cancelled by wolves')
            fake_auth.login(l_s_college_scheduler_uid)
            AppointmentTestUtil.check_in_appointment(client, waiting['id'], l_s_college_drop_in_advisor_uid, expected_status_code=400)


class TestAppointmentReserve:

    @classmethod
    def _unreserve_appointment(cls, client, appointment_id, expected_status_code=200):
        response = client.post(f'/api/appointments/{appointment_id}/unreserve')
        assert response.status_code == expected_status_code

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            AppointmentTestUtil.reserve_appointment(client, 1, l_s_college_advisor_uid, expected_status_code=401)
            self._unreserve_appointment(client, 1, expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            AppointmentTestUtil.reserve_appointment(client, 1, coe_advisor_no_advising_data_uid, expected_status_code=401)
            self._unreserve_appointment(client, 1, expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is not a drop-in advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            AppointmentTestUtil.reserve_appointment(client, 1, l_s_college_advisor_uid, expected_status_code=401)
            self._unreserve_appointment(client, 1, expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        AppointmentTestUtil.reserve_appointment(client, 1, l_s_college_drop_in_advisor_uid, expected_status_code=401)
        self._unreserve_appointment(client, 1, expected_status_code=401)

    def test_cancel_reserve_conflict(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            AppointmentTestUtil.cancel_appointment(client, waiting['id'], 'Cancelled by wolves')
            fake_auth.login(l_s_college_scheduler_uid)
            AppointmentTestUtil.reserve_appointment(client, waiting['id'], l_s_college_drop_in_advisor_uid, expected_status_code=400)

    def test_check_in_reserve_conflict(self, app, client, fake_auth):
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            AppointmentTestUtil.check_in_appointment(client, waiting['id'], l_s_college_drop_in_advisor_uid)
            fake_auth.login(l_s_college_scheduler_uid)
            AppointmentTestUtil.reserve_appointment(client, waiting['id'], l_s_college_drop_in_advisor_uid, expected_status_code=400)

    def test_unreserve_appointment_reserved_by_other(self, app, client, fake_auth):
        """Returns 401 if user un-reserves an appointment which is reserved by another."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            waiting = Appointment.query.filter(
                and_(
                    Appointment.status == 'waiting',
                    Appointment.deleted_at == None,  # noqa: E711
                ),
                Appointment.dept_code == 'QCADV',
            ).first()  # noqa: E711
            advisor = AuthorizedUser.find_by_id(waiting.created_by)
            fake_auth.login(advisor.uid)
            AppointmentTestUtil.reserve_appointment(client, waiting.id, advisor.uid)
            fake_auth.login(l_s_college_advisor_uid)
            self._unreserve_appointment(client, 1, expected_status_code=401)

    def test_reserve_appointment(self, app, client, fake_auth):
        """Drop-in advisor can reserve an appointment."""
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            advisor = DropInAdvisor.advisors_for_dept_code(dept_code)[0]
            user = AuthorizedUser.find_by_id(advisor.authorized_user_id)
            fake_auth.login(user.uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, dept_code)

            AppointmentTestUtil.reserve_appointment(client, waiting['id'], user.uid)

            # Verify
            appointment = AppointmentTestUtil.get_appointment(client, waiting['id'])
            assert appointment['status'] == 'reserved'
            assert appointment['statusDate'] is not None
            assert appointment['statusBy']['id'] == user.id
            assert appointment['advisorId'] == user.id
            assert appointment['advisorUid'] == user.uid
            assert 'QCADV' in [d['code'] for d in appointment['advisorDepartments']]
            assert appointment['advisorName'] is not None
            assert appointment['advisorRole'] == 'Advisor'
            Appointment.delete(appointment['id'])

    def test_scheduler_reserve_appointment(self, app, client, fake_auth):
        """Scheduler can reserve an appointment for a drop-in advisor."""
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            advisor = DropInAdvisor.advisors_for_dept_code(dept_code)[0]
            user = AuthorizedUser.find_by_id(advisor.authorized_user_id)
            fake_auth.login(l_s_college_scheduler_uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, dept_code)

            AppointmentTestUtil.reserve_appointment(client, waiting['id'], user.uid)

            # Verify
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            appointment = AppointmentTestUtil.get_appointment(client, waiting['id'])
            assert appointment['status'] == 'reserved'
            assert appointment['statusDate'] is not None
            assert appointment['statusBy']['uid'] == l_s_college_scheduler_uid
            assert appointment['advisorId'] == user.id
            assert appointment['advisorUid'] == user.uid
            assert 'QCADV' in [d['code'] for d in appointment['advisorDepartments']]
            assert appointment['advisorName'] is not None
            assert appointment['advisorRole'] == 'Advisor'
            Appointment.delete(appointment['id'])

    def test_steal_appointment_reservation(self, app, client, fake_auth):
        """Reserve an appointment that another advisor has reserved."""
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            user_1 = AuthorizedUser.find_by_uid(coe_drop_in_advisor_uid)
            fake_auth.login(user_1.uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, dept_code)

            AppointmentTestUtil.reserve_appointment(client, waiting['id'], user_1.uid)

            # Verify
            appointment = AppointmentTestUtil.get_appointment(client, waiting['id'])
            assert appointment['status'] == 'reserved'
            assert appointment['statusDate'] is not None
            assert appointment['statusBy']['id'] == user_1.id
            assert appointment['advisorUid'] == user_1.uid
            client.get('/api/auth/logout')

            # Another advisor comes along...
            user_2 = AuthorizedUser.find_by_uid(coe_drop_in_advisor_2_uid)
            fake_auth.login(user_2.uid)

            AppointmentTestUtil.reserve_appointment(client, waiting['id'], user_2.uid)

            # Verify
            appointment = AppointmentTestUtil.get_appointment(client, waiting['id'])
            assert appointment['status'] == 'reserved'
            assert appointment['statusDate'] is not None
            assert appointment['statusBy']['id'] == user_2.id
            assert appointment['advisorUid'] == user_2.uid

            # Clean up
            Appointment.delete(appointment['id'])

    def test_unreserve_appointment(self, app, client, fake_auth):
        """Drop-in advisor can un-reserve an appointment."""
        dept_code = 'COENG'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            user = AuthorizedUser.find_by_uid(coe_drop_in_advisor_uid)
            fake_auth.login(user.uid)
            waiting = AppointmentTestUtil.create_drop_in_appointment(client, dept_code)

            AppointmentTestUtil.reserve_appointment(client, waiting['id'], user.uid)
            # Verify
            reserved = AppointmentTestUtil.get_appointment(client, waiting['id'])
            assert reserved['status'] == 'reserved'
            assert reserved['statusDate']
            assert reserved['statusBy']['id'] == user.id
            assert reserved['statusBy']['uid'] == user.uid
            assert reserved['advisorId'] == user.id
            assert reserved['advisorUid'] == user.uid
            assert 'name' in reserved['statusBy']

            self._unreserve_appointment(client, waiting['id'])
            # Verify
            appointment = AppointmentTestUtil.get_appointment(client, waiting['id'])
            assert appointment['status'] == 'waiting'
            assert appointment['statusDate'] is not None
            assert appointment['statusBy']['id'] == user.id
            assert appointment['advisorDepartments'] is None
            assert appointment['advisorName'] is None
            assert appointment['advisorRole'] is None
            assert appointment['advisorUid'] is None
            assert appointment['advisorId'] is None
            Appointment.delete(appointment['id'])


class TestAppointmentReopen:

    @classmethod
    def _reopen_appointment(cls, client, appointment_id, expected_status_code=200):
        response = client.get(f'/api/appointments/{appointment_id}/reopen')
        assert response.status_code == expected_status_code

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            self._reopen_appointment(client, 1, expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            self._reopen_appointment(client, 1, expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is a non-dropin advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._reopen_appointment(client, 1, expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        self._reopen_appointment(client, 1, expected_status_code=401)

    def test_appointment_not_found(self, app, client, fake_auth):
        """Returns 404 if appointment is not found."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            self._reopen_appointment(client, 9999999, expected_status_code=404)

    def test_reopen_appointment(self, app, client, fake_auth):
        """Drop-in advisor can reopen an appointment."""
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            advisor = DropInAdvisor.advisors_for_dept_code(dept_code)[0]
            user = AuthorizedUser.find_by_id(advisor.authorized_user_id)
            fake_auth.login(user.uid)
            appointment = AppointmentTestUtil.create_drop_in_appointment(client, dept_code)
            AppointmentTestUtil.cancel_appointment(client, appointment['id'], 'Accidental cancel, whoopsie')

            cancelled = AppointmentTestUtil.get_appointment(client, appointment['id'])
            assert cancelled['status'] == 'cancelled'

            self._reopen_appointment(client, cancelled['id'])

            appointment = AppointmentTestUtil.get_appointment(client, appointment['id'])
            assert appointment['status'] == 'waiting'
            assert appointment['statusDate'] is not None
            assert appointment['statusBy']['id'] == user.id
            assert appointment['advisorUid'] is None
            Appointment.delete(appointment['id'])


class TestAppointmentWaitlist:

    @classmethod
    def _get_waitlist(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/appointments/waitlist/{dept_code}')
        assert response.status_code == expected_status_code
        if response.status_code == 200:
            return response.json['waitlist']

    def test_mark_read_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            self._get_waitlist(client, 'COENG', expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            self._get_waitlist(client, 'COENG', expected_status_code=401)

    def test_unrecognized_dept_code(self, app, client, fake_auth):
        """Returns 401 if requested dept_code is invalid."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(l_s_college_scheduler_uid)
            self._get_waitlist(client, 'BOGUS', expected_status_code=401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is not a drop-in advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_advisor_uid)
            self._get_waitlist(client, 'QCADV', expected_status_code=401)

    def test_not_drop_in_enabled(self, client, fake_auth):
        """Returns 401 if user's department is not configured for drop-in advising'."""
        fake_auth.login(l_s_college_drop_in_advisor_uid)
        self._get_waitlist(client, 'QCADV', expected_status_code=401)

    def test_l_and_s_advisor_cannot_view_coe_waitlist(self, app, client, fake_auth):
        """L&S advisor cannot view COE appointments (waitlist)."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG', 'QCADV']):
            fake_auth.login(l_s_college_scheduler_uid)
            self._get_waitlist(client, 'COENG', expected_status_code=403)

    def test_coe_scheduler_waitlist(self, app, client, fake_auth):
        """Waitlist is properly sorted for COE drop-in advisor."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_drop_in_advisor_uid)
            waitlist = self._get_waitlist(client, 'COENG')
            assert len(waitlist['unresolved']) == 3
            assert len(waitlist['resolved']) > 2
            for appt in waitlist['unresolved']:
                assert appt['status'] in ('reserved', 'waiting')
            for appt in waitlist['resolved']:
                assert appt['status'] in ('checked_in', 'cancelled')

    def test_waitlist_include_checked_in_and_cancelled(self, app, client, fake_auth):
        """For scheduler, the waitlist has appointments with event type 'waiting' or 'reserved'."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_scheduler_uid)
            appointments = self._get_waitlist(client, 'COENG')
            assert len(appointments['resolved']) == 0
            assert len(appointments['unresolved']) > 2
            for index, appointment in enumerate(appointments['unresolved']):
                assert appointment['status'] in ('reserved', 'waiting')

    def test_l_and_s_scheduler_waitlist(self, app, client, fake_auth):
        """L&S scheduler can only see L&S unresolved appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_scheduler_uid)
            dept_code = 'QCADV'
            appointments = self._get_waitlist(client, dept_code)
            assert len(appointments['unresolved']) >= 2
            assert len(appointments['resolved']) == 0
            for appointment in appointments['unresolved']:
                assert appointment['deptCode'] == dept_code

    def test_l_s_college_drop_in_advisor_uid_waitlist(self, app, client, fake_auth):
        """L&S drop-in advisor can only see L&S appointments."""
        dept_code = 'QCADV'
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', [dept_code]):
            fake_auth.login(l_s_college_drop_in_advisor_uid)
            appointments = self._get_waitlist(client, dept_code)
            assert len(appointments['unresolved']) >= 2
            assert len(appointments['resolved']) > 0
            for appointment in appointments['unresolved'] + appointments['resolved']:
                assert appointment['deptCode'] == dept_code


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

    def test_mark_read_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            self._mark_appointment_read(client, 1, expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['COENG']):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            self._mark_appointment_read(client, 1, expected_status_code=401)

    def test_advisor_read_appointment(self, app, client, fake_auth):
        """L&S advisor reads an appointment."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            fake_auth.login(l_s_college_scheduler_uid)
            # As scheduler, create appointment
            appointment = AppointmentTestUtil.create_drop_in_appointment(client, 'QCADV')
            appointment_id = appointment['id']
            client.get('/api/auth/logout')
            # Verify unread by advisor
            uid = l_s_college_advisor_uid
            user_id = AuthorizedUser.get_id_per_uid(uid)
            assert AppointmentRead.was_read_by(user_id, appointment_id) is False
            # Next, log in as advisor and read the appointment
            fake_auth.login(uid)
            api_json = self._mark_appointment_read(client, appointment_id)
            assert api_json['appointmentId'] == str(appointment_id)
            assert api_json['viewerId'] == user_id
            assert AppointmentRead.was_read_by(user_id, appointment_id) is True
            Appointment.delete(appointment_id)

    def test_advisor_read_legacy_appointment(self, app, client, fake_auth):
        """L&S advisor reads an imported SIS appointment."""
        with override_config(app, 'DEPARTMENTS_SUPPORTING_DROP_INS', ['QCADV']):
            appointment_id = '11667051-00010'
            user_id = AuthorizedUser.get_id_per_uid(l_s_college_advisor_uid)
            assert AppointmentRead.was_read_by(user_id, appointment_id) is False

            fake_auth.login(l_s_college_advisor_uid)
            api_json = self._mark_appointment_read(client, appointment_id)
            assert api_json['appointmentId'] == appointment_id
            assert api_json['viewerId'] == user_id
            assert AppointmentRead.was_read_by(user_id, appointment_id) is True


class TestStreamLegacyAppointmentAttachments:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/appointments/attachment/9100000000_00010_1.pdf').status_code == 401

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        with mock_legacy_appointment_attachment(app):
            fake_auth.login(coe_advisor_no_advising_data_uid)
            assert client.get('/api/appointments/attachment/9100000000_00010_1.pdf').status_code == 401

    def test_stream_attachment(self, app, client, fake_auth):
        with mock_legacy_appointment_attachment(app):
            fake_auth.login(coe_advisor_uid)
            response = client.get('/api/appointments/attachment/9100000000_00010_1.pdf')
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'application/octet-stream'
            assert response.headers['Content-Disposition'] == "attachment; filename*=UTF-8''not_a_virus.exe"
            assert response.data == b'01001000 01100101 01101100 01101100 01101111 00100000 01010111 01101111 01110010 01101100 01100100'

    def test_stream_attachment_reports_missing_files_not_found(self, app, client, fake_auth):
        with mock_legacy_appointment_attachment(app):
            fake_auth.login(l_s_college_advisor_uid)
            response = client.get('/api/appointments/attachment/h0ax.lol')
            assert response.status_code == 404
            assert response.data == b'Sorry, attachment not available.'
