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
coe_student_uid = '300847'
qcadv_advisor_uid = '53791'


@pytest.fixture()
def mock_degree_check():
    return DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid),
        degree_name=f'Degree check of {coe_student_sid}',
        student_sid='11667051',
    )


@pytest.fixture()
def mock_degree_course():
    marker = datetime.now().timestamp()
    sid = '11667051'
    degree_check = DegreeProgressTemplate.create(
        advisor_dept_codes=['COENG'],
        created_by=AuthorizedUser.get_id_per_uid(coe_advisor_read_write_uid),
        degree_name=f'Degree check of {coe_student_sid}',
        student_sid=sid,
    )
    return DegreeProgressCourse.create(
        degree_check_id=degree_check.id,
        display_name=f'The Decline of Western Civilization ({marker})',
        grade='B+',
        section_id=datetime.utcfromtimestamp(0).microsecond,
        sid=sid,
        term_id=2218,
        units=4,
    )


@pytest.fixture()
def mock_degree_checks():
    user = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
    marker = datetime.now().timestamp()
    degree_checks = []
    for index in (1, 2, 3):
        parent_template = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=user.id,
            degree_name=f'I am a mock template ({marker}_{index})',
        )
        degree_checks.append(
            DegreeProgressTemplate.create(
                advisor_dept_codes=['COENG'],
                created_by=user.id,
                degree_name=f'I am a mock degree check ({marker}_{index})',
                student_sid=coe_student_sid,
                parent_template_id=parent_template.id,
            ),
        )
    std_commit(allow_test_environment=True)
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
    def _api_create_category(cls, client, template_id, expected_status_code=200):
        response = client.post(
            '/api/degree/category/create',
            data=json.dumps({
                'categoryType': 'Category',
                'name': f'Category of the now: {datetime.now()}',
                'parentCategoryId': None,
                'position': 2,
                'templateId': template_id,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_degree_course):
        """Denies anonymous user."""
        _api_assign_course(category_id=1, client=client, course_id=mock_degree_course.id, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_degree_course):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        _api_assign_course(category_id=1, client=client, course_id=mock_degree_course.id, expected_status_code=401)

    def test_illegal_assign(self, client, fake_auth):
        """A course cannot be assigned to a category with a subcategory."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)
        sid = '11667051'
        # Set up
        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree for {sid}',
            student_sid=sid,
        )
        category = DegreeProgressCategory.create(
            category_type='Category',
            name=f'Category for {sid}',
            position=1,
            template_id=degree_check.id,
        )
        # Subcategory
        subcategory = DegreeProgressCategory.create(
            category_type='Subcategory',
            name=f'Subcategory for {sid}',
            parent_category_id=category.id,
            position=category.position,
            template_id=degree_check.id,
        )
        std_commit(allow_test_environment=True)

        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        course_id = api_json['courses']['unassigned'][-1]['id']
        # Expect failure
        _api_assign_course(category_id=category.id, client=client, course_id=course_id, expected_status_code=400)
        # Expect success
        _api_assign_course(category_id=subcategory.id, client=client, course_id=course_id)

    def test_assign_and_unassign_course(self, client, fake_auth):
        """User can assign and unassign a course."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)
        sid = '11667051'
        # Set up
        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree check for {sid}',
            student_sid=sid,
        )
        original_updated_at = degree_check.updated_at
        category = DegreeProgressCategory.create(
            category_type='Category',
            name=f'Category for {sid}',
            position=1,
            template_id=degree_check.id,
        )
        std_commit(allow_test_environment=True)
        # Assign
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        course_id = api_json['courses']['unassigned'][-1]['id']
        course = _api_assign_course(category_id=category.id, client=client, course_id=course_id)
        # Verify assignment
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        assert course['categoryId'] == category.id
        assert course_id in [c['id'] for c in api_json['courses']['assigned']]
        assert course_id not in [c['id'] for c in api_json['courses']['unassigned']]
        # Unassign
        _api_assign_course(category_id=None, client=client, course_id=course_id)
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        assert course_id not in [c['id'] for c in api_json['courses']['assigned']]
        assert course_id in [c['id'] for c in api_json['courses']['unassigned']]
        # Verify update of updated_at
        assert DegreeProgressTemplate.find_by_id(degree_check.id).updated_at != original_updated_at


class TestBatchStudentDegreeChecks:

    @classmethod
    def _api_batch_degree_checks(
            cls,
            client,
            sids,
            template_id,
            expected_status_code=200,
    ):
        response = client.post(
            '/api/degree/check/batch',
            data=json.dumps({
                'sids': sids,
                'templateId': template_id,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_batch_degree_checks(client, sids=[coe_student_sid], template_id=1, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_batch_degree_checks(client, sids=[coe_student_sid], template_id=1, expected_status_code=401)

    def test_create_batch(self, client, fake_auth, mock_template):
        """Authorized user can create a batch of degree checks."""
        fake_auth.login(coe_advisor_read_write_uid)
        student_sids = [coe_student_sid, '11667051', '7890123456', '9100000000']
        api_json = self._api_batch_degree_checks(client, sids=student_sids, template_id=mock_template.id)
        assert api_json == 'started'

    def test_get_status(self, client, fake_auth, mock_template):
        fake_auth.login(coe_advisor_read_write_uid)
        response = client.get('/api/degree/check/batch')
        assert response.status_code == 200
        api_json = json.loads(response.data)
        assert api_json['percentComplete'] is None

        self._api_batch_degree_checks(client, sids=[coe_student_sid], template_id=mock_template.id)

        response = client.get('/api/degree/check/batch')
        assert response.status_code == 200
        api_json = json.loads(response.data)
        assert api_json['percentComplete'] == 1


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
        assert api_json['parentTemplateId'] == mock_template.id


class TestUpdateCourse:
    """Update course in degree check."""

    @classmethod
    def _api_update_course(cls, client, course_id, units, expected_status_code=200):
        response = client.post(
            f'/api/degree/course/{course_id}/update',
            data=json.dumps({'units': units}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_update_course(client, course_id=1, expected_status_code=401, units=3)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_update_course(client, course_id=1, expected_status_code=401, units=3)

    def test_update_template(self, client, fake_auth, mock_degree_check):
        """Authorized user can edit a template."""
        fake_auth.login(coe_advisor_read_write_uid)
        api_json = _api_get_degree(client, degree_check_id=mock_degree_check.id)
        course = api_json['courses']['unassigned'][0]
        units = course['units']

        units_original = units
        units_updated = units + 2
        api_json = self._api_update_course(
            client=client,
            course_id=course['id'],
            units=str(units_updated),
        )
        assert api_json['id'] == course['id']
        # Verify
        api_json = _api_get_degree(client, degree_check_id=mock_degree_check.id)
        unassigned_courses = api_json['courses']['unassigned']
        course = next((c for c in unassigned_courses if c['id'] == course['id']), None)
        assert course['units'] == units_updated
        assert course['sis']['units'] == units_original


class TestGetDegreeCheckStudents:

    @classmethod
    def _api_get_students(cls, client, template_id, sids, expected_status_code=200):
        response = client.post(
            f'/api/degree/{template_id}/students',
            data=json.dumps({'sids': sids}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client, mock_template):
        """Denies anonymous user."""
        self._api_get_students(client, template_id=mock_template.id, sids=[coe_student_sid], expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_template):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        self._api_get_students(client, template_id=mock_template.id, sids=[coe_student_sid], expected_status_code=401)

    def test_authorized_no_students(self, client, fake_auth, mock_template):
        """Authorized user gets an empty list if no students have the degree check."""
        fake_auth.login(coe_advisor_read_write_uid)
        api_json = self._api_get_students(client, template_id=mock_template.id, sids=[coe_student_sid])
        assert api_json == []

    def test_authorized(self, client, fake_auth, mock_degree_checks):
        """Authorized user gets a list of students currently assigned the degree check."""
        fake_auth.login(coe_advisor_read_write_uid)

        def _sort_by(item):
            return item.updated_at
        mock_degree_checks.sort(key=_sort_by, reverse=True)

        current_template_students = self._api_get_students(
            client,
            template_id=mock_degree_checks[0].parent_template_id,
            sids=[coe_student_sid],
        )
        assert len(current_template_students) == 1
        assert current_template_students[0]['sid'] == coe_student_sid
        assert current_template_students[0]['uid'] == coe_student_uid
        assert current_template_students[0]['firstName'] == 'Wolfgang'
        assert current_template_students[0]['lastName'] == "Pauli-O'Rourke"

        old_template_students = self._api_get_students(
            client,
            template_id=mock_degree_checks[2].parent_template_id,
            sids=[coe_student_sid],
        )
        assert len(old_template_students) == 0


class TestGetStudentDegreeChecks:

    @classmethod
    def _api_get_degree_checks(cls, client, uid, expected_status_code=200):
        response = client.get(f'/api/degrees/student/{uid}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_degree_checks(client, uid=coe_student_uid, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        self._api_get_degree_checks(client, uid=coe_student_uid, expected_status_code=401)

    def test_authorized(self, client, fake_auth, mock_degree_checks):
        """Advisor can view student degree checks."""
        fake_auth.login(coe_advisor_read_only_uid)

        def _sort_by(item):
            return item.updated_at
        mock_degree_checks.sort(key=_sort_by, reverse=True)
        expected_current_id = mock_degree_checks[0].id

        degree_checks = self._api_get_degree_checks(client, uid=coe_student_uid)
        assert degree_checks[0]['id'] == expected_current_id
        assert degree_checks[0]['isCurrent'] is True
        assert degree_checks[1]['isCurrent'] is False
        assert degree_checks[2]['isCurrent'] is False


class TestUnassignedCourses:

    def test_ignored_courses(self, client, fake_auth):
        """Authorized user can ignore a course."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)
        # Set up
        sid = '11667051'
        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree check for {sid}',
            student_sid=sid,
        )
        std_commit(allow_test_environment=True)
        # Fetch
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        unassigned_courses = api_json['courses']['unassigned']
        ignored_courses = api_json['courses']['ignored']
        ignored_courses_count = len(ignored_courses)
        # Ignore
        ignore_this_course = unassigned_courses[-1]
        _api_assign_course(
            client=client,
            category_id=None,
            course_id=ignore_this_course['id'],
            ignore=True,
        )
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        # Verify
        unassigned_courses = api_json['courses']['unassigned']
        assert next((c for c in unassigned_courses if c['sectionId'] == ignore_this_course['sectionId']), None) is None

        ignored_courses = api_json['courses']['ignored']
        assert len(ignored_courses) == ignored_courses_count + 1
        assert next((c for c in ignored_courses if c['sectionId'] == ignore_this_course['sectionId']), None)

    def test_unassigned_courses(self, client, fake_auth):
        """Authorized user can un-assign a course."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)
        # Set up
        sid = '11667051'
        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree check for {sid}',
            student_sid=sid,
        )
        category = DegreeProgressCategory.create(
            category_type='Category',
            name=f'Category for {sid}',
            position=1,
            template_id=degree_check.id,
        )
        std_commit(allow_test_environment=True)
        # Fetch
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        assigned_courses = api_json['courses']['assigned']
        unassigned_courses = api_json['courses']['unassigned']
        assert len(unassigned_courses)
        assigned_course_count = len(assigned_courses)
        unassigned_course_count = len(unassigned_courses)
        # Assign
        unassigned_course = unassigned_courses[-1]
        _api_assign_course(client=client, category_id=category.id, course_id=unassigned_course['id'])
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        # Verify
        assigned_courses = api_json['courses']['assigned']
        assert len(assigned_courses) == assigned_course_count + 1
        assert next((c for c in unassigned_courses if c['sectionId'] == unassigned_course['sectionId']), None)

        unassigned_courses = api_json['courses']['unassigned']
        assert len(unassigned_courses) == unassigned_course_count - 1
        assert next((c for c in unassigned_courses if c['sectionId'] == unassigned_course['sectionId']), None) is None


class TestCopyCourse:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_copy_course(
            category_id=1,
            client=client,
            expected_status_code=401,
            section_id=12345,
            sid=coe_student_sid,
            term_id=2218,
        )

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(coe_advisor_read_only_uid)
        _api_copy_course(
            category_id=1,
            client=client,
            expected_status_code=401,
            section_id=12345,
            sid=coe_student_sid,
            term_id=2218,
        )

    def test_copy_course(self, client, fake_auth):
        """User can copy course and add it to a category."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)
        sid = '11667051'
        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree for {sid}',
            student_sid=sid,
        )
        std_commit(allow_test_environment=True)
        degree_check_id = degree_check.id

        # Set up
        def _create_category(category_type='Category', parent_category_id=None):
            category = DegreeProgressCategory.create(
                category_type=category_type,
                name=f'{category_type} for {sid} ({datetime.now().timestamp()})',
                parent_category_id=parent_category_id,
                position=1,
                template_id=degree_check_id,
            )
            return category
        category_1 = _create_category()
        category_2 = _create_category()
        std_commit(allow_test_environment=True)

        # Get sample course from list of unassigned courses
        api_json = _api_get_degree(client=client, degree_check_id=degree_check_id)
        course = api_json['courses']['unassigned'][-1]
        course_id = course['id']
        section_id = course['sectionId']
        copied_course_ids = []

        def _copy_course(category_id, expected_status_code=200):
            course_copy = _api_copy_course(
                category_id=category_id,
                client=client,
                expected_status_code=expected_status_code,
                section_id=section_id,
                sid=sid,
                term_id=course['termId'],
            )
            if expected_status_code == 200:
                copied_course_ids.append(course_copy['id'])
            return course_copy

        # Verify: user cannot copy an unassigned course.
        _copy_course(category_id=category_1.id, expected_status_code=400)
        # Verify: user cannot copy course to a category which already has the course.
        _api_assign_course(category_id=category_1.id, client=client, course_id=course_id)
        by_id = DegreeProgressCourse.find_by_id(course_id)
        assert by_id.category_id == category_1.id
        _copy_course(category_id=category_1.id, expected_status_code=400)

        subcategory = _create_category(category_type='Subcategory', parent_category_id=category_1.id)
        # Verify: user cannot copy course to a category which has subcategories.
        _copy_course(category_id=category_1.id, expected_status_code=400)

        # Verify we can create a copy of course in subcategory, thereby provisioning a new 'Course Requirement'
        child_count = len(DegreeProgressCategory.find_by_parent_category_id(subcategory.id))
        copy_of_course = _copy_course(category_id=subcategory.id)
        children = DegreeProgressCategory.find_by_parent_category_id(subcategory.id)
        assert len(children) == child_count + 1
        assert children[0].category_type == 'Placeholder: Course Copy'
        assert copy_of_course['categoryId'] == children[0].id

        # Assign the copied course to an actual Course Requirement and verify that "placeholder" category is deleted.
        course_requirement = _create_category(category_type='Course Requirement', parent_category_id=subcategory.id)
        placeholder_category_id = copy_of_course['categoryId']
        _api_assign_course(category_id=course_requirement.id, client=client, course_id=copy_of_course['id'])
        assert DegreeProgressCategory.find_by_id(placeholder_category_id) is None

        # Finally, we create a copy for a separate category and expect success.
        copy_of_course = _copy_course(category_id=category_2.id)
        assert copy_of_course['id'] != course_id
        assert copy_of_course['sectionId'] == section_id
        # Verify 'isCopy' property per course
        degree_json = _api_get_degree(client=client, degree_check_id=degree_check_id)
        assigned_courses = degree_json['courses']['assigned']
        unassigned_courses = degree_json['courses']['unassigned']
        assert len(assigned_courses)
        assert len(unassigned_courses)
        # Expect no "copies" in the Unassigned set of courses.
        assert True not in [c['isCopy'] for c in unassigned_courses]
        for assigned_course in assigned_courses:
            course_id = assigned_course['id']
            assert assigned_course['isCopy'] == (course_id in copied_course_ids)


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
        template_id = mock_note.template_id
        original_updated_at = DegreeProgressTemplate.find_by_id(template_id).updated_at

        fake_auth.login(coe_advisor_read_write_uid)
        body = 'Stróż pchnął kość w quiz gędźb vel fax myjń.'
        api_json = self._api_update_degree_note(client, body=body, template_id=template_id)
        assert api_json['templateId']
        assert api_json['body'] == body
        # Verify update of updated_at
        assert DegreeProgressTemplate.find_by_id(template_id).updated_at != original_updated_at


class TestDeleteCategory:

    @classmethod
    def _api_create_category(
            cls,
            client,
            category_type,
            name,
            position,
            template_id,
            description=None,
            expected_status_code=200,
            parent_category_id=None,
            unit_requirement_ids=(),
            units_lower=None,
            units_upper=None,
    ):
        response = client.post(
            '/api/degree/category/create',
            data=json.dumps({
                'categoryType': category_type,
                'description': description,
                'name': name,
                'parentCategoryId': parent_category_id,
                'position': position,
                'templateId': template_id,
                'unitRequirementIds': ','.join(str(id_) for id_ in unit_requirement_ids),
                'unitsLower': units_lower,
                'unitsUpper': units_upper,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_not_authenticated(self, client):
        """Denies anonymous user."""
        assert client.delete('/api/degree/course/1').status_code == 401

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(qcadv_advisor_uid)
        assert client.delete('/api/degree/course/1').status_code == 401

    def test_delete(self, client, fake_auth):
        """Advisor can delete course."""
        advisor = AuthorizedUser.find_by_uid(coe_advisor_read_write_uid)
        fake_auth.login(advisor.uid)
        sid = '11667051'

        degree_check = DegreeProgressTemplate.create(
            advisor_dept_codes=['COENG'],
            created_by=advisor.id,
            degree_name=f'Degree for {sid}',
            student_sid=sid,
        )
        api_json = _api_get_degree(client, degree_check_id=degree_check.id)
        course_id = api_json['courses']['unassigned'][-1]['id']
        categories = []
        for index in (1, 2, 3):
            categories.append(
                self._api_create_category(
                    category_type='Category',
                    client=client,
                    name=f'Category {index}',
                    position=index,
                    template_id=degree_check.id,
                ),
            )
        # Category #2 gets a child 'Course Requirement'
        course_requirement = self._api_create_category(
            category_type='Course Requirement',
            client=client,
            name='Course Requirement',
            parent_category_id=categories[1]['id'],
            position=categories[1]['position'],
            template_id=degree_check.id,
        )
        # Assign course to Category #1
        course = _api_assign_course(
            category_id=categories[0]['id'],
            client=client,
            course_id=course_id,
        )
        # Copy course to Category #2 and then assign it to the 'Course Requirement'
        section_id = course['sectionId']
        term_id = course['termId']
        course_copy_1 = _api_copy_course(
            category_id=categories[1]['id'],
            client=client,
            section_id=section_id,
            sid=sid,
            term_id=term_id,
        )
        placeholder_category_id = course_copy_1['categoryId']
        course_copy_1 = _api_assign_course(
            category_id=course_requirement['id'],
            client=client,
            course_id=course_copy_1['id'],
        )
        # Placeholder category is auto-deleted during re-assignment
        assert not DegreeProgressCategory.find_by_id(placeholder_category_id)
        # Delete the course_copy_1 and expect the underlying 'Course Requirement' to survive
        assert client.delete(f"/api/degree/course/{course_copy_1['id']}").status_code == 200

        # Copy course to Category #3 and then delete. Expect removal of course and its 'Placeholder' category.
        course_copy_2 = _api_copy_course(
            category_id=categories[2]['id'],
            client=client,
            section_id=section_id,
            sid=sid,
            term_id=term_id,
        )
        placeholder_category_id = course_copy_2['categoryId']
        assert 'Placeholder' in DegreeProgressCategory.find_by_id(placeholder_category_id).category_type
        assert client.delete(f"/api/degree/course/{course_copy_2['id']}").status_code == 200
        assert not DegreeProgressCategory.find_by_id(placeholder_category_id)


def _api_assign_course(category_id, client, course_id, expected_status_code=200, ignore=False):
    response = client.post(
        f'/api/degree/course/{course_id}/assign',
        data=json.dumps({'categoryId': category_id, 'ignore': ignore}),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return json.loads(response.data)


def _api_copy_course(
        category_id,
        client,
        section_id,
        sid,
        term_id,
        expected_status_code=200,
):
    response = client.post(
        '/api/degree/course/copy',
        data=json.dumps({
            'categoryId': category_id,
            'sectionId': section_id,
            'sid': sid,
            'termId': term_id,
        }),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return json.loads(response.data)


def _api_get_degree(client, degree_check_id, expected_status_code=200):
    response = client.get(f'/api/degree/{degree_check_id}')
    assert response.status_code == expected_status_code
    return response.json
