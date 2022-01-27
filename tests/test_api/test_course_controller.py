"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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

import pytest

asc_advisor_uid = '1081940'
coe_advisor_uid = '1133399'
coe_scheduler_uid = '6972201'
term_id = 2178
student_uid = '61889'
student_sid = '11667051'
section_id = 90100


@pytest.fixture()
def asc_advisor(fake_auth):
    fake_auth.login(asc_advisor_uid)


@pytest.fixture()
def coe_advisor(fake_auth):
    fake_auth.login(coe_advisor_uid)


@pytest.fixture()
def coe_scheduler(fake_auth):
    fake_auth.login(coe_scheduler_uid)


class TestCourseController:

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/section/2182/1').status_code == 401

    def test_coe_scheduler_not_authorized(self, coe_scheduler, client):
        """Returns 403 if user is only a scheduler."""
        assert client.get('/api/section/2182/1').status_code == 401

    def test_not_authorized(self, user_factory, client, fake_auth):
        """Returns 403 if user is not authorized."""
        advisor = user_factory(can_access_canvas_data=False)
        fake_auth.login(advisor.uid)
        assert client.get('/api/section/2182/1').status_code == 403

    def test_api_route_not_found(self, coe_advisor, client):
        """Returns a 404 for non-existent section_id."""
        response = client.get('/api/section/2222/1')
        assert response.status_code == 404

    def test_get_section(self, coe_advisor, client):
        """Returns section info from data loch."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        assert response.status_code == 200
        section = response.json
        assert section['sectionId'] == section_id
        assert section['displayName'] == 'BURMESE 1A'
        assert section['title'] == 'Introductory Burmese'
        assert section['units'] == 4
        assert section['meetings'][0]['days'] == 'Mon, Tue, Wed, Thu, Fri'
        assert section['meetings'][0]['instructionMode'] == 'P'
        assert section['meetings'][0]['instructors'] == ['George Orwell']
        assert section['meetings'][0]['time'] == '12:00 pm - 12:59 pm'
        assert section['meetings'][0]['location'] == 'Wheeler 999'

    def test_section_student_details(self, coe_advisor, client):
        """Includes per-student details."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        students = response.json['students']
        assert len(students) == 1
        assert response.json['totalStudentCount'] == 1
        assert students[0]['academicCareerStatus'] == 'Active'
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['degrees'] is None
        assert students[0]['firstName'] == 'Deborah'
        assert students[0]['lastName'] == 'Davies'
        assert students[0]['level'] == 'Junior'
        assert students[0]['majors'] == ['English BA', 'Nuclear Engineering BS']
        assert students[0]['name'] == 'Deborah Davies'
        assert students[0]['sid'] == '11667051'
        assert students[0]['transfer'] is False
        assert students[0]['uid'] == '61889'
        assert len(students[0]['enrollment']['canvasSites']) == 1
        assert students[0]['enrollment']['midtermGrade'] == 'D+'
        assert isinstance(students[0].get('alertCount'), int)

    def test_section_student_analytics(self, coe_advisor, client):
        section_id = 90200
        response = client.get(f'/api/section/{term_id}/{section_id}')
        students = response.json['students']
        assert len(students) == 1
        assert students[0]['enrollment']['enrollmentStatus'] == 'E'
        assert students[0]['enrollment']['gradingBasis'] == 'Letter'
        # Per-site analytics are used by the List view.
        assert len(students[0]['enrollment']['canvasSites']) == 2
        assignments_submitted_0 = students[0]['enrollment']['canvasSites'][0]['analytics']['assignmentsSubmitted']
        assert assignments_submitted_0['student']['percentile'] == 64
        current_score_0 = students[0]['enrollment']['canvasSites'][0]['analytics']['currentScore']
        assert current_score_0['displayPercentile'] == '76th'
        assert current_score_0['student']['percentile'] == 73
        assignments_submitted_1 = students[0]['enrollment']['canvasSites'][1]['analytics']['assignmentsSubmitted']
        assert assignments_submitted_1['student']['percentile'] is None
        current_score_1 = students[0]['enrollment']['canvasSites'][1]['analytics']['currentScore']
        assert current_score_1['displayPercentile'] == '11th'
        assert current_score_1['student']['percentile'] == 12
        # Cross-site analytics are used by the Matrix view.
        assert students[0]['analytics']['assignmentsSubmitted']['percentile'] == 64
        assert students[0]['analytics']['currentScore']['percentile'] == 42.5

    def test_section_mean_course_analytics(self, coe_advisor, client):
        """Calculates mean course analytics across all sites associated with the section."""
        section_id = 90200
        response = client.get(f'/api/section/{term_id}/{section_id}')
        mean_metrics = response.json['meanMetrics']
        assert mean_metrics['assignmentsSubmitted']['displayPercentile'] == '50th'
        assert mean_metrics['assignmentsSubmitted']['percentile'] == 57
        assert mean_metrics['currentScore']['displayPercentile'] == '50th'
        assert mean_metrics['currentScore']['percentile'] == 40.5
        assert mean_metrics['lastActivity']['displayPercentile'] == '50th'
        assert mean_metrics['lastActivity']['percentile'] == 46
        assert mean_metrics['gpa']['cumulative'] == 3.131
        assert mean_metrics['gpa']['2175'] == 3.055
        assert mean_metrics['gpa']['2172'] == 3.23

    def test_section_student_athletics_asc(self, asc_advisor, client):
        """Includes athletics for ASC advisors."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        students = response.json['students']
        assert len(students[0]['athleticsProfile']['athletics']) == 2
        assert isinstance(students[0].get('alertCount'), int)

    def test_section_student_athletics_non_asc(self, coe_advisor, client):
        """Does not include athletics for non-ASC advisors."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        students = response.json['students']
        assert 'athletics' not in students[0]

    def test_section_student_alert_count(self, create_alerts, coe_advisor, client):
        """Includes alert count of COE student."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        assert response.json['students'][0].get('alertCount') == 4
