from boac.merged.sis_enrollments import merge_sis_enrollments_for_term
from boac.models.alert import Alert
import pytest


@pytest.mark.usefixtures('db_session')
class TestMergedSisEnrollments:

    def test_creates_alert_for_midterm_grade(self, app):
        feed = merge_sis_enrollments_for_term([], '11667051', app.config['CANVAS_CURRENT_ENROLLMENT_TERM'])
        assert '2178' == feed['termId']
        enrollments = feed['enrollments']
        assert 3 == len(enrollments)
        assert 'D+' == enrollments[0]['midtermGrade']
        assert 'BURMESE 1A' == enrollments[0]['displayName']
        assert 90100 == enrollments[0]['sections'][0]['ccn']
        alerts = Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')['shown']
        assert 1 == len(alerts)
        assert 0 < alerts[0]['id']
        assert 'midterm' == alerts[0]['alertType']
        assert '2178_90100' == alerts[0]['key']
        assert 'BURMESE 1A midterm grade of D+.' == alerts[0]['message']
