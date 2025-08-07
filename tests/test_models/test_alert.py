"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from time import sleep

import pytest
from dateutil import parser

from boac.models.alert import Alert
from tests.util import override_config


def get_current_alerts(sid):
    alerts = Alert.current_alerts_for_sid(sid=sid, viewer_id='2040')
    return list(filter(lambda a: not a['dismissed'], alerts))


alert_props = {
    'sid': '11667051',
    'term_id': '2178',
    'assignment_id': '987654321',
    'due_at': '2017-10-31T12:00:00Z',
    'status': 'missing',
    'course_site_name': 'MED ST 205',
}


@pytest.mark.usefixtures('db_session')
class TestAlert:
    """Student status alerts."""

    def test_activation_deactivation_all_students(self):
        """Can activate and deactive across entire population for term."""
        assert len(get_current_alerts('11667051')) == 0
        assert len(get_current_alerts('3456789012')) == 0
        Alert.update_all_for_term(2178)
        assert len(get_current_alerts('11667051')) == 2
        assert len(get_current_alerts('3456789012')) == 1
        Alert.deactivate_all_for_term(2178)
        assert len(get_current_alerts('11667051')) == 0
        assert len(get_current_alerts('3456789012')) == 0

    def test_assignment_alerts_change_updated_at_timestamp(self):
        def _parse(date_string):
            return parser.parse(date_string).replace(microsecond=0)

        Alert.update_all_for_term(2178)
        alerts = Alert.current_alerts_for_sid(sid='3456789012', viewer_id='2040')
        assert _parse(alerts[0]['updatedAt']) == _parse(alerts[0]['createdAt'])
        sleep(1.0)
        Alert.deactivate_all_for_term(2178)
        Alert.update_all_for_term(2178)
        alerts = Alert.current_alerts_for_sid(sid='3456789012', viewer_id='2040')
        assert _parse(alerts[0]['updatedAt']) > _parse(alerts[0]['createdAt'])

    def test_midpoint_deficient_grade_alerts_preserve_updated_at_timestamp(self):
        def _parse(date_string):
            return parser.parse(date_string).replace(microsecond=0)

        Alert.update_all_for_term(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')
        alert = next((a for a in alerts if a['alertType'] == 'midterm'), None)
        assert _parse(alert['updatedAt']) == _parse(alert['createdAt'])
        sleep(0.5)
        Alert.deactivate_all_for_term(2178)
        Alert.update_all_for_term(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')
        alert = next((a for a in alerts if a['alertType'] == 'midterm'), None)
        assert _parse(alert['updatedAt']) == _parse(alert['createdAt'])

    def test_inactive_alert_preserves_timestamp(self):
        # The 'updated_at' attribute of an inactive alert preserves the time at which it was deactivated.
        Alert.update_all_for_term(2178)
        Alert.deactivate_all(sid='11667051', term_id='2178', alert_types=['midterm'])
        inactive_alert_1 = (Alert.query.
                            filter(Alert.sid == '11667051').
                            filter(Alert.key.startswith('2178_')).
                            filter(Alert.deleted_at != None).  # noqa: E711
                            first()
                            )
        inactivation_timestamp = inactive_alert_1.updated_at
        sleep(0.5)
        Alert.deactivate_all_for_term(2178)
        inactive_alert_1 = Alert.query.filter_by(id=inactive_alert_1.id).first()
        inactive_alert_2 = (Alert.query.
                            filter(Alert.sid == '3456789012').
                            filter(Alert.key.startswith('2178_%')).
                            filter(Alert.deleted_at != None).  # noqa: E711
                            first()
                            )
        assert inactive_alert_1.updated_at == inactivation_timestamp
        assert inactive_alert_2.updated_at > inactivation_timestamp

    def test_academic_standing_action_date_as_created_at(self):
        actual_action_date = '2017-12-30'
        Alert.update_all_for_term(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')
        alert = next((a for a in alerts if a['alertType'] == 'academic_standing'), None)
        created_at = alert['createdAt']
        assert created_at.startswith(actual_action_date)
        assert alert['updatedAt'] == created_at

        sleep(1.0)
        Alert.deactivate_all_for_term(2178)
        Alert.update_all_for_term(2178)
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')
        academic_standing_alert = next((a for a in alerts if a['alertType'] == 'academic_standing'), None)
        created_at = academic_standing_alert['createdAt']
        assert created_at.startswith(actual_action_date)
        assert academic_standing_alert['updatedAt'] == created_at


class TestNoActivityAlert:
    """Alerts for no bCourses activity."""

    def test_update_no_activity_alerts(self):
        """Can be created from bCourses analytics feeds, at most one per enrollment."""
        Alert.update_all_for_term(2178)
        alerts = get_current_alerts('3456789012')
        assert len(alerts) == 1
        assert alerts[0]['id'] > 0
        assert alerts[0]['alertType'] == 'no_activity'
        assert alerts[0]['key'] == '2178_MED ST 205'
        assert alerts[0]['message'] == 'No activity! Student has never visited the MED ST 205 bCourses site for Fall 2017.'

    def test_no_activity_percentile_cutoff(self, app):
        """Respect percentile cutoff for alert creation."""
        with override_config(app, 'ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF', 10):
            Alert.update_all_for_term(2178)
            assert len(get_current_alerts('3456789012')) == 0
        with override_config(app, 'ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF', 20):
            Alert.update_all_for_term(2178)
            assert len(get_current_alerts('3456789012')) == 1


class TestInfrequentActivityAlert:
    """Alerts for infrequent bCourses activity."""

    def test_update_infrequent_activity_alerts(self, app):
        """Can be created from bCourses analytics feeds, at most one per enrollment."""
        with override_config(app, 'ALERT_INFREQUENT_ACTIVITY_ENABLED', True):
            Alert.update_all_for_term(2178)
            alerts = get_current_alerts('5678901234')
            assert len(alerts) == 1
            assert alerts[0]['id'] > 0
            assert alerts[0]['alertType'] == 'infrequent_activity'
            assert alerts[0]['key'] == '2178_MED ST 205'
            assert alerts[0]['message'].startswith('Infrequent activity! Last MED ST 205 bCourses activity')

    def test_infrequent_activity_percentile_cutoff(self, app):
        """Respect percentile cutoff for alert creation."""
        with override_config(app, 'ALERT_INFREQUENT_ACTIVITY_ENABLED', True):
            with override_config(app, 'ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF', 10):
                Alert.update_all_for_term(2178)
                assert len(get_current_alerts('5678901234')) == 0
            with override_config(app, 'ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF', 20):
                Alert.update_all_for_term(2178)
                assert len(get_current_alerts('5678901234')) == 1


class TestWithdrawalAlert:
    """Alerts for withdrawal/cancellation status."""

    def test_update_withdrawal_alerts(self, app):
        """Can be created from SIS feeds."""
        with override_config(app, 'ALERT_WITHDRAWAL_ENABLED', True):
            Alert.update_all_for_term(2178)
            alerts = get_current_alerts('2345678901')
            assert len(alerts) == 1
            assert alerts[0]['key'] == '2178_withdrawal'
            assert alerts[0]['message'] == 'Student is no longer enrolled in the Fall 2017 term.'
