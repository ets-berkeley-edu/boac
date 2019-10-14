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

import simplejson as json

coe_advisor_uid = '90412'
coe_scheduler_uid = '6972201'
l_s_major_advisor_uid = '242881'


class TestCreateAppointment:

    @classmethod
    def _create_appointment(cls, client, json_data=(), expected_status_code=200):
        response = client.post(
            '/api/appointments/create',
            data=json.dumps(json_data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _get_waitlist(cls, client):
        response = client.get('/api/appointments/waitlist')
        assert response.status_code == 200
        return response.json

    def test_create_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._create_appointment(client, expected_status_code=401)

    def test_create_appointment_as_scheduler(self, client, fake_auth):
        """Scheduler can create appointments."""
        fake_auth.login(coe_scheduler_uid)
        details = 'Aloysius has some questions.'
        data = {
            'advisorDeptCodes': ['COENG'],
            'advisorName': 'Mr. Snuffleupagus',
            'advisorRole': 'Advisor',
            'advisorUid': coe_advisor_uid,
            'details': details,
            'sid': '3456789012',
            'topics': ['Appointment Topic 1', 'Appointment Topic 3'],
        }
        appointment = self._create_appointment(client, data)
        waitlist = self._get_waitlist(client)
        matching = next((a for a in waitlist if a['details'] == details), None)
        assert appointment['id'] == matching['id']
        assert len(appointment['topics']) == 2


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
        fake_auth.login(l_s_major_advisor_uid)
        self._create_appointment(client, 1, expected_status_code=401)


class TestAppointmentWaitlist:

    @classmethod
    def _get_waitlist(cls, client, expected_status_code=200):
        response = client.get('/api/appointments/waitlist')
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._get_waitlist(client, 401)

    def test_deny_advisor(self, app, client, fake_auth):
        """Returns 401 if user is an advisor without drop_in responsibilities."""
        fake_auth.login(l_s_major_advisor_uid)
        self._get_waitlist(client, 401)

    def test_scheduler_viewing_waitlist(self, app, client, fake_auth):
        """COE scheduler can see COE waitlist."""
        fake_auth.login(coe_scheduler_uid)
        appointments = self._get_waitlist(client)
        assert len(appointments) == 2
        appointment = appointments[0]
        assert appointment['id'] > 0
        assert appointment['advisorName'] == 'Johnny C. Lately'
        assert appointment['advisorUid'] == coe_advisor_uid
        assert appointment['advisorDeptCodes'] == ['COENG']
        assert appointment['createdAt'] is not None
        assert appointment['createdBy'] == coe_scheduler_uid
        assert 'crossroads' in appointment['details']
        assert appointment['studentSid'] == '3456789012'
        assert len(appointment['topics']) == 1

    def test_advisor_viewing_waitlist(self, app, client, fake_auth):
        """COE advisor can see COE waitlist."""
        fake_auth.login(coe_advisor_uid)
        appointments = self._get_waitlist(client)
        assert len(appointments) == 2
        assert appointments[0]['advisorUid'] == coe_advisor_uid
        assert appointments[0]['createdBy'] == coe_scheduler_uid
        assert appointments[1]['advisorUid'] == coe_advisor_uid
        assert appointments[1]['createdBy'] == coe_advisor_uid


class TestMarkAppointmentRead:

    @classmethod
    def _mark_appointment_read(cls, client, appointment_id, expected_status_code=200):
        response = client.post(
            f'/api/appointments/{appointment_id}/check_in',
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._mark_appointment_read(client, 1, expected_status_code=401)


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
        fake_auth.login(l_s_major_advisor_uid)
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
