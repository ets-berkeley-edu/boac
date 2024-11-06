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

from bea.config.bea_test_base_configs import BEATestBaseConfigs
from bea.config.bea_test_case import BEATestCase
from bea.models.cohorts_and_groups.cohort_filter import CohortFilter
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.models.department import Department
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.term import Term
from bea.test_utils import boa_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app


class BEATestConfig(BEATestBaseConfigs):

    def appts_content(self):
        limit = app.config['MAX_NOTES_OR_APPTS_STUDENTS_COUNT']
        self.set_base_configs(opts={'include_inactive': True})
        self.set_test_students(count=limit, opts={'appts': True})

        # Generate test cases for parameterized tests
        for student in self.test_students:
            # Throw out junk SIS appts
            appts = [a for a in nessie_timeline_utils.get_sis_appts(student) if '504GatewayTimeout' not in a.detail][0:limit]
            ycbm_appts = nessie_timeline_utils.get_ycbm_appts(student)[0:limit]
            appts.extend(ycbm_appts)
            for appt in appts:
                self.test_cases.append(BEATestCase(student=student, appt=appt))

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

    def degree_check(self, opts=None):
        self.set_base_configs(dept=Department.COE, opts=opts)
        self.set_read_only_advisor()
        data = {
            'majors': [{'major': app.config['TEST_DEFAULT_COHORT_MAJOR']}],
            'units': [{'unit': '90 - 119'}],
        }
        cohort_filter = CohortFilter(dept=self.dept, data=data)
        self.set_default_cohort(cohort_filter)
        self.set_degree_templates()

    def e_form_content(self):
        self.set_base_configs(opts={'include_inactive': True})
        self.set_test_students(count=app.config['MAX_NOTES_OR_APPTS_STUDENTS_COUNT'], opts={'e_forms': True})
        for student in self.test_students:
            e_forms = nessie_timeline_utils.get_e_form_notes(student)
            # Tests for the list view of e-forms
            self.test_cases.append(BEATestCase(student=student,
                                               note=e_forms,
                                               test_case_id=f'UID {student.uid}'))
            # Tests for a sample of e-form detail
            for e_form in e_forms[:app.config['MAX_NOTES_OR_APPTS_COUNT']]:
                self.test_cases.append(BEATestCase(student=student,
                                                   note=e_form,
                                                   test_case_id=f'UID {student.uid} {e_form.record_id}'))

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

    def note_batch(self):
        self.set_note_attachments()
        self.set_base_configs()
        self.set_default_cohort()

    def note_content(self):
        self.set_base_configs(opts={'include_inactive': True})
        self.set_test_students(count=app.config['MAX_NOTES_OR_APPTS_STUDENTS_COUNT'],
                               opts={'notes': True, 'inactive': True})
        for student in self.test_students:
            all_notes, sample_notes = self.get_test_notes(student, app.config['MAX_NOTES_OR_APPTS_COUNT'])
            # Tests for the list view all a student's notes
            self.test_cases.append(BEATestCase(student=student,
                                               note=all_notes,
                                               test_case_id=f'UID {student.uid}'))
            # Tests for a representative sample of notes in more detail
            for note in sample_notes:
                source = note.source.value['schema'] if note.source else 'BOA'
                if note.subject and 'QA Test' in note.subject:
                    app.logger.info(f'Skipping note {note.record_id} because it is a testing artifact')
                else:
                    self.test_cases.append(BEATestCase(student=student,
                                                       note=note,
                                                       test_case_id=f'UID {student.uid} {source} {note.record_id}'))

    def note_draft(self):
        self.set_base_configs(dept=Department.ZCEEE)
        self.set_default_cohort()
        self.set_note_attachments()
        self.set_test_students(count=100, opts={'notes': True})
        boa_notes_sids = boa_utils.get_sids_with_notes_of_src_boa()
        self.test_students = [s for s in self.test_students if s.sid in boa_notes_sids]

    def note_mgmt(self):
        self.set_note_attachments()
        self.set_base_configs()

    def note_template(self):
        self.set_base_configs()
        self.set_default_cohort()
        self.set_note_attachments()

    def search_admits(self):
        self.set_dept(dept=Department.ZCEEE)
        self.set_advisor()
        self.set_admits()
        self.set_test_admits(count=app.config['MAX_SEARCH_STUDENTS_COUNT'])
        self.set_search_cohorts(opts={'admits': True})

    def search_appts(self):
        self.set_base_configs(opts={'include_inactive': True})
        self.set_test_students(count=app.config['MAX_SEARCH_STUDENTS_COUNT'],
                               opts={'appts': True, 'inactive': True})

        count = app.config['MAX_NOTES_OR_APPTS_COUNT']
        all_appts = []
        for student in self.test_students:
            all_student_appts = nessie_timeline_utils.get_sis_appts(student)
            for student_appt in all_student_appts:
                # Throw out junk SIS appts
                if '504GatewayTimeout' not in student_appt.detail:
                    all_appts.append(student_appt)

        test_cases = []
        for appt in all_appts:
            search_string = boa_utils.generate_appt_search_query(appt)
            if search_string:
                test_case_id = f'UID {appt.student.uid} SIS {search_string}'
                test_cases.append(BEATestCase(student=appt.student,
                                              appt=appt,
                                              search_string=search_string,
                                              test_case_id=test_case_id))

        self.test_cases = test_cases[:count]
        for tc in self.test_cases:
            app.logger.info(f"Test case: {tc.test_case_id}, '{tc.search_string}'")

    def search_class(self):
        self.set_base_configs()
        self.set_test_students(count=app.config['MAX_SEARCH_STUDENTS_COUNT'], opts={'enrollments': True})
        self.get_test_student_enrollments()

    def search_notes(self):
        self.set_base_configs(dept=Department.ZCEEE, opts={'include_inactive': True})
        self.set_test_students(count=app.config['MAX_SEARCH_STUDENTS_COUNT'],
                               opts={'notes': True, 'inactive': True, 'private': False})

        all_notes = []
        count = app.config['MAX_NOTES_OR_APPTS_COUNT']
        for student in self.test_students:
            all_student_notes, _ = self.get_test_notes(student, count)
            for student_note in all_student_notes:
                if student_note.subject and 'QA Test' in student_note.subject:
                    app.logger.info(f'Skipping note {student_note.record_id} because it is a testing artifact')
                else:
                    all_notes.append(student_note)

        test_cases = []
        for note in all_notes:
            search_string = boa_utils.generate_note_search_query(note)
            if search_string:
                test_case_id = f"UID {note.student.uid} {note.source.value['name']} {note.record_id}"
                test_cases.append(BEATestCase(student=note.student,
                                              note=note,
                                              search_string=search_string,
                                              test_case_id=test_case_id))

        sources = list(set(TimelineRecordSource) - {TimelineRecordSource.E_FORM, TimelineRecordSource.YCBM})
        for source in sources:
            source_notes = [tc for tc in test_cases if tc.note.source == source]
            self.test_cases.extend(source_notes[:count])
        for tc in self.test_cases:
            app.logger.info(f"Test case: {tc.test_case_id}, '{tc.search_string}'")

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

    def user_role_admin(self):
        self.set_base_configs(dept=Department.ADMIN)
        self.set_search_cohorts(opts={'students': True})
