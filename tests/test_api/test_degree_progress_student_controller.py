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

from datetime import datetime
import json

from boac import std_commit
from boac.models.authorized_user import AuthorizedUser
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_note import DegreeProgressNote
from boac.models.degree_progress_template import DegreeProgressTemplate
import pytest

coe_advisor_read_only_uid = '6972201'
coe_advisor_read_write_uid = '1133399'
coe_student_sid = '9000000000'
qcadv_advisor_uid = '53791'


@pytest.fixture()
def mock_degree_course():
    marker = datetime.now().timestamp()
    return DegreeProgressCourse.create(
        display_name=f'The Decline of Western Civilization ({marker})',
        grade='B+',
        section_id=1905013,
        sid=coe_student_sid,
        term_id=2218,
        units=4,
    )


@pytest.fixture()
def mock_degree_checks():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    marker = datetime.now().timestamp()
    degree_checks = []
    for index in (1, 2, 3):
        degree_checks.append(
            DegreeProgressTemplate.create(
                advisor_dept_codes=['COENG'],
                created_by=user.id,
                degree_name=f'I am a mock template, made for a mock category ({marker}_{index})',
                student_sid=coe_student_sid,
            ),
        )
    return degree_checks


@pytest.fixture()
def mock_template():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    marker = datetime.now().timestamp()
    return DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=user.id,
        degree_name=f'I am a mock template, made for a mock category ({marker})',
    )


@pytest.fixture()
def mock_note():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    template = DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=user.id,
        degree_name='I am a mock template, made for a mock note',
    )
    return DegreeProgressNote.upsert(
        body='A mock note.',
        template_id=template.id,
        updated_by=user.id,
    )


