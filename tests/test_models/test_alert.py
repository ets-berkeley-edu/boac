from boac.models.alert import Alert
import pytest


def get_current_alerts():
    return Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')['shown']


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

    def test_update_assignment_alerts(self):
        """Can be created from assignment data."""
        assert len(get_current_alerts()) == 0
        Alert.update_assignment_alerts(**alert_props)
        alerts = get_current_alerts()
        assert len(alerts) == 1
        assert alerts[0]['id'] > 0
        assert alerts[0]['alertType'] == 'missing_assignment'
        assert alerts[0]['key'] == '2178_987654321'
        assert alerts[0]['message'] == 'MED ST 205 assignment due on Oct 31, 2017.'

    def test_no_duplicate_alerts(self):
        """If an alert exists with the same key, updates the message rather than creating a duplicate."""
        assert len(get_current_alerts()) == 0
        Alert.update_assignment_alerts(**alert_props)
        updated_alert_props = dict(alert_props, due_at='2017-12-25T12:00:00Z')
        Alert.update_assignment_alerts(**updated_alert_props)
        alerts = get_current_alerts()
        assert len(alerts) == 1
        assert alerts[0]['key'] == '2178_987654321'
        assert alerts[0]['message'] == 'MED ST 205 assignment due on Dec 25, 2017.'

    def test_deactivate_reactivate_alerts(self):
        """Can be deactivated and reactivated, preserving id."""
        assert len(get_current_alerts()) == 0
        Alert.update_assignment_alerts(**alert_props)
        alerts = get_current_alerts()
        assert len(alerts) == 1
        alert_id = alerts[0]['id']

        Alert.deactivate_all(sid='11667051', term_id='2178', alert_types=['missing_assignment'])
        assert len(get_current_alerts()) == 0

        Alert.update_assignment_alerts(**alert_props)
        alerts = get_current_alerts()
        assert len(alerts) == 1
        assert alerts[0]['id'] == alert_id

    def test_alert_timezones(self):
        """For purposes of displaying due dates, loves LA."""
        Alert.update_assignment_alerts(**dict(alert_props, due_at='2017-02-03T07:59:01Z'))
        assert get_current_alerts()[0]['message'] == 'MED ST 205 assignment due on Feb 2, 2017.'
        Alert.update_assignment_alerts(**dict(alert_props, due_at='2017-02-03T08:00:01Z'))
        assert get_current_alerts()[0]['message'] == 'MED ST 205 assignment due on Feb 3, 2017.'
        Alert.update_assignment_alerts(**dict(alert_props, due_at='2017-06-17T06:59:59Z'))
        assert get_current_alerts()[0]['message'] == 'MED ST 205 assignment due on Jun 16, 2017.'
        Alert.update_assignment_alerts(**dict(alert_props, due_at='2017-06-17T07:00:01Z'))
        assert get_current_alerts()[0]['message'] == 'MED ST 205 assignment due on Jun 17, 2017.'
