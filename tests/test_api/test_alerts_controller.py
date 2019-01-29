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

from boac.models.alert import Alert

admin_uid = '2040'
coe_advisor = '1133399'


class TestAlertsController:

    @classmethod
    def _get_dismissed(cls, alerts):
        return list(filter(lambda a: a['dismissed'], alerts))

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/alerts/current/11667051').status_code == 401

    def test_current_alerts_for_sid(self, create_alerts, fake_auth, client):
        """Returns current_user's current alerts for a given sid."""
        fake_auth.login(admin_uid)
        response = client.get('/api/alerts/current/11667051')
        assert response.status_code == 200
        alerts = response.json
        assert len(alerts) == 3
        assert alerts[0]['alertType'] == 'late_assignment'
        assert alerts[0]['key'] == '2178_800900300'
        assert alerts[0]['message'] == 'Week 5 homework in RUSSIAN 13 is late.'
        assert not alerts[0]['dismissed']
        assert alerts[1]['alertType'] == 'missing_assignment'
        assert alerts[1]['key'] == '2178_500600700'
        assert alerts[1]['message'] == 'Week 6 homework in PORTUGUESE 12 is missing.'
        assert not alerts[1]['dismissed']
        assert alerts[2]['alertType'] == 'midterm'
        assert alerts[2]['key'] == '2178_90100'
        assert alerts[2]['message'] == 'BURMESE 1A midterm grade of D+.'
        assert not alerts[2]['dismissed']

    def test_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Can dismiss alerts for one user without affecting visibility for other users."""
        fake_auth.login(admin_uid)
        advisor_1_deborah_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_deborah_alerts) == 3
        for alert in advisor_1_deborah_alerts:
            assert not alert['dismissed']
        alert_id = advisor_1_deborah_alerts[0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        assert response.json['message'] == 'Alert ' + str(alert_id) + ' dismissed by UID 2040'

        advisor_1_deborah_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_deborah_alerts) == 3
        assert len(self._get_dismissed(advisor_1_deborah_alerts)) == 1

        fake_auth.login(coe_advisor)
        advisor_2_deborah_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_2_deborah_alerts) == 3
        assert len(self._get_dismissed(advisor_2_deborah_alerts)) == 0

    def test_duplicate_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Shrugs off duplicate dismissals."""
        fake_auth.login(admin_uid)
        advisor_1_deborah_alerts = client.get('/api/alerts/current/11667051').json
        alert_id = advisor_1_deborah_alerts[0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200

    def test_dismiss_nonexistent_alerts(self, create_alerts, fake_auth, client):
        """Politely handles nonexistent alert dismissals."""
        fake_auth.login(admin_uid)
        response = client.get('/api/alerts/99999999/dismiss')
        assert response.status_code == 400
        assert response.json['message'] == 'No alert found for id 99999999'

    def test_deactivate_alerts(self, create_alerts, fake_auth, client):
        """Can programmatically deactivate alerts, removing them for all users."""
        Alert.query.filter_by(key='2178_800900300').first().deactivate()

        fake_auth.login(admin_uid)
        advisor_1_deborah_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_1_deborah_alerts) == 2
        assert advisor_1_deborah_alerts[0]['key'] == '2178_500600700'
        assert len(self._get_dismissed(advisor_1_deborah_alerts)) == 0

        fake_auth.login(coe_advisor)
        advisor_2_deborah_alerts = client.get('/api/alerts/current/11667051').json
        assert len(advisor_2_deborah_alerts) == 2
        assert advisor_2_deborah_alerts[0]['key'] == '2178_500600700'
        assert len(self._get_dismissed(advisor_1_deborah_alerts)) == 0