class TestAssignCourse:

    @classmethod
    def _api_get_template(cls, client, template_id, expected_status_code=200):
        response = client.get(f'/api/degree/{template_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client, mock_degree_course):
        """Denies anonymous user."""
        _api_assign_course(client, category_id=1, course=mock_degree_course, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_degree_course):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        _api_assign_course(client, category_id=1, course=mock_degree_course, expected_status_code=401)

    def test_create_category(self, client, fake_auth, mock_degree_course, mock_template):
        """Authorized user can create a degree check."""
        user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(user.uid)
        category = DegreeProgressCategory.create(
            category_type='Course',
            course_units='3',
            name='History of Western Philosophy',
            position=1,
            template_id=mock_template.id,
        )
        _api_assign_course(client, category_id=category.id, course=mock_degree_course)
        # Verify
        api_json = self._api_get_template(client, template_id=mock_template.id)
        categories_json = api_json['categories']
        assert len(categories_json) == 1

        assert categories_json[0]['id'] == category.id
        fulfilled_by = categories_json[0]['fulfilledBy']
        assert len(fulfilled_by) == 1

        course = fulfilled_by[0]
        assert course['name'] == mock_degree_course.display_name
        category_ids = course['categoryIds']
        assert len(category_ids) == 1
        assert category_ids[0] == category.id


class TestCreateStudentDegreeCheck:

    @classmethod
    def _api_create_degree_check(
            cls,
            client,
            sid,
            template_id,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/degree/check/{sid}/create',
            data=json.dumps({'templateId': template_id}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_degree_check(client, sid=coe_student_sid, template_id=1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_create_degree_check(client, sid=coe_student_sid, template_id=1, expected_status_code=401)

    def test_create_category(self, client, fake_auth, mock_template):
        """Authorized user can create a degree check."""
        fake_auth.login(coe_advisor_read_write_uid)
        api_json = self._api_create_degree_check(client, sid=coe_student_sid, template_id=mock_template.id)
        assert api_json['id']


class TestGetStudentDegreeChecks:

    @classmethod
    def _api_get_degree_checks(cls, client, sid, expected_status_code=200):
        response = client.get(f'/api/degrees/student/{sid}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_degree_checks(client, sid=coe_student_sid, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_degree_checks(client, sid=coe_student_sid, expected_status_code=401)

    def test_authorized(self, client, fake_auth, mock_degree_checks, app):
        """Authorized user can get student degree checks."""
        fake_auth.login(coe_advisor_read_only_uid)

        def _sort_by(item):
            return item.updated_at
        mock_degree_checks.sort(key=_sort_by, reverse=True)
        expected_current_id = mock_degree_checks[0].id

        degree_checks = self._api_get_degree_checks(client, sid=coe_student_sid)
        assert len(degree_checks) == 3
        assert degree_checks[0]['id'] == expected_current_id
        assert degree_checks[0]['isCurrent'] is True
        assert degree_checks[1]['isCurrent'] is False
        assert degree_checks[2]['isCurrent'] is False


class TestGetUnassignedCourses:

    @classmethod
    def _api_get_unassigned_courses(cls, client, degree_check_id, expected_status_code=200):
        response = client.get(f'/api/degree/{degree_check_id}/courses/unassigned')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_unassigned_courses(client, degree_check_id=1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_unassigned_courses(client, degree_check_id=1, expected_status_code=401)

    def test_authorized(self, client, fake_auth, mock_degree_checks):
        """Authorized user can get student degree checks."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)

        sid_with_enrollments = '11667051'

        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree check for {sid_with_enrollments}',
            student_sid=sid_with_enrollments,
        )
        category = DegreeProgressCategory.create(
            category_type='Category',
            name=f'Category for {sid_with_enrollments}',
            position=1,
            template_id=degree_check.id,
        )
        std_commit(allow_test_environment=True)

        unassigned_courses = self._api_get_unassigned_courses(client, degree_check_id=degree_check.id)
        unassigned_course_count = len(unassigned_courses)
        assert len(unassigned_courses)
        unassigned_course = DegreeProgressCourse.query.filter_by(
            section_id=unassigned_courses[-1]['sectionId'],
            sid=unassigned_courses[-1]['sid'],
            term_id=unassigned_courses[-1]['termId'],
        ).first()

        # Assign the course
        _api_assign_course(client, category_id=category.id, course=unassigned_course)
        unassigned_courses = self._api_get_unassigned_courses(client, degree_check_id=degree_check.id)
        assert len(unassigned_courses) == unassigned_course_count - 1
        assert next((c for c in unassigned_courses if c['sectionId'] == unassigned_course.section_id), None) is None


class TestUpdateDegreeNote:

    @classmethod
    def _api_update_degree_note(
            cls,
            client,
            body,
            template_id,
            expected_status_code=200,
    ):
        response = client.post(
            f'/api/degree/{template_id}/note',
            data=json.dumps({'body': body}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_template):
        """Denies anonymous user."""
        self._api_update_degree_note(client, body='', template_id=mock_template.id, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_template):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_update_degree_note(client, body='', template_id=mock_template.id, expected_status_code=401)

    def test_create_degree_note(self, client, fake_auth, mock_template):
        """Authorized user can create a degree note."""
        fake_auth.login(coe_advisor_read_write_uid)
        body = """Pranzo d'acqua \n\nfa volti sghembi."""
        api_json = self._api_update_degree_note(client, body=body, template_id=mock_template.id)
        assert api_json['templateId']
        assert api_json['body'] == body

    def test_edit_degree_note(self, client, fake_auth, mock_note):
        """Authorized user can edit a degree note."""
        fake_auth.login(coe_advisor_read_write_uid)
        body = 'Stróż pchnął kość w quiz gędźb vel fax myjń.'
        api_json = self._api_update_degree_note(client, body=body, template_id=mock_note.template_id)
        assert api_json['templateId']
        assert api_json['body'] == body


def _api_assign_course(client, category_id, course, expected_status_code=200):
    data = {
        'categoryId': category_id,
        'sectionId': course.section_id,
        'sid': course.sid,
        'termId': course.term_id,
    }
    response = client.post(
        '/api/degree/course/assign',
        data=json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
