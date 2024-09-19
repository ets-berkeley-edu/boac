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

import calendar
from datetime import datetime as dt
import os
import random

from bea.config.bea_test_case import BEATestCase
from bea.models.academic_standings import AcademicStandings
from bea.models.advisor_role import AdvisorRole
from bea.models.cohorts_and_groups.cohort_admit_filter import CohortAdmitFilter
from bea.models.cohorts_and_groups.cohort_filter import CohortFilter
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.incomplete_grades import IncompleteGrades
from bea.models.notes_and_appts.note_attachment import NoteAttachment
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.term import Term
from bea.models.user import User
from bea.test_utils import boa_utils
from bea.test_utils import nessie_filter_admits_utils
from bea.test_utils import nessie_filter_students_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app


class BEATestConfig(object):

    def __init__(self, data=None, dept=None):
        self.data = data or {}
        self.dept = dept or Department.L_AND_S
        self.test_admits = []
        self.test_cases = []
        self.test_id = f'{calendar.timegm(dt.now().timetuple())}'
        self.test_students = []

    @property
    def admin(self):
        return self.data['admin']

    @admin.setter
    def admin(self, value):
        self.data['admin'] = value

    @property
    def admits(self):
        return self.data['admits']

    @admits.setter
    def admits(self, value):
        self.data['admits'] = value

    @property
    def advisor(self):
        return self.data['advisor']

    @advisor.setter
    def advisor(self, value):
        self.data['advisor'] = value

    @property
    def advisor_read_only(self):
        return self.data['advisor_read_only']

    @advisor_read_only.setter
    def advisor_read_only(self, value):
        self.data['advisor_read_only'] = value

    @property
    def attachments(self):
        return self.data['attachments']

    @attachments.setter
    def attachments(self, value):
        self.data['attachments'] = value

    @property
    def default_cohort(self):
        return self.data['cohort']

    @default_cohort.setter
    def default_cohort(self, value):
        self.data['cohort'] = value

    @property
    def degree_templates(self):
        return self.data['default_cohort']

    @degree_templates.setter
    def degree_templates(self, value):
        self.data['degree_templates'] = value

    @property
    def dept(self):
        return self.data['dept']

    @dept.setter
    def dept(self, value):
        self.data['dept'] = value

    @property
    def searches(self):
        return self.data['searches']

    @searches.setter
    def searches(self, value):
        self.data['searches'] = value

    @property
    def students(self):
        return self.data['students']

    @students.setter
    def students(self, value):
        self.data['students'] = value

    @property
    def term(self):
        return self.data['term']

    @term.setter
    def term(self, value):
        self.data['term'] = value

    def set_dept(self, dept=None):
        self.dept = dept or Department.L_AND_S

    def set_advisor(self, uid=None):
        role = DepartmentMembership(advisor_role=AdvisorRole.ADVISOR,
                                    dept=self.dept,
                                    is_automated=None,
                                    )
        boa_advisors = boa_utils.get_dept_advisors(self.dept, role)
        boa_advisors.reverse()
        if self.dept == Department.ADMIN:
            boa_advisor = User({'uid': utils.get_admin_uid()})
        elif uid:
            boa_advisor = next(filter(lambda a: a.uid == uid, boa_advisors))
        else:
            boa_advisor = next(filter(lambda a: a.depts == [self.dept], boa_advisors))

        nessie_advisor = nessie_timeline_utils.get_advising_note_author(boa_advisor.uid)
        if nessie_advisor:
            boa_advisor.sid = nessie_advisor.sid
            boa_advisor.first_name = nessie_advisor.first_name
            boa_advisor.last_name = nessie_advisor.last_name
        boa_utils.get_advisor_names(boa_advisor)
        app.logger.info(f'{vars(boa_advisor)}')
        self.advisor = boa_advisor

    def set_read_only_advisor(self):
        advisors = boa_utils.get_dept_advisors(self.dept)
        advisors = list(filter(lambda a: (len(a.uid) > 1), advisors))
        for advisor in advisors:
            if f'{advisor.uid}' != f'{self.advisor.uid}' and nessie_timeline_utils.get_advising_note_author(
                    advisor.uid):
                self.advisor_read_only = advisor
                break

    def set_students(self, students=None, opts=None):
        self.students = students or nessie_utils.get_all_students(opts)
        if opts and opts['include_inactive']:
            app.logger.info('Pool of test students will include inactive students')
        else:
            self.students = [s for s in self.students if s.status == 'active']

    def set_base_configs(self, dept=None, opts=None):
        self.term = utils.get_current_term()
        self.set_dept(dept)
        self.set_advisor()
        self.set_students(opts=opts)

    def set_admits(self):
        self.admits = nessie_utils.get_admits()

    def set_default_cohort(self, cohort_filter=None, opts=None):
        if not cohort_filter:
            if opts and opts['include_inactive']:
                data = {
                    'intended_majors': [{'major': app.config['TEST_DEFAULT_COHORT_MAJOR']}],
                    'career_statuses': [{'status': 'Active'}, {'status': 'Inactive'}],
                }
            else:
                data = {
                    'intended_majors': [{'major': app.config['TEST_DEFAULT_COHORT_MAJOR']}],
                }
            cohort_filter = CohortFilter(dept=self.dept, data=data)
            self.default_cohort = FilteredCohort
            self.default_cohort.name = f'Cohort {self.test_id}'
            self.default_cohort.search_criteria = cohort_filter
            filtered_sids = nessie_filter_students_utils.get_cohort_result(self, self.default_cohort.search_criteria)
            self.default_cohort.members = [s for s in self.students if s.sid in filtered_sids]

    def set_test_students(self, count, opts=None):
        self.test_students = []
        test_sids = []

        # Use a specific set of students, represented by a string of space-separated UIDs
        uid_string = os.getenv('UIDS')
        if uid_string:
            app.logger.info('Running tests using students with a fixed set of UIDs')
            uids = uid_string.split()
            self.test_students = list(filter(lambda st: st.uid in uids, self.students))

        elif opts:

            # Use a cohort of students
            if opts.get('cohort_members'):
                app.logger.info('Running tests using students within a cohort')
                random.shuffle(self.default_cohort.members)
                self.test_students.extend(self.default_cohort.members[:count])

            # Use students with active career status
            if opts.get('active'):
                active = []
                for s in self.students:
                    if s.status == 'active':
                        active.append(s)
                random.shuffle(active)
                test_sids.extend(active[:count])

            # Use students who represent different appt sources
            if opts.get('appts'):
                app.logger.info('Running tests using students with appointments')
                sids = nessie_utils.get_all_student_sids()

                sis_sids = nessie_timeline_utils.get_sids_with_sis_appts()
                sis_sids = list(set(sids) & set(sis_sids))
                app.logger.info(f'There are {len(sis_sids)} students with SIS appointments')

                ycbm_sids = nessie_timeline_utils.get_sids_with_ycbm_appts()
                ycbm_sids = list(set(sids) & set(ycbm_sids))
                app.logger.info(f'There are {len(ycbm_sids)} students with YCBM appointments')

                for sid_list in [sis_sids, ycbm_sids]:
                    random.shuffle(sid_list)
                    test_sids.extend(sid_list[:count])

            # Use students with enrollments in the current term
            if opts.get('enrollments'):
                app.logger.info('Running tests using students with enrollments')
                enrolled_sids = nessie_utils.get_sids_with_enrollments(self.term.sis_id)
                random.shuffle(enrolled_sids)
                test_sids.extend(enrolled_sids[:count])

            # Use students with inactive career status
            if opts.get('inactive'):
                inactive = []
                for s in self.students:
                    if s.status != 'active':
                        inactive.append(s)
                random.shuffle(inactive)
                test_sids.extend(inactive[:count])

            # Use students with incomplete grades, one student for each
            if opts.get('incomplete_grades'):
                app.logger.info('Running tests using students with various incomplete grades')
                term_id_0 = utils.get_prev_term_sis_id()
                term_id_1 = utils.get_prev_term_sis_id(term_id_0)
                term_id_2 = utils.get_prev_term_sis_id(term_id_1)
                term_id_3 = utils.get_prev_term_sis_id(term_id_2)
                term_ids = [term_id_2, term_id_3]
                for incomplete in IncompleteGrades:
                    frozen_sids = nessie_utils.get_sids_with_incomplete_grades(incomplete, term_ids, True)
                    thawed_sids = nessie_utils.get_sids_with_incomplete_grades(incomplete, term_ids, False)
                    if frozen_sids:
                        random.shuffle(frozen_sids)
                        test_sids.append(frozen_sids[0])
                    if thawed_sids:
                        random.shuffle(thawed_sids)
                        test_sids.append(thawed_sids[0])

            # Use students with all different note sources
            if opts.get('notes'):
                app.logger.info('Running tests using students with notes')
                sids = nessie_utils.get_all_student_sids()

                asc_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.ASC)
                asc_sids = list(set(sids) & set(asc_sids))
                app.logger.info(f'There are {len(asc_sids)} students with ASC notes')

                boa_sids = boa_utils.get_sids_with_notes_of_src_boa()
                boa_sids = list(set(sids) & set(boa_sids))
                app.logger.info(f'There are {len(boa_sids)} students with BOA notes')

                data_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.DATA)
                data_sids = list(set(sids) & set(data_sids))
                app.logger.info(f'There are {len(data_sids)} students with Data Science notes')

                e_form_sids = nessie_timeline_utils.get_sids_with_e_forms()
                e_form_sids = list(set(sids) & set(e_form_sids))
                app.logger.info(f'There are {len(e_form_sids)} students with eForms')

                ei_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.E_AND_I)
                ei_sids = list(set(sids) & set(ei_sids))
                app.logger.info(f'There are {len(ei_sids)} students with E&I notes')

                eop_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.EOP, eop_private=True)
                eop_sids = list(set(sids) & set(eop_sids))
                app.logger.info(f'There are {len(eop_sids)} students with EOP notes')

                history_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.HISTORY)
                history_sids = list(set(sids) & set(history_sids))
                app.logger.info(f'There are {len(history_sids)} students with History notes')

                sis_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.SIS)
                sis_sids = list(set(sids) & set(sis_sids))
                app.logger.info(f'There are {len(sis_sids)} students with SIS notes that have attachments')

                for sid_list in [asc_sids, boa_sids, data_sids, e_form_sids, ei_sids, eop_sids, history_sids, sis_sids]:
                    random.shuffle(sid_list)
                    test_sids.extend(sid_list[:count])

            # Use students with different academic standing, one student for each
            if opts.get('standing'):
                app.logger.info('Running tests using students with various standing')
                for standing in AcademicStandings:
                    standing_sids = nessie_utils.get_sids_with_standing(standing, self.term())
                    if standing_sids:
                        random.shuffle(standing_sids)
                        test_sids.append(standing_sids[0])

        # By default, run tests against a combo of active and inactive students
        else:
            app.logger.info('Running tests using a random set of students')
            active = []
            inactive = []
            for s in self.students:
                active.append(s) if s.status == 'active' else inactive.append(s)
            random.shuffle(active)
            random.shuffle(inactive)
            test_sids.extend(list(map(lambda st: st.sid, active[:count])))
            test_sids.extend(list(map(lambda st: st.sid, inactive[:count])))

        if test_sids:
            app.logger.info(f'Pre-de-duped SIDs {test_sids}')
            students_to_add = list(filter(lambda st: st.sid in test_sids, self.students))
            self.test_students.extend(students_to_add)

        app.logger.info(f'Test UIDs: {list(map(lambda u: u.uid, self.test_students))}')

    def get_test_student_profiles(self, students=None):
        students = students or self.test_students
        nessie_utils.set_student_profiles(students)

    def get_test_student_enrollments(self, students=None):
        students = students or self.test_students
        nessie_utils.set_student_term_enrollments(students)

    def set_search_cohorts(self, opts):
        test_data = utils.parse_test_data()
        self.searches = []
        if opts.get('students') and opts['students']:
            data = test_data['filters']['students']
        elif opts.get('admits') and opts['admits']:
            data = test_data['filters']['admits']
        else:
            app.logger.error('Unable to determine search cohorts')
            raise

        for test_case in data:
            if opts.get('students') and opts['students']:
                nessie_utils.remove_unavailable_student_cohort_test_data(test_case)
                search_criteria = CohortFilter(test_case, self.dept)
                sids = nessie_filter_students_utils.get_cohort_result(self, search_criteria)
                cohort_members = []
                for student in self.students:
                    if student.sid in sids:
                        cohort_members.append(student)
            else:
                nessie_utils.remove_unavailable_admit_cohort_test_data(test_case)
                search_criteria = CohortAdmitFilter(test_case)
                sids = nessie_filter_admits_utils.get_cohort_result(self, search_criteria)
                cohort_members = []
                for admit in self.admits:
                    if admit.sid in sids:
                        cohort_members.append(admit)
            cohort = FilteredCohort({
                'name': f'Test Cohort {data.index(test_case)} {self.test_id}',
                'members': cohort_members,
                'search_criteria': search_criteria,
            })
            self.searches.append(cohort)

    def set_test_admits(self, count):
        sid_string = os.getenv('SIDS')
        if sid_string:
            sids = sid_string.split()
            self.test_admits = list(filter(lambda st: st.sid in sids, self.admits))
        else:
            random.shuffle(self.admits)
            self.test_admits = self.admits[:count]

    # TODO set_degree_templates

    def set_note_attachments(self):
        attachments = []
        files = os.listdir(utils.attachments_dir())
        for f in files:
            size = os.path.getsize(f'{utils.attachments_dir()}/{f}')
            attachment = NoteAttachment(file_name=f, file_size=size)
            attachments.append(attachment)
        self.attachments = attachments

    # CONFIGURATION FOR SPECIFIC TEST SCRIPTS

    def class_pages(self):
        self.set_base_configs(opts={'include_inactive': True})
        self.set_test_students(count=app.config['MAX_CLASS_PAGE_STUDENTS_COUNT'], opts={'enrollments': True})

        # Generate test cases for parameterized tests
        nessie_utils.set_student_profiles(self.test_students)
        nessie_utils.set_student_term_enrollments(self.test_students)
        for student in self.test_students:
            for term_data in student.enrollment_data.enrollment_terms()[0:2]:
                term = Term({
                    'name': student.enrollment_data.term_name(term_data),
                    'sis_id': student.enrollment_data.term_id(term_data),
                })
                section_ids = []
                for course_data in student.enrollment_data.courses(term_data):
                    for section_data in student.enrollment_data.sections(course_data):
                        section_ids.append(student.enrollment_data.sis_section_data(section_data)['ccn'])
                if section_ids:
                    sections = nessie_utils.get_sections(term, section_ids, primary_only=True)
                    for section in sections:
                        self.test_cases.append(BEATestCase(student=student,
                                                           section=section))

    def curated_groups(self):
        self.set_base_configs(opts={'include_inactive': True})
        self.set_default_cohort(opts={'include_inactive': True})
        self.set_test_students(count=50)
        self.get_test_student_enrollments(self.default_cohort.members)

    def filtered_admits(self):
        self.set_dept(Department.ZCEEE)
        self.set_advisor()
        self.set_admits()
        nessie_utils.get_admits_data(self.admits)
        self.set_search_cohorts(opts={'admits': True})

    def filtered_cohorts(self):
        self.set_base_configs(dept=Department.ADMIN, opts={'include_inactive': True})
        self.set_search_cohorts({'students': True})

        # Set a default cohort to exercise editing and removing filters
        if self.dept == Department.COE:
            colleges = [{'college': 'Undergrad Engineering'}]
        else:
            colleges = [{'college': 'Undergrad Letters & Science'}]
        coe_advisor = boa_utils.get_dept_advisors(Department.COE)[0]
        filters = {
            'colleges': colleges,
            'holds': True,
            'coe_advisors': [{'advisor': coe_advisor.uid}],
        }
        editing_test_search_criteria = CohortFilter(filters, self.dept)
        self.default_cohort = FilteredCohort({
            'name': f'Default cohort {self.test_id}',
            'search_criteria': editing_test_search_criteria,
        })

    def note_mgmt(self):
        self.set_note_attachments()
        self.set_base_configs()

    def search_admits(self):
        self.set_dept(dept=Department.ZCEEE)
        self.set_advisor()
        self.set_admits()
        self.set_test_admits(count=app.config['MAX_SEARCH_STUDENTS_COUNT'])
        self.set_search_cohorts(opts={'admits': True})

    def search_class(self):
        self.set_base_configs()
        self.set_test_students(count=app.config['MAX_SEARCH_STUDENTS_COUNT'], opts={'with_enrollments': True})
        self.get_test_student_enrollments()

    def search_students(self):
        self.set_base_configs()
        self.set_test_students(count=app.config['MAX_SEARCH_STUDENTS_COUNT'])

    def sis_admit_data(self):
        self.set_dept(Department.ZCEEE)
        self.set_advisor()
        self.set_admits()
        self.set_test_admits(count=app.config['MAX_SIS_DATA_STUDENTS_COUNT'])
        nessie_utils.get_admits_data(self.test_admits)
        for admit in self.test_admits:
            self.test_cases.append(BEATestCase(student=admit,
                                               test_case_id=f'{admit.sid}'))

    def sis_student_data(self):
        self.set_base_configs(opts={'include_inactive': True})
        self.set_test_students(count=app.config['MAX_SIS_DATA_STUDENTS_COUNT'],
                               opts={
                                   'include_inactive': True,
                                   'incomplete_grades': True,
                                   'with_standing': True},
                               )
        # Generate test cases for parameterized tests
        nessie_utils.set_student_profiles(self.test_students)
        nessie_utils.set_student_academic_standings(self.test_students)
        nessie_utils.set_student_term_enrollments(self.test_students)

        for student in self.test_students:
            # Tests for student profile data
            self.test_cases.append(BEATestCase(student=student))

            for term_data in student.enrollment_data.enrollment_terms():
                term_sis_id = student.enrollment_data.term_id(term_data)
                term_test_case_id = f'UID {student.uid} {term_sis_id}'
                # Tests for student term data
                self.test_cases.append(BEATestCase(student=student,
                                                   term=term_data,
                                                   term_sis_id=term_sis_id,
                                                   test_case_id=term_test_case_id))

                for course_data in student.enrollment_data.courses(term_data):
                    course_code = student.enrollment_data.course_code(course_data)
                    course_test_case_id = f'UID {student.uid} {term_sis_id} {course_code}'
                    sections_data = student.enrollment_data.sections(course_data)
                    primary_section_id = utils.safe_key(student.enrollment_data.course_primary_section(course_data), 'ccn')
                    # Tests for student course data
                    self.test_cases.append(BEATestCase(student=student,
                                                       course=course_data,
                                                       section=sections_data,
                                                       section_id=primary_section_id,
                                                       term=term_data,
                                                       term_sis_id=term_sis_id,
                                                       test_case_id=course_test_case_id))
