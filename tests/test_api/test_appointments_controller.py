"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.appointment_read import AppointmentRead
from boac.models.authorized_user import AuthorizedUser
import pytest
import simplejson as json
from tests.util import mock_legacy_appointment_attachment


coe_advisor_uid = '211159'
coe_advisor_no_advising_data_uid = '1022796'
l_s_college_advisor_uid = '188242'
l_s_advisor_no_advising_data_uid = '19735'
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
        self._mark_appointment_read(client, '11667051-00010', expected_status_code=401)

    def test_user_without_advising_data_access(self, app, client, fake_auth):
        """Denies access to a user who cannot access notes and appointments."""
        fake_auth.login(coe_advisor_no_advising_data_uid)
        self._mark_appointment_read(client, '11667051-00010', expected_status_code=401)
        fake_auth.login(l_s_advisor_no_advising_data_uid)
        self._mark_appointment_read(client, '11667051-00010', expected_status_code=401)

    def test_advisor_read_legacy_appointment(self, app, client, fake_auth):
        """L&S advisor reads an imported SIS appointment."""
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
