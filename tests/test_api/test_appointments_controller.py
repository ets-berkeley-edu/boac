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

coe_scheduler_uid = '6972201'


class TestGetAppointment:

    @classmethod
    def _api_appointment_by_id(cls, client, appointment_id, expected_status_code=200):
        response = client.get(f'/api/appointments/{appointment_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, app, client):
        """Returns 401 if not authenticated."""
        self._api_appointment_by_id(client=client, appointment_id=1, expected_status_code=401)

    def test_deny_scheduler(self, app, client, fake_auth):
        """Returns 401 if user is a scheduler."""
        fake_auth.login(coe_scheduler_uid)
        self._api_appointment_by_id(client=client, appointment_id=1, expected_status_code=401)


class TestMarkAppointmentRead:

    def test_mark_read_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/appointments/1/mark_read').status_code == 401

    def test_deny_scheduler(self, app, client, fake_auth):
        """Returns 401 if user is a scheduler."""
        fake_auth.login(coe_scheduler_uid)
        assert client.get('/api/appointments/1/mark_read').status_code == 401
