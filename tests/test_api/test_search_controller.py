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


import pytest
import simplejson as json


class TestAthleticsStudyCenter:
    """ASC-specific API calls."""

    @pytest.fixture()
    def authenticated_session(self, fake_auth):
        fake_auth.login('1133399')

    def test_multiple_teams(self, client):
        """Includes multiple team memberships."""
        response = client.get('/api/students/all')
        assert response.status_code == 200
        athletics = next(user['athletics'] for user in response.json if user['uid'] == '98765')
        assert len(athletics) == 2
        group_codes = [a['groupCode'] for a in athletics]
        assert 'MFB-DB' in group_codes
        assert 'MFB-DL' in group_codes

    def test_get_intensive_cohort(self, authenticated_session, client):
        """Returns the canned 'intensive' cohort, available to all authenticated users."""
        response = client.post('/api/students', data=json.dumps({'inIntensiveCohort': True}), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' in cohort
        assert cohort['totalStudentCount'] == len(cohort['students']) == 5
        assert 'teamGroups' not in cohort
        for student in cohort['students']:
            assert student['inIntensiveCohort']

    def test_order_by_with_intensive_cohort(self, authenticated_session, client):
        """Returns the canned 'intensive' cohort, available to all authenticated users."""
        all_expected_order = {
            'first_name': ['61889', '1022796', '1049291', '242881', '211159'],
            'gpa': ['211159', '1022796', '242881', '1049291', '61889'],
            'group_name': ['211159', '242881', '1049291', '61889', '1022796'],
            'last_name': ['1022796', '61889', '1049291', '242881', '211159'],
            'level': ['1022796', '211159', '242881', '1049291', '61889'],
            'major': ['1022796', '242881', '61889', '1049291', '211159'],
            'units': ['61889', '211159', '1022796', '242881', '1049291'],
        }
        for order_by, expected_uid_list in all_expected_order.items():
            args = {
                'inIntensiveCohort': True,
                'orderBy': order_by,
            }
            response = client.post('/api/students', data=json.dumps(args), content_type='application/json')
            assert response.status_code == 200, f'Non-200 response where order_by={order_by}'
            cohort = json.loads(response.data)
            assert cohort['totalStudentCount'] == 5, f'Wrong count where order_by={order_by}'
            uid_list = [s['uid'] for s in cohort['students']]
            assert uid_list == expected_uid_list, f'Unmet expectation where order_by={order_by}'

    def test_get_inactive_cohort(self, authenticated_session, client):
        response = client.post('/api/students', data=json.dumps({'isInactiveAsc': True}), content_type='application/json')
        assert response.status_code == 200
        cohort = json.loads(response.data)
        assert 'students' in cohort
        assert cohort['totalStudentCount'] == len(cohort['students']) == 1
        assert 'teamGroups' not in cohort
        inactive_student = response.json['students'][0]
        assert not inactive_student['isActiveAsc']
        assert inactive_student['statusAsc'] == 'Trouble'


class TestSearch:
    """Student Search API."""

    @pytest.fixture()
    def authenticated_session(self, fake_auth):
        fake_auth.login('1133399')

    def test_all_students(self, client):
        """Returns a list of students."""
        response = client.get('/api/students/all')
        assert response.status_code == 200
        # We have one student not on a team
        assert len(response.json) == 6

    def test_search_not_authenticated(self, client):
        """Search is not available to the world."""
        response = client.post('/api/students/search')
        assert response.status_code == 401

    def test_search_with_missing_input(self, client, fake_auth):
        """Search is nothing without input."""
        fake_auth.login('2040')
        response = client.post('/api/students/search', data=json.dumps({'searchPhrase': ' \t  '}), content_type='application/json')
        assert response.status_code == 400

    def test_search_by_sid_snippet(self, client, fake_auth):
        """Search by snippet of SID."""
        fake_auth.login('2040')
        response = client.post('/api/students/search', data=json.dumps({'searchPhrase': '89012'}), content_type='application/json')
        assert response.status_code == 200
        assert len(response.json['students']) == response.json['totalStudentCount'] == 2

    def test_search_by_name_snippet(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        response = client.post('/api/students/search', data=json.dumps({'searchPhrase': 'dav'}), content_type='application/json')
        assert response.status_code == 200
        students = response.json['students']
        assert len(students) == response.json['totalStudentCount'] == 3
        assert ['Crossman', 'Davies', 'Doolittle'] == [s['lastName'] for s in students]

    def test_search_by_full_name_snippet(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        permutations = ['david c', 'john  david cro', 'john    cross', ' crossman, j ']
        for phrase in permutations:
            response = client.post(
                '/api/students/search',
                data=json.dumps({'searchPhrase': phrase}),
                content_type='application/json',
            )
            message_if_fail = f'Unexpected result(s) when search phrase={phrase}'
            assert response.status_code == 200, message_if_fail
            students = response.json['students']
            assert len(students) == response.json['totalStudentCount'] == 1, message_if_fail
            assert students[0]['lastName'] == 'Crossman', message_if_fail

    def test_search_order_by_offset_limit(self, client, fake_auth):
        """Search by snippet of name."""
        fake_auth.login('2040')
        args = {
            'searchPhrase': 'dav',
            'orderBy': 'major',
            'offset': 1,
            'limit': 1,
        }
        response = client.post('/api/students/search', data=json.dumps(args), content_type='application/json')
        assert response.status_code == 200
        assert response.json['totalStudentCount'] == 3
        assert len(response.json['students']) == 1
        assert 'Crossman' == response.json['students'][0]['lastName']

    def test_get_students(self, authenticated_session, client):
        data = {
            'gpaRanges': ['numrange(3, 3.5, \'[)\')', 'numrange(3.5, 4, \'[]\')'],
            'groupCodes': ['MFB-DB', 'MFB-DL'],
            'levels': ['Junior', 'Senior'],
            'majors': [
                'Chemistry BS',
                'English BA',
                'History BA',
                'Letters & Sci Undeclared UG',
            ],
            'unitRanges': [],
            'inIntensiveCohort': None,
            'orderBy': 'last_name',
            'offset': 1,
            'limit': 50,
        }
        response = client.post('/api/students', data=json.dumps(data), content_type='application/json')

        assert response.status_code == 200
        assert 'students' in response.json
        students = response.json['students']
        assert 2 == len(students)
        # Offset of 1, ordered by lastName
        assert ['1133399', '242881'] == [student['uid'] for student in students]
        group_codes_1133399 = [a['groupCode'] for a in students[0]['athletics']]
        assert len(group_codes_1133399) == 3
        assert 'MFB-DB' in group_codes_1133399
        assert 'MFB-DL' in group_codes_1133399
        assert 'MTE' in group_codes_1133399
        group_codes_242881 = [a['groupCode'] for a in students[1]['athletics']]
        assert group_codes_242881 == ['MFB-DL']
