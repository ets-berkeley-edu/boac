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

from datetime import date

from boac.models.appointment_availability import AppointmentAvailability
from boac.models.authorized_user import AuthorizedUser
import pytest


@pytest.fixture()
def advisor_1_id():
    return AuthorizedUser.get_id_per_uid('53791')


@pytest.fixture()
def advisor_2_id():
    return AuthorizedUser.get_id_per_uid('188242')


@pytest.mark.usefixtures('db_session')
class TestAppointmentAvailability:

    def test_recurring_availability_slots(self, advisor_1_id):
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '15:00', '16:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Wed')

        advisor_schedule = AppointmentAvailability.availability_for_advisor(advisor_1_id, 'QCADV')
        assert len(list(advisor_schedule.keys())) == 2
        assert list(advisor_schedule['Mon'].keys()) == ['recurring']
        assert len(advisor_schedule['Mon']['recurring']) == 2
        assert advisor_schedule['Mon']['recurring'][0]['id']
        assert advisor_schedule['Mon']['recurring'][0]['startTime'] == '10:00:00'
        assert advisor_schedule['Mon']['recurring'][0]['endTime'] == '12:00:00'
        assert advisor_schedule['Mon']['recurring'][1]['id']
        assert advisor_schedule['Mon']['recurring'][1]['startTime'] == '15:00:00'
        assert advisor_schedule['Mon']['recurring'][1]['endTime'] == '16:00:00'
        assert list(advisor_schedule['Wed'].keys()) == ['recurring']
        assert len(advisor_schedule['Wed']['recurring']) == 1
        assert advisor_schedule['Wed']['recurring'][0]['id']
        assert advisor_schedule['Wed']['recurring'][0]['startTime'] == '10:00:00'
        assert advisor_schedule['Wed']['recurring'][0]['endTime'] == '12:00:00'

        monday_schedule = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 23))
        assert list(monday_schedule.keys()) == ['53791']
        assert monday_schedule['53791'] == advisor_schedule['Mon']['recurring']

        wednesday_schedule = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 25))
        assert list(wednesday_schedule.keys()) == ['53791']
        assert wednesday_schedule['53791'] == advisor_schedule['Wed']['recurring']

        friday_schedule = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 27))
        assert friday_schedule == {}

    def test_single_date_override(self, advisor_1_id):
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Fri')

        AppointmentAvailability.create(advisor_1_id, 'QCADV', '09:00', '11:00', 'Mon', '2020-03-23')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '15:00', '17:00', 'Mon', '2020-03-23')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Wed', '2020-03-25')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', None, None, 'Fri', '2020-03-27')

        advisor_schedule = AppointmentAvailability.availability_for_advisor(advisor_1_id, 'QCADV')
        assert list(advisor_schedule['Mon'].keys()) == ['recurring', '2020-03-23']
        assert len(advisor_schedule['Mon']['recurring']) == 1
        assert advisor_schedule['Mon']['recurring'][0]['id']
        assert advisor_schedule['Mon']['recurring'][0]['startTime'] == '10:00:00'
        assert advisor_schedule['Mon']['recurring'][0]['endTime'] == '12:00:00'
        assert len(advisor_schedule['Mon']['2020-03-23']) == 2
        assert advisor_schedule['Mon']['2020-03-23'][0]['id']
        assert advisor_schedule['Mon']['2020-03-23'][0]['startTime'] == '09:00:00'
        assert advisor_schedule['Mon']['2020-03-23'][0]['endTime'] == '11:00:00'
        assert advisor_schedule['Mon']['2020-03-23'][1]['id']
        assert advisor_schedule['Mon']['2020-03-23'][1]['startTime'] == '15:00:00'
        assert advisor_schedule['Mon']['2020-03-23'][1]['endTime'] == '17:00:00'
        assert list(advisor_schedule['Wed'].keys()) == ['2020-03-25']
        assert len(advisor_schedule['Wed']['2020-03-25']) == 1
        assert advisor_schedule['Wed']['2020-03-25'][0]['id']
        assert advisor_schedule['Wed']['2020-03-25'][0]['startTime'] == '10:00:00'
        assert advisor_schedule['Wed']['2020-03-25'][0]['endTime'] == '12:00:00'
        assert list(advisor_schedule['Fri'].keys()) == ['recurring', '2020-03-27']
        assert len(advisor_schedule['Fri']['recurring']) == 1
        assert advisor_schedule['Fri']['recurring'][0]['id']
        assert advisor_schedule['Fri']['recurring'][0]['startTime'] == '10:00:00'
        assert advisor_schedule['Fri']['recurring'][0]['endTime'] == '12:00:00'
        assert len(advisor_schedule['Fri']['2020-03-27']) == 1
        assert advisor_schedule['Fri']['2020-03-27'][0]['id']
        assert advisor_schedule['Fri']['2020-03-27'][0]['startTime'] is None
        assert advisor_schedule['Fri']['2020-03-27'][0]['endTime'] is None

        assert AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 23))['53791'] == \
            advisor_schedule['Mon']['2020-03-23']

        assert AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 25))['53791'] == \
            advisor_schedule['Wed']['2020-03-25']

        assert AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 27)) == {}

        assert AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 30))['53791'] == \
            advisor_schedule['Mon']['recurring']

        assert AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 4, 1)) == {}

        assert AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 4, 3))['53791'] == \
            advisor_schedule['Fri']['recurring']

    def test_per_department_schedule(self, advisor_1_id, advisor_2_id):
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADVMAJ', '10:00', '12:00', 'Tue')
        AppointmentAvailability.create(advisor_2_id, 'QCADV', '1:00', '3:00', 'Mon')
        AppointmentAvailability.create(advisor_2_id, 'QCADV', '10:00', '12:00', 'Thu')

        monday_schedule = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 23))
        assert list(monday_schedule.keys()) == ['188242', '53791']

        tuesday_schedule = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 24))
        assert tuesday_schedule == {}

        thursday_schedule = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 26))
        assert list(thursday_schedule.keys()) == ['188242']

    def test_update_delete_slot(self, advisor_1_id):
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '15:00', '17:00', 'Mon', '2020-03-23')

        monday_slot = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 23))['53791'][0]
        assert monday_slot['startTime'] == '15:00:00'
        assert monday_slot['endTime'] == '17:00:00'

        AppointmentAvailability.update(monday_slot['id'], '09:00', '10:00')
        monday_slot = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 23))['53791'][0]
        assert monday_slot['startTime'] == '09:00:00'
        assert monday_slot['endTime'] == '10:00:00'

        AppointmentAvailability.delete(monday_slot['id'])
        monday_slot = AppointmentAvailability.daily_availability_for_department('QCADV', date(2020, 3, 23))['53791'][0]
        assert monday_slot['startTime'] == '10:00:00'
        assert monday_slot['endTime'] == '12:00:00'

    def test_validation_missing_start_or_end_times(self, advisor_1_id):
        with pytest.raises(ValueError, match='End time cannot be null'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', None, 'Mon')
        with pytest.raises(ValueError, match='Start time cannot be null'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', None, '12:00', 'Mon')

    def test_validation_missing_times_without_date_override(self, advisor_1_id):
        with pytest.raises(ValueError, match='Start time cannot be null'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', None, None, 'Mon')

    def test_validation_invalid_time(self, advisor_1_id):
        with pytest.raises(ValueError, match='Could not parse start time'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', 'sub_specie_aeternitatis', '10:00', 'Mon')
        with pytest.raises(ValueError, match='Could not parse end time'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', '09:00', '25:00', 'Mon')
        with pytest.raises(ValueError, match='Start time must be before end time'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', '09:00', '08:00', 'Mon')
        with pytest.raises(ValueError, match='Start time must be before end time'):
            AppointmentAvailability.create(advisor_1_id, 'QCADV', '09:00', '09:00', 'Mon')

    def test_overlapping_slots(self, advisor_1_id):
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '09:00', '10:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '11:00', 'Mon')
        monday_schedule = AppointmentAvailability.availability_for_advisor(advisor_1_id, 'QCADV')['Mon']['recurring']
        assert len(monday_schedule) == 1
        assert monday_schedule[0]['startTime'] == '09:00:00'
        assert monday_schedule[0]['endTime'] == '11:00:00'

        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '12:00', 'Mon')
        AppointmentAvailability.create(advisor_1_id, 'QCADV', '13:00', '14:00', 'Mon')
        monday_schedule = AppointmentAvailability.availability_for_advisor(advisor_1_id, 'QCADV')['Mon']['recurring']
        assert len(monday_schedule) == 2
        assert monday_schedule[0]['startTime'] == '09:00:00'
        assert monday_schedule[0]['endTime'] == '12:00:00'
        assert monday_schedule[1]['startTime'] == '13:00:00'
        assert monday_schedule[1]['endTime'] == '14:00:00'

        AppointmentAvailability.create(advisor_1_id, 'QCADV', '12:00', '13:00', 'Mon')
        monday_schedule = AppointmentAvailability.availability_for_advisor(advisor_1_id, 'QCADV')['Mon']['recurring']
        assert len(monday_schedule) == 1
        assert monday_schedule[0]['startTime'] == '09:00:00'
        assert monday_schedule[0]['endTime'] == '14:00:00'

        AppointmentAvailability.create(advisor_1_id, 'QCADV', '10:00', '11:00', 'Mon')
        monday_schedule = AppointmentAvailability.availability_for_advisor(advisor_1_id, 'QCADV')['Mon']['recurring']
        assert len(monday_schedule) == 1
        assert monday_schedule[0]['startTime'] == '09:00:00'
        assert monday_schedule[0]['endTime'] == '14:00:00'
