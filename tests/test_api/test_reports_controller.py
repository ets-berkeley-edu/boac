"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

import json

admin_uid = '2040'
asc_director_uid = '90412'
l_s_advisor_uid = '188242'
l_s_director_uid = '53791'
l_s_major_advisor_uid = '242881'


class TestAlertsLogExport:
    """Download alerts CSV."""

    @classmethod
    def _api_download_alerts_csv(cls, client, expected_status_code=200):
        response = client.post(
            '/api/reports/download_alerts_csv',
            data=json.dumps({
                'fromDate': '08/01/1900',
                'toDate': '08/01/2525',
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response

    def test_download_alerts_csv_not_authenticated(self, client):
        """Anonymous user is rejected."""
        self._api_download_alerts_csv(client, expected_status_code=401)

    def test_download_alerts_csv_unauthorized(self, client, fake_auth):
        """403 if user is not an admin."""
        fake_auth.login(l_s_advisor_uid)
        self._api_download_alerts_csv(client, expected_status_code=401)

    def test_download_alerts_csv(self, client, create_alerts, fake_auth):
        """Admin can download alerts CSV."""
        fake_auth.login(admin_uid)
        response = self._api_download_alerts_csv(client)
        assert 'csv' in response.content_type
        csv = str(response.data)
        for snippets in [
            ['sid,term,key,type,active,created_at'],
            ['11667051', 'Fall 2017', 'academic_standing,true'],
            ['11667051', 'Spring 2017', 'late_assignment,true'],
            ['11667051', 'Fall 2017', 'late_assignment,true'],
            ['11667051', 'Fall 2017', 'missing_assignment,true'],
            ['2345678901', 'Fall 2017', 'late_assignment,true'],
            ['11667051', 'Fall 2017', 'midterm,true'],
            ['3456789012', 'Fall 2017', 'no_activity,true'],
        ]:
            for snippet in snippets:
                assert snippet in csv, f'Failed on snippet: {snippet}'


class TestNotesReport:

    @classmethod
    def _api_notes_report(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/reports/notes/{dept_code}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_notes_report(client, 'qcadv', expected_status_code=401)

    def test_not_authorized_advisor(self, client, fake_auth):
        """Returns 401 if neither admin nor director."""
        fake_auth.login(l_s_advisor_uid)
        self._api_notes_report(client, 'qcadv', expected_status_code=401)

    def test_not_authorized_director_of_other_dept(self, client, fake_auth):
        """Returns 401 if director in some other dept."""
        fake_auth.login(asc_director_uid)
        self._api_notes_report(client, 'qcadv', expected_status_code=403)

    def test_not_found(self, client, fake_auth):
        """Returns 404 if dept_code not found."""
        fake_auth.login(admin_uid)
        self._api_notes_report(client, 'foo', expected_status_code=404)

    def test_director_can_access_report_per_dept(self, client, fake_auth):
        """Director of L&S Advising can access L&S report."""
        fake_auth.login(l_s_director_uid)
        report = self._api_notes_report(client, 'qcadv')
        assert 'boa' in report
        assert 'asc' in report
        assert 'ei' in report
        assert 'sis' in report

    def test_admin_can_access_dept_report(self, client, fake_auth):
        """Admin user can access L&S report."""
        fake_auth.login(admin_uid)
        report = self._api_notes_report(client, 'qcadv')
        assert 'boa' in report


class TestUsersReport:

    @classmethod
    def _api_users_report(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/reports/users/{dept_code}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_users_report(client, 'qcadv', expected_status_code=401)

    def test_not_authorized_advisor(self, client, fake_auth):
        """Returns 401 if neither admin nor director."""
        fake_auth.login(l_s_advisor_uid)
        self._api_users_report(client, 'qcadv', expected_status_code=401)

    def test_not_authorized_director_of_other_dept(self, client, fake_auth):
        """Returns 401 if director in some other dept."""
        fake_auth.login(asc_director_uid)
        self._api_users_report(client, 'qcadv', expected_status_code=403)

    def test_not_found(self, client, fake_auth):
        """Returns 404 if dept_code not found."""
        fake_auth.login(admin_uid)
        self._api_users_report(client, 'foo', expected_status_code=404)

    def test_director_can_access_report_per_dept(self, client, fake_auth):
        """Director of L&S Advising can access L&S report."""
        fake_auth.login(l_s_director_uid)
        report = self._api_users_report(client, 'qcadv')
        assert report['totalUserCount'] > 0
        assert 'notesCreated' in report['users'][0]

    def test_admin_can_access_dept_report(self, client, fake_auth):
        """Admin user can access L&S report."""
        fake_auth.login(admin_uid)
        report = self._api_users_report(client, 'qcadv')
        assert report['totalUserCount'] > 0
        assert 'notesCreated' in report['users'][0]


class TestAvailableDeptCodesPerUser:

    @classmethod
    def _api_available_departments(cls, client, expected_status_code=200):
        response = client.get('/api/reports/available_departments')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_available_departments(client, expected_status_code=401)

    def test_not_authorized_advisor(self, client, fake_auth):
        """Returns 401 if neither admin nor director."""
        fake_auth.login(l_s_advisor_uid)
        self._api_available_departments(client, expected_status_code=401)

    def test_asc_director(self, client, fake_auth):
        """Returns 401 if director in some other dept."""
        fake_auth.login(asc_director_uid)
        departments = self._api_available_departments(client)
        assert len(departments) == 1
        assert departments == [
            {
                'code': 'UWASC',
                'name': 'Athletic Study Center',
            },
        ]

    def test_director_of_multiple_departments(self, client, fake_auth):
        """Director of multiple departments can access reports accordingly."""
        fake_auth.login(l_s_director_uid)
        departments = self._api_available_departments(client)
        assert len(departments) == 2
        assert departments == [
            {
                'code': 'QCADV',
                'name': 'L&S College Advising',
            },
            {
                'code': 'QCADVMAJ',
                'name': 'L&S Major Advising',
            },
        ]

    def test_admin_has_access_to_all_departments(self, client, fake_auth):
        """Admin user can access all departments."""
        fake_auth.login(admin_uid)
        departments = self._api_available_departments(client)
        assert len(departments) > 5
