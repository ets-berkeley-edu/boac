from boac.models.alert import Alert
import pytest

advisor_1_uid = '2040'
advisor_2_uid = '1133399'


@pytest.fixture()
def authenticated_session_1(fake_auth):
    fake_auth.login(advisor_1_uid)


@pytest.fixture()
def authenticated_session_2(fake_auth):
    fake_auth.login(advisor_2_uid)


@pytest.fixture()
def create_alerts(db_session):
    alert_1 = Alert.create(
        sid='11667051',
        alert_type='late_assignment',
        key='800900300',
        message='Week 5 homework in RUSSIAN 13 is late.',
    )
    alert_2 = Alert.create(
        sid='11667051',
        alert_type='missing_assignment',
        key='500600700',
        message='Week 6 homework in PORTUGUESE 12 is missing.',
    )
    alert_3 = Alert.create(
        sid='2345678901',
        alert_type='late_assignment',
        key='100200300',
        message='Week 5 homework in BOSCRSR 27B is late.',
    )

    alert_1.add_viewer(advisor_1_uid)
    alert_2.add_viewer(advisor_1_uid)
    alert_3.add_viewer(advisor_1_uid)

    alert_1.add_viewer(advisor_2_uid)
    alert_2.add_viewer(advisor_2_uid)


class TestAlertsController:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/alerts/current').status_code == 401

    def test_current_alerts(self, create_alerts, fake_auth, client):
        """Returns current_user's current alert counts, grouped by sid."""
        fake_auth.login(advisor_1_uid)
        response = client.get('/api/alerts/current')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['sid'] == '2345678901'
        assert response.json[0]['uid'] == '2040'
        assert response.json[0]['first_name'] == 'Oliver'
        assert response.json[0]['last_name'] == 'Heyer'
        assert response.json[0]['alert_count'] == 1
        assert response.json[1]['sid'] == '11667051'
        assert response.json[1]['uid'] == '61889'
        assert response.json[1]['first_name'] == 'Brigitte'
        assert response.json[1]['last_name'] == 'Lin'
        assert response.json[1]['alert_count'] == 2

        fake_auth.login(advisor_2_uid)
        response = client.get('/api/alerts/current')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['sid'] == '11667051'
        assert response.json[0]['uid'] == '61889'
        assert response.json[0]['first_name'] == 'Brigitte'
        assert response.json[0]['last_name'] == 'Lin'
        assert response.json[0]['alert_count'] == 2

    def test_current_alerts_for_sid(self, create_alerts, fake_auth, client):
        """Returns current_user's current alerts for a given sid."""
        fake_auth.login(advisor_1_uid)
        response = client.get('/api/alerts/current/11667051')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['alertType'] == 'late_assignment'
        assert response.json[0]['key'] == '800900300'
        assert response.json[0]['message'] == 'Week 5 homework in RUSSIAN 13 is late.'
        assert response.json[1]['alertType'] == 'missing_assignment'
        assert response.json[1]['key'] == '500600700'
        assert response.json[1]['message'] == 'Week 6 homework in PORTUGUESE 12 is missing.'

    def test_current_alerts_empty(self, create_alerts, fake_auth, client):
        """Returns empty when no active alerts found."""
        fake_auth.login(advisor_1_uid)
        response = client.get('/api/alerts/current/9999999')
        assert response.status_code == 200
        assert response.json == []

    def test_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Can dismiss alerts for one user without affecting visibility for other users."""
        fake_auth.login(advisor_1_uid)
        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_brigitte_alerts) == 2
        alert_id = advisor_1_brigitte_alerts[0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        assert response.json['message'] == 'Alert ' + str(alert_id) + ' dismissed by UID 2040'

        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_brigitte_alerts) == 1
        advisor_1_current_alerts = client.get('/api/alerts/current').json
        assert advisor_1_current_alerts[1]['sid'] == '11667051'
        assert advisor_1_current_alerts[1]['alert_count'] == 1

        fake_auth.login(advisor_2_uid)
        advisor_2_current_alerts = client.get('/api/alerts/current').json
        assert advisor_2_current_alerts[0]['sid'] == '11667051'
        assert advisor_2_current_alerts[0]['alert_count'] == 2
        advisor_2_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_2_brigitte_alerts) == 2

    def test_duplicate_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Politely handles duplicate dismissal."""
        fake_auth.login(advisor_1_uid)
        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        alert_id = advisor_1_brigitte_alerts[0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 400
        assert response.json['message'] == 'No current alert view found for alert ' + str(alert_id) + ' and UID 2040'

    def test_deactivate_alerts(self, create_alerts, fake_auth, client):
        """Can programmatically deactivate alerts, removing them for all users."""
        Alert.query.filter_by(key='800900300').first().deactivate()

        fake_auth.login(advisor_1_uid)
        advisor_1_current_alerts = client.get('/api/alerts/current').json
        assert advisor_1_current_alerts[1]['sid'] == '11667051'
        assert advisor_1_current_alerts[1]['alert_count'] == 1
        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_brigitte_alerts) == 1
        assert advisor_1_brigitte_alerts[0]['key'] == '500600700'

        fake_auth.login(advisor_2_uid)
        advisor_2_current_alerts = client.get('/api/alerts/current').json
        assert advisor_2_current_alerts[0]['sid'] == '11667051'
        assert advisor_2_current_alerts[0]['alert_count'] == 1
        advisor_2_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_2_brigitte_alerts) == 1
        assert advisor_2_brigitte_alerts[0]['key'] == '500600700'
