"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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
from tests.test_api.api_test_utils import all_cohorts_owned_by

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor = '1133399'


class TestAlertsController:

    @classmethod
    def _get_alerts(cls, client, uid):
        response = client.get(f'/api/student/by_uid/{uid}')
        assert response.status_code == 200
        return response.json['notifications']['alert']

    @classmethod
    def _get_dismissed(cls, alerts):
        return list(filter(lambda a: a['dismissed'], alerts))

    def test_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Can dismiss alerts for one user without affecting visibility for other users."""
        fake_auth.login(admin_uid)
        advisor_1_alerts = self._get_alerts(client, 61889)
        assert len(advisor_1_alerts) == 4
        assert next((a for a in advisor_1_alerts if a['message'] == "Student's academic standing is 'Probation'."), None)
        assert not next((a for a in advisor_1_alerts if a['dismissed']), None)

        alert_id = advisor_1_alerts[0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        assert response.json['message'] == 'Alert ' + str(alert_id) + ' dismissed by UID 2040'

        advisor_1_alerts = self._get_alerts(client, 61889)
        assert len(advisor_1_alerts) == 4
        assert len(self._get_dismissed(advisor_1_alerts)) == 1

        fake_auth.login(coe_advisor)
        advisor_2_alerts = self._get_alerts(client, 61889)
        assert len(advisor_2_alerts) == 4
        assert len(self._get_dismissed(advisor_2_alerts)) == 0

    def test_duplicate_dismiss_alerts(self, create_alerts, fake_auth, client):
        """Shrugs off duplicate dismissals."""
        fake_auth.login(admin_uid)
        advisor_1_alerts = self._get_alerts(client, 61889)
        alert_id = advisor_1_alerts[0]['id']
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
        advisor_1_alerts = self._get_alerts(client, 61889)
        assert len(advisor_1_alerts) == 3
        assert next((a for a in advisor_1_alerts if a['key'] == '2178_500600700'), None)
        assert len(self._get_dismissed(advisor_1_alerts)) == 0

        fake_auth.login(coe_advisor)
        advisor_2_alerts = self._get_alerts(client, 61889)
        assert len(advisor_2_alerts) == 3
        assert next((a for a in advisor_2_alerts if a['key'] == '2178_500600700'), None)
        assert len(self._get_dismissed(advisor_1_alerts)) == 0

    def test_alert_dismissal_updates_cohort_alert_counts(self, db, create_alerts, fake_auth, client):
        fake_auth.login(asc_advisor_uid)
        cohort_id = all_cohorts_owned_by(asc_advisor_uid)[0]['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.json['alertCount'] == 6

        alerts = self._get_alerts(client, 61889)
        client.get('/api/alerts/' + str(alerts[0]['id']) + '/dismiss')
        db.session.expire_all()

        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.json['alertCount'] == 5
