from boac.models.alert import Alert

advisor_1_uid = '2040'
advisor_2_uid = '1133399'


class TestAlertsController:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/alerts/current/11667051').status_code == 401

    def test_current_alerts_for_sid(self, create_alerts, fake_auth, client):
        """Returns current_user's current alerts for a given sid."""
        fake_auth.login(advisor_1_uid)
        response = client.get('/api/alerts/current/11667051')
        assert response.status_code == 200
        assert len(response.json['shown']) == 2
        assert len(response.json['dismissed']) == 0
        assert response.json['shown'][0]['alertType'] == 'late_assignment'
        assert response.json['shown'][0]['key'] == '2178_800900300'
        assert response.json['shown'][0]['message'] == 'Week 5 homework in RUSSIAN 13 is late.'
        assert response.json['shown'][1]['alertType'] == 'missing_assignment'
        assert response.json['shown'][1]['key'] == '2178_500600700'
        assert response.json['shown'][1]['message'] == 'Week 6 homework in PORTUGUESE 12 is missing.'

    def test_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Can dismiss alerts for one user without affecting visibility for other users."""
        fake_auth.login(advisor_1_uid)
        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_brigitte_alerts['shown']) == 2
        assert len(advisor_1_brigitte_alerts['dismissed']) == 0
        alert_id = advisor_1_brigitte_alerts['shown'][0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        assert response.json['message'] == 'Alert ' + str(alert_id) + ' dismissed by UID 2040'

        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_brigitte_alerts['shown']) == 1
        assert len(advisor_1_brigitte_alerts['dismissed']) == 1

        fake_auth.login(advisor_2_uid)
        advisor_2_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_2_brigitte_alerts['shown']) == 2
        assert len(advisor_2_brigitte_alerts['dismissed']) == 0

    def test_duplicate_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Shrugs off duplicate dismissals."""
        fake_auth.login(advisor_1_uid)
        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        alert_id = advisor_1_brigitte_alerts['shown'][0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200

    def test_dismiss_nonexistent_alerts(self, create_alerts, fake_auth, client):
        """Politely handles nonexistent alert dismissals."""
        fake_auth.login(advisor_1_uid)
        response = client.get('/api/alerts/99999999/dismiss')
        assert response.status_code == 400
        assert response.json['message'] == 'No alert found for id 99999999'

    def test_deactivate_alerts(self, create_alerts, fake_auth, client):
        """Can programmatically deactivate alerts, removing them for all users."""
        Alert.query.filter_by(key='2178_800900300').first().deactivate()

        fake_auth.login(advisor_1_uid)
        advisor_1_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_brigitte_alerts['shown']) == 1
        assert advisor_1_brigitte_alerts['shown'][0]['key'] == '2178_500600700'
        assert len(advisor_1_brigitte_alerts['dismissed']) == 0

        fake_auth.login(advisor_2_uid)
        advisor_2_brigitte_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_2_brigitte_alerts['shown']) == 1
        assert advisor_2_brigitte_alerts['shown'][0]['key'] == '2178_500600700'
        assert len(advisor_2_brigitte_alerts['dismissed']) == 0
