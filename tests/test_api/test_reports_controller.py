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

admin_uid = '2040'
asc_director_uid = '90412'
l_s_advisor_uid = '188242'
l_s_director_uid = '53791'
l_s_major_advisor_uid = '242881'


class TestBoaUsageSummary:

    @classmethod
    def _api_boa_usage_summary(cls, client, dept_code, expected_status_code=200):
        response = client.get(f'/api/reports/boa_usage_summary/{dept_code}')
        assert response.status_code == expected_status_code
        return response.json

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        self._api_boa_usage_summary(client, 'qcadv', 401)

    def test_not_authorized_advisor(self, client, fake_auth):
        """Returns 401 if neither admin nor director."""
        fake_auth.login(l_s_advisor_uid)
        self._api_boa_usage_summary(client, 'qcadv', 401)

    def test_not_authorized_director_of_other_dept(self, client, fake_auth):
        """Returns 401 if director in some other dept."""
        fake_auth.login(asc_director_uid)
        self._api_boa_usage_summary(client, 'qcadv', 403)

    def test_not_found(self, client, fake_auth):
        """Returns 404 if dept_code not found."""
        fake_auth.login(admin_uid)
        self._api_boa_usage_summary(client, 'foo', 404)

    def director_can_access_report_per_dept(self, client, fake_auth):
        """Director of L&S Advising can access L&S report."""
        fake_auth.login(l_s_director_uid)
        report = self._api_boa_usage_summary(client, 'qcadv')
        assert report['dept']['name'] == 'L&S College Advising'

    def admin_can_access_dept_report(self, client, fake_auth):
        """Admin user can access L&S report."""
        fake_auth.login(admin_uid)
        report = self._api_boa_usage_summary(client, 'qcadv')
        assert report['dept']['name'] == 'L&S College Advising'
