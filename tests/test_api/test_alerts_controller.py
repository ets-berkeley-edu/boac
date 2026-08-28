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

from boac.api.util import alert_counts_for_curated_group
from boac.models import json_cache
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.curated_group import CuratedGroup
from tests.test_api.api_test_utils import all_cohorts_owned_by

admin_uid = '2040'
asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'


class TestAlertsController:
    """Dismiss Alert API."""

    @classmethod
    def _get_alerts(cls, client, uid):
        response = client.get(f'/api/student/by_uid/{uid}')
        assert response.status_code == 200
        return response.json['notifications']['alert']

    @classmethod
    def _get_dismissed(cls, alerts):
        return list(filter(lambda a: a['dismissed'], alerts))

    def test_dismiss_alerts(self, create_alerts, fake_auth, client):  # noqa: ARG002
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

        fake_auth.login(coe_advisor_uid)
        advisor_2_alerts = self._get_alerts(client, 61889)
        assert len(advisor_2_alerts) == 4
        assert len(self._get_dismissed(advisor_2_alerts)) == 0

    def test_duplicate_dismiss_alerts(self, create_alerts, fake_auth, client):  # noqa: ARG002
        """Shrugs off duplicate dismissals."""
        fake_auth.login(admin_uid)
        advisor_1_alerts = self._get_alerts(client, 61889)
        alert_id = advisor_1_alerts[0]['id']
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200
        response = client.get('/api/alerts/' + str(alert_id) + '/dismiss')
        assert response.status_code == 200

    def test_dismiss_nonexistent_alerts(self, create_alerts, fake_auth, client):  # noqa: ARG002
        """Politely handles nonexistent alert dismissals."""
        fake_auth.login(admin_uid)
        response = client.get('/api/alerts/99999999/dismiss')
        assert response.status_code == 400
        assert response.json['message'] == 'No alert found for id 99999999'

    def test_deactivate_alerts(self, create_alerts, fake_auth, client):  # noqa: ARG002
        """Can programmatically deactivate alerts, removing them for all users."""
        Alert.query.filter_by(key='2178_800900300').first().deactivate()

        fake_auth.login(admin_uid)
        advisor_1_alerts = self._get_alerts(client, 61889)
        assert len(advisor_1_alerts) == 3
        assert next((a for a in advisor_1_alerts if a['key'] == '2178_500600700'), None)
        assert len(self._get_dismissed(advisor_1_alerts)) == 0

        fake_auth.login(coe_advisor_uid)
        advisor_2_alerts = self._get_alerts(client, 61889)
        assert len(advisor_2_alerts) == 3
        assert next((a for a in advisor_2_alerts if a['key'] == '2178_500600700'), None)
        assert len(self._get_dismissed(advisor_1_alerts)) == 0

    def test_alert_dismissal_updates_cohort_alert_counts(self, create_alerts, db, fake_auth, client):  # noqa: ARG002
        """Updates alert counts for cohorts the student belongs to."""
        fake_auth.login(asc_advisor_uid)
        cohort_id = all_cohorts_owned_by(asc_advisor_uid)[0]['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        assert response.json['alertCount'] == 6

        alerts = self._get_alerts(client, 61889)
        client.get('/api/alerts/' + str(alerts[0]['id']) + '/dismiss')
        db.session.expire_all()

        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.json['alertCount'] == 5

    def test_cohort_single_alert_dismissal(self, create_alerts, db, fake_auth, client):  # noqa: ARG002
        """Sets the cohort alert count to zero when the last remaining alert is dismissed."""
        fake_auth.login(asc_advisor_uid)
        cohort_id = all_cohorts_owned_by(asc_advisor_uid)[1]['id']
        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.status_code == 200
        assert response.json['alertCount'] == 1

        alerts = self._get_alerts(client, 98765)
        client.get('/api/alerts/' + str(alerts[0]['id']) + '/dismiss')
        db.session.expire_all()

        response = client.get(f'/api/cohort/{cohort_id}')
        assert response.json['alertCount'] == 0

    def test_clears_cached_curated_group_alert_counts(self, db, create_alerts, fake_auth, client):  # noqa: ARG002
        """Clears cached alert counts for curated groups the student belongs to."""
        fake_auth.login(coe_advisor_uid)
        group_id = CuratedGroup.get_curated_groups_owned_by(uids=[coe_advisor_uid])[0]['id']
        response = client.get(f'/api/curated_group/{group_id}/students_with_alerts')
        assert response.status_code == 200
        student = next(s for s in response.json if s['uid'] == '61889')
        assert student['alertCount'] == 4

        # Make sure alert counts for this curated group are cached
        coe_advisor = AuthorizedUser.find_by_uid(coe_advisor_uid)
        alert_counts_for_curated_group(
            viewer_id=coe_advisor.id,
            group_id=group_id,
        )
        cached_counts = json_cache.fetch(f'alert_counts_curated_group_{group_id}_user_{coe_advisor.id}')
        assert cached_counts == [{'sid': '11667051', 'alertCount': 4}]

        # Dismiss the alert
        alerts = self._get_alerts(client, 61889)
        client.get('/api/alerts/' + str(alerts[0]['id']) + '/dismiss')
        db.session.expire_all()

        # Alert counts for this curated group have been removed from cache
        cached_counts = json_cache.fetch(f'alert_counts_curated_group_{group_id}_user_{coe_advisor.id}')
        assert cached_counts is None

        response = client.get(f'/api/curated_group/{group_id}/students_with_alerts')
        assert response.status_code == 200
        student = next(s for s in response.json if s['uid'] == '61889')
        assert student['alertCount'] == 3

        # Updated alert counts for this curated group are cached
        cached_counts = json_cache.fetch(f'alert_counts_curated_group_{group_id}_user_{coe_advisor.id}')
        assert cached_counts == [{'sid': '11667051', 'alertCount': 3}]

