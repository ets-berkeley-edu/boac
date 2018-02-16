from boac.externals import canvas
from boac.lib.mockingbird import MockResponse, register_mock
from boac.models.alert import Alert
import pytest


def get_current_alerts():
    return Alert.current_alerts_for_sid(sid='11667051', viewer_id='2040')['shown']


term_id = '2178'


@pytest.mark.usefixtures('db_session')
class TestCacheUtils:
    """Cache utils."""

    def test_assignment_alerts_created_on_cache_load(self):
        """Creates assignment alerts from fixtures on cache load."""
        from boac.api.cache_utils import load_term
        load_term(term_id)
        alerts = get_current_alerts()
        assert len(alerts) == 3
        assert alerts[0]['alertType'] == 'midterm'
        assert alerts[0]['message'] == 'BURMESE 1A midterm grade of D+.'
        assert alerts[1]['alertType'] == 'late_assignment'
        assert alerts[1]['message'] == 'MED ST 205 assignment due on Oct 5, 2017.'
        assert alerts[2]['alertType'] == 'missing_assignment'
        assert alerts[2]['message'] == 'MED ST 205 assignment due on Nov 2, 2017.'

    def test_assignment_alerts_updated_on_cache_reload(self, app, db_session):
        """Updates assignment alerts on cache reload."""
        from boac.api.cache_utils import load_term, refresh_term
        load_term(term_id)
        assert len(get_current_alerts()) == 3

        with open(app.config['BASE_DIR'] + '/fixtures/canvas_course_assignments_analytics_7654321_61889.json') as file:
            # History is rewritten, so that the late assignment turns out to have been on time...
            modified_response_body = file.read().replace('"status": "late"', '"status": "on_time"')
            # ...meanwhile, the missing assignment shows up late.
            modified_response_body = modified_response_body.replace('"status": "missing"', '"status": "late"')

            def modified_assignment_analytics_fixture(course_id, uid, **kwargs):
                if str(course_id) == '7654321' and str(uid) == '61889':
                    return MockResponse(200, {}, modified_response_body)
                else:
                    return MockResponse(404, {}, '')
            with register_mock(canvas._get_assignments_analytics, modified_assignment_analytics_fixture):
                refresh_term(term_id)

                db_alerts = db_session.query(Alert).order_by(Alert.created_at).all()
                assert len(db_alerts) == 4
                assert db_alerts[0].alert_type == 'midterm'
                assert db_alerts[0].key == '2178_90100'
                assert db_alerts[0].active is True
                assert db_alerts[1].alert_type == 'late_assignment'
                assert db_alerts[1].key == '2178_331896'
                assert db_alerts[1].active is False
                assert db_alerts[2].alert_type == 'missing_assignment'
                assert db_alerts[2].key == '2178_331897'
                assert db_alerts[2].active is False
                assert db_alerts[3].alert_type == 'late_assignment'
                assert db_alerts[3].key == '2178_331897'
                assert db_alerts[3].active is True

                api_alerts = get_current_alerts()
                assert len(api_alerts) == 2
                assert api_alerts[0]['alertType'] == 'midterm'
                assert api_alerts[1]['alertType'] == 'late_assignment'
                assert api_alerts[1]['message'] == 'MED ST 205 assignment due on Nov 2, 2017.'
