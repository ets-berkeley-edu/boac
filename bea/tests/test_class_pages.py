"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from bea.config.bea_test_config import BEATestConfig
from bea.models.department import Department
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.class_pages()


@pytest.mark.usefixtures('page_objects')
class TestClassPagesLogin:

    def test_login(self):
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('tc', test.test_cases, ids=[f'UID{tc.student.uid} {tc.section.term.sis_id}-{tc.section.ccn}'
                                                     for tc in test.test_cases], scope='class')
class TestClassPagesSectionInfo:

    def test_student_page_section_link(self, tc):
        self.student_page.load_page(tc.student)
        self.student_page.click_class_page_link(tc.section.term.sis_id, tc.section.ccn)

    def test_class_page_term_name(self, tc):
        utils.assert_equivalence(self.class_page.course_term(), tc.section.term.name)

    def test_class_page_course_code(self, tc):
        utils.assert_equivalence(self.class_page.course_code(), tc.section.code)

    def test_class_page_course_title(self, tc):
        utils.assert_equivalence(self.class_page.course_title(), tc.section.title)

    def test_class_page_section_format(self, tc):
        utils.assert_equivalence(self.class_page.section_format(), tc.section.instruction_format)

    def test_class_page_section_number(self, tc):
        utils.assert_equivalence(self.class_page.section_number(), tc.section.number)

    def test_class_page_section_ccn(self, tc):
        utils.assert_equivalence(self.class_page.section_ccn(), tc.section.ccn)

    def test_class_page_meeting_instructors(self, tc):
        for meeting in tc.section.meetings:
            idx = tc.section.meetings.index(meeting)
            instructor_names = [f'{i.first_name} {i.last_name}' for i in meeting.instructors]
            instructor_names = list(set(instructor_names))
            instructor_names.sort()
            utils.assert_equivalence(self.class_page.meeting_instructors(idx), instructor_names)

    def test_class_page_meeting_days(self, tc):
        for meeting in tc.section.meetings:
            idx = tc.section.meetings.index(meeting)
            utils.assert_equivalence(self.class_page.meeting_days(idx), meeting.days)

    def test_class_page_meeting_times(self, tc):
        for meeting in tc.section.meetings:
            idx = tc.section.meetings.index(meeting)
            meeting_time = f'{meeting.start_time} - {meeting.end_time}'.strip() if meeting.start_time else None
            utils.assert_equivalence(self.class_page.meeting_time(idx), meeting_time)

    def test_class_page_meeting_locations(self, tc):
        for meeting in tc.section.meetings:
            idx = tc.section.meetings.index(meeting)
            if meeting.location:
                assert meeting.location in self.class_page.meeting_location(idx)

    def test_class_page_first_student(self, tc):
        sids = self.class_page.list_view_sids()
        assert sids[0] == tc.student.sid

    def test_class_page_majors(self, tc):
        active_majors = [maj['major'] for maj in tc.student.profile_data.majors() if maj['active']]
        active_majors.sort()
        if active_majors:
            utils.assert_equivalence(self.class_page.student_majors(tc.student), active_majors)
        else:
            assert not self.class_page.student_majors(tc.student)

    def test_class_page_graduation(self, tc):
        profile_data = tc.student.profile_data
        grads = profile_data.graduations()
        if profile_data.academic_career_status() == 'Completed' and grads:
            assert grads[0]['date'].strftime('%b %e, %Y') in self.class_page.student_graduation()
            for major in grads[0]['majors']:
                assert major['plan'] in self.class_page.student_graduation(tc.student)
        else:
            utils.assert_equivalence(self.class_page.student_level(tc.student), profile_data.level())

    def test_class_page_academic_career_status(self, tc):
        profile_data = tc.student.profile_data
        if profile_data.academic_career_status() == 'Inactive':
            assert self.class_page.is_student_inactive(tc.student, tc.section)
        else:
            assert not self.class_page.is_student_inactive(tc.student, tc.section)

    def test_class_page_sports(self, tc):
        teams = tc.student.profile_data.asc_teams()
        if teams and test.dept == Department.ASC:
            sports = list(map(lambda sp: sp.replace(' (AA)', ''), teams))
            sports.sort()
            utils.assert_equivalence(self.class_page.student_sports(tc.student), sports)
        else:
            assert not self.class_page.student_sports(tc.student)

    def test_class_page_final_grade_vs_grading_basis(self, tc):
        course = tc.student.enrollment_data.course_by_section_id(tc.section)
        student_data = tc.student.enrollment_data.sis_course_data(course)
        if student_data['grade']:
            utils.assert_equivalence(self.class_page.student_final_grade(tc.student), student_data['grade'])
        else:
            utils.assert_equivalence(self.class_page.student_final_grade(tc.student), student_data['grading_basis'])

    def test_class_page_midpoint_grade(self, tc):
        course = tc.student.enrollment_data.course_by_section_id(tc.section)
        student_data = tc.student.enrollment_data.sis_course_data(course)
        if student_data['midpoint']:
            utils.assert_equivalence(self.class_page.student_mid_point_grade(tc.student), student_data['midpoint'])
        else:
            utils.assert_equivalence(self.class_page.student_mid_point_grade(tc.student), '—')

    def test_class_page_site_code(self, tc):
        course = tc.student.enrollment_data.course_by_section_id(tc.section)
        sites = tc.student.enrollment_data.course_sites(course)
        for site in sites:
            site_data = tc.student.enrollment_data.site_metadata(site)
            node = sites.index(site) + 1
            utils.assert_equivalence(self.class_page.site_code(tc.student, node), site_data['code'])

    def test_class_page_site_assignments(self, tc):
        course = tc.student.enrollment_data.course_by_section_id(tc.section)
        sites = tc.student.enrollment_data.course_sites(course)
        for site in sites:
            assignment_data = tc.student.enrollment_data.assignments_submitted(site)
            visible_data = self.class_page.visible_assigns_data(tc.student, sites.index(site))
            if not assignment_data['score']:
                assert visible_data['assigns_submit_no_data']
            elif assignment_data['score'] == 0:
                assert visible_data['assigns_submitted'] in ['0', '--']
            else:
                utils.assert_equivalence(visible_data['assigns_submitted'], assignment_data['score'])

    def test_class_page_site_grades(self, tc):
        course = tc.student.enrollment_data.course_by_section_id(tc.section)
        sites = tc.student.enrollment_data.course_sites(course)
        for site in sites:
            grades_data = tc.student.enrollment_data.assignment_grades(site)
            visible_data = self.class_page.visible_assigns_data(tc.student, sites.index(site))
            if not grades_data['score']:
                assert visible_data['assigns_grade_no_data']
            elif grades_data['score'] == 0:
                assert visible_data['assigns_grade'] in ['0', '--']
            else:
                utils.assert_equivalence(visible_data['assigns_grade'], grades_data['score'])

    def test_class_page_enrollment(self, tc):
        if len(tc.section.enrollments) > app.config['MAX_CLASS_PAGE_CLASS_SIZE']:
            app.logger.info('Skipping enrollment verification because class is too big')
        else:
            expected_sids = list(map(lambda en: en.sid, tc.section.enrollments))
            expected_sids.sort()
            visible_sids = self.class_page.visible_sids()
            visible_sids.sort()
            utils.assert_equivalence(visible_sids, expected_sids)
