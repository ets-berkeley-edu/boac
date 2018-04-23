"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.normalized_cache_enrollment import NormalizedCacheEnrollment
import pytest

test_uid = '1133399'
term_id = 2178
sid = '11667051'
section_id = 90100


@pytest.fixture()
def authenticated_session(fake_auth):
    fake_auth.login(test_uid)


@pytest.fixture()
def course_data_load(fake_auth):
    fake_auth.login(test_uid)
    _json = json.load(open(f'fixtures/sis_enrollments_api_{sid}_{term_id}.json'))
    enrollments = _json.get('apiResponse', {}).get('response', {}).get('studentEnrollments', {})
    sections = []
    for enrollment in enrollments:
        section = enrollment.get('classSection')
        sections.append(section)
    # Cache course data
    NormalizedCacheEnrollment.update_enrollments(term_id=term_id, sid=sid, sections=sections)


class TestCourseController:
    """API for retrieving course info."""

    def test_not_authenticated(self, client):
        """Returns 401 if not authenticated."""
        assert client.get('/api/section/2182/1').status_code == 401

    def test_api_route_not_found(self, authenticated_session, client):
        """Returns a 404 for non-existent section_id."""
        response = client.get('/api/section/2222/1')
        assert response.status_code == 404

    def test_get_section(self, authenticated_session, client, course_data_load):
        """Finds section info in normalized cache."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        assert response.status_code == 200
        section = response.json
        assert section['sectionId'] == section_id
        assert section['displayName'] == 'BURMESE 1A'
        assert section['title'] == 'Introductory Burmese'
        assert section['units'] == 4

    def test_section_student_details(self, authenticated_session, client, course_data_load):
        """Includes per-student details."""
        response = client.get(f'/api/section/{term_id}/{section_id}')
        students = response.json['students']
        assert len(students) == 1
        assert students[0]['uid'] == '61889'
        assert students[0]['sid'] == '11667051'
        assert students[0]['firstName'] == 'Deborah'
        assert students[0]['lastName'] == 'Davies'
        assert students[0]['cumulativeGPA'] == 3.8
        assert students[0]['cumulativeUnits'] == 101.3
        assert students[0]['level'] == 'Junior'
        assert len(students[0]['athletics']) == 2
        assert len(students[0]['majors']) == 2
        assert len(students[0]['term']['enrollments']) == 3
