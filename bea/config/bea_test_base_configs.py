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

from bea.models.academic_standings import AcademicStandings
from bea.models.advisor_role import AdvisorRole
from bea.models.cohorts_and_groups.cohort_admit_filter import CohortAdmitFilter
from bea.models.cohorts_and_groups.cohort_filter import CohortFilter
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.models.degree_progress.degree_check_template import DegreeCheckTemplate
from bea.models.degree_progress.degree_reqt_category import DegreeReqtCategory
from bea.models.degree_progress.degree_reqt_course import DegreeReqtCourse
from bea.models.degree_progress.degree_reqt_units import DegreeReqtUnits
from bea.models.department import Department
from bea.models.department_membership import DepartmentMembership
from bea.models.incomplete_grades import IncompleteGrades
from bea.models.notes_and_appts.note_attachment import NoteAttachment
from bea.models.notes_and_appts.timeline_record_source import TimelineRecordSource
from bea.models.user import User
from bea.test_utils import boa_utils
from bea.test_utils import nessie_filter_admits_utils
from bea.test_utils import nessie_filter_students_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app


class BEATestBaseConfigs(object):

    def __init__(self, data=None, dept=None):
        self.data = data or {}
        self.dept = dept or Department.L_AND_S
        self.test_admits = []
        self.test_cases = []
        self.test_id = f'{calendar.timegm(dt.now().timetuple())}'
        self.test_students = []

    @property
    def admin(self):
        return self.data.get('admin')

    @admin.setter
    def admin(self, value):
        self.data['admin'] = value

    @property
    def admits(self):
        return self.data.get('admits')

    @admits.setter
    def admits(self, value):
        self.data['admits'] = value

    @property
    def advisor(self):
        return self.data.get('advisor')

    @advisor.setter
    def advisor(self, value):
        self.data['advisor'] = value

    @property
    def advisor_read_only(self):
        return self.data.get('advisor_read_only')

    @advisor_read_only.setter
    def advisor_read_only(self, value):
        self.data['advisor_read_only'] = value

    @property
    def attachments(self):
        return self.data.get('attachments')

    @attachments.setter
    def attachments(self, value):
        self.data['attachments'] = value

    @property
    def default_cohort(self):
        return self.data.get('cohort')

    @default_cohort.setter
    def default_cohort(self, value):
        self.data['cohort'] = value

    @property
    def degree_templates(self):
        return self.data.get('degree_templates')

    @degree_templates.setter
    def degree_templates(self, value):
        self.data['degree_templates'] = value

    @property
    def dept(self):
        return self.data.get('dept')

    @dept.setter
    def dept(self, value):
        self.data['dept'] = value

    @property
    def searches(self):
        return self.data.get('searches')

    @searches.setter
    def searches(self, value):
        self.data['searches'] = value

    @property
    def students(self):
        return self.data.get('students')

    @students.setter
    def students(self, value):
        self.data['students'] = value

    @property
    def term(self):
        return self.data.get('term')

    @term.setter
    def term(self, value):
        self.data['term'] = value

    # BASE CONFIGS FOR ALL TESTS

    def set_dept(self, dept=None):
        self.dept = dept or Department.L_AND_S

    def set_admin(self):
        self.admin = User({
            'depts': [Department.ADMIN],
            'is_admin': True,
            'uid': utils.get_admin_uid(),
            'username': utils.get_admin_username(),
        })

    def set_advisor(self, uid=None):
        role = DepartmentMembership(advisor_role=AdvisorRole.ADVISOR,
                                    dept=self.dept,
                                    is_automated=None)
        boa_advisors = boa_utils.get_dept_advisors(self.dept, role)
        boa_advisors.reverse()
        if self.dept == Department.ADMIN:
            self.set_admin()
            boa_advisor = self.admin
        elif uid:
            boa_advisor = next(filter(lambda a: a.uid == uid, boa_advisors))
        else:
            boa_advisor = next(
                filter(lambda a: a.depts == [self.dept] and a.can_access_advising_data and a.can_access_canvas_data,
                       boa_advisors))

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
                nessie_advisor = nessie_timeline_utils.get_advising_note_author(self.advisor_read_only.uid)
                if nessie_advisor:
                    self.advisor_read_only.sid = nessie_advisor.sid
                    self.advisor_read_only.first_name = nessie_advisor.first_name
                    self.advisor_read_only.last_name = nessie_advisor.last_name
                break

    @staticmethod
    def get_no_canvas_advisor():
        users = boa_utils.get_authorized_users()
        return next(filter(
            lambda a: len(a.depts) == 1 and a.can_access_advising_data and not a.can_access_canvas_data and a.active,
            users))

    @staticmethod
    def get_no_canvas_no_notes_advisor():
        users = boa_utils.get_authorized_users()
        return next(filter(
            lambda a: len(
                a.depts) == 1 and not a.can_access_advising_data and not a.can_access_canvas_data and a.active,
            users))

    def set_students(self, students=None, opts=None):
        self.students = students or nessie_utils.get_all_students(opts)
        if opts and opts.get('include_inactive'):
            app.logger.info('Pool of test students will include inactive students')
        else:
            self.students = [s for s in self.students if s.status == 'active']

    def set_base_configs(self, dept=None, opts=None):
        self.term = utils.get_current_term()
        self.set_dept(dept)
        self.set_admin()
        self.set_advisor()
        self.set_students(opts=opts)

    # TEST STUDENT CONFIGS

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

            # Use students with e-forms
            if opts.get('e_forms'):
                app.logger.info('Running tests using students with e-forms')
                sids = nessie_utils.get_all_student_sids()
                e_form_sids = nessie_timeline_utils.get_sids_with_e_forms()
                e_form_sids = list(set(sids) & set(e_form_sids))
                app.logger.info(f'There are {len(e_form_sids)} students with eForms')
                random.shuffle(e_form_sids)
                test_sids.extend(e_form_sids[:count])

            # Use students with enrollments in the current term
            if opts.get('enrollments'):
                term_sis_id = opts['enrollment_term'] if opts.get('enrollment_term') else self.term.sis_id
                app.logger.info('Running tests using students with enrollments')
                enrolled_sids = nessie_utils.get_sids_with_enrollments(term_sis_id)
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
                private = opts.get('private') or False
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

                ei_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.E_AND_I)
                ei_sids = list(set(sids) & set(ei_sids))
                app.logger.info(f'There are {len(ei_sids)} students with E&I notes')

                eop_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.EOP,
                                                                            eop_private=private)
                eop_sids = list(set(sids) & set(eop_sids))
                app.logger.info(f'There are {len(eop_sids)} students with EOP notes')

                history_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.HISTORY)
                history_sids = list(set(sids) & set(history_sids))
                app.logger.info(f'There are {len(history_sids)} students with History notes')

                sis_sids = nessie_timeline_utils.get_sids_with_notes_of_src(TimelineRecordSource.SIS)
                sis_sids = list(set(sids) & set(sis_sids))
                app.logger.info(f'There are {len(sis_sids)} students with SIS notes that have attachments')

                for sid_list in [asc_sids, boa_sids, data_sids, ei_sids, eop_sids, history_sids, sis_sids]:
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
            for st in self.students:
                if st.sid in test_sids:
                    self.test_students.append(st)

        app.logger.info(f'Test UIDs: {list(map(lambda u: u.uid, self.test_students))}')

    def get_test_student_profiles(self, students=None):
        students = students or self.test_students
        nessie_utils.set_student_profiles(students)

    def get_test_student_enrollments(self, students=None):
        students = students or self.test_students
        nessie_utils.set_student_term_enrollments(students)

    # TEST COHORT CONFIGS

    def set_default_cohort(self, cohort_filter=None, opts=None):
        if not cohort_filter:
            if opts:
                if opts.get('include_inactive'):
                    data = {
                        'intended_majors': [{'major': app.config['TEST_DEFAULT_COHORT_MAJOR']}],
                        'career_statuses': [{'status': 'Active'}, {'status': 'Inactive'}],
                    }
                elif opts.get('major'):
                    data = {
                        'majors': [{'major': opts['major']}],
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

    # TEST ADMIT CONFIGS

    def set_admits(self):
        self.admits = nessie_utils.get_admits()

    def set_test_admits(self, count):
        sid_string = os.getenv('SIDS')
        if sid_string:
            sids = sid_string.split()
            self.test_admits = list(filter(lambda st: st.sid in sids, self.admits))
        else:
            random.shuffle(self.admits)
            self.test_admits = self.admits[:count]

    # TEST NOTES CONFIGS

    def get_test_notes(self, student, count):
        asc_notes = nessie_timeline_utils.get_asc_notes(student)
        boa_notes = boa_utils.get_student_notes(student)
        boa_notes = [n for n in boa_notes if not (n.is_draft and n.advisor.uid != self.advisor.uid) or n.is_private]
        data_notes = nessie_timeline_utils.get_data_sci_notes(student)
        ei_notes = nessie_timeline_utils.get_e_and_i_notes(student)
        eop_notes = nessie_timeline_utils.get_eop_notes(student)
        history_notes = nessie_timeline_utils.get_history_notes(student)
        sis_notes = nessie_timeline_utils.get_sis_notes(student)
        all_notes = asc_notes + boa_notes + data_notes + ei_notes + eop_notes + history_notes + sis_notes
        sample_notes = (asc_notes[:count] + boa_notes[:count] + data_notes[:count] + ei_notes[:count]
                        + eop_notes[:count] + history_notes[:count] + sis_notes[:count])
        return all_notes, sample_notes

    def set_note_attachments(self):
        attachments = []
        files = os.listdir(utils.attachments_dir())
        for f in files:
            size = os.path.getsize(f'{utils.attachments_dir()}/{f}')
            attachment = NoteAttachment({
                'file_name': f,
                'file_size': size,
            })
            attachments.append(attachment)
        self.attachments = attachments

    # TEST DEGREE CHECK CONFIGS

    def get_degree_template_category_unit_reqts(self, template, category_data):
        cat_unit_reqts = []
        if category_data.get('unit_reqts'):
            for cat_unit_reqt_data in category_data['unit_reqts']:
                for template_unit_reqt in template.unit_reqts:
                    if template_unit_reqt.name == f"{cat_unit_reqt_data['reqt']} {self.test_id}":
                        cat_unit_reqts.append(template_unit_reqt)
        return cat_unit_reqts

    def get_degree_template_category_course_reqts(self, template, category_data):
        cat_course_reqts = []
        if category_data.get('courses'):
            for cat_course_reqt_data in category_data['courses']:
                cat_course_unit_reqts = []
                if cat_course_reqt_data.get('unit_reqts'):
                    for cat_course_unit_reqt_data in cat_course_reqt_data['unit_reqts']:
                        for template_unit_reqt in template.unit_reqts:
                            if template_unit_reqt.name == f"{cat_course_unit_reqt_data['reqt']} {self.test_id}":
                                cat_course_unit_reqts.append(template_unit_reqt)
                cat_course_reqts.append(DegreeReqtCourse({
                    'name': f"{cat_course_reqt_data['name']} {self.test_id}",
                    'column_num': cat_course_reqt_data.get('column_num'),
                    'is_transfer_course': cat_course_reqt_data.get('is_transfer_course'),
                    'units': cat_course_reqt_data.get('units'),
                    'unit_reqts': cat_course_unit_reqts,
                }))
        return cat_course_reqts

    @staticmethod
    def set_degree_template_inheritance(parent, children):
        for child in children:
            child.parent = parent
            child.column_num = parent.column_num
            child.unit_reqts += [r for r in parent.unit_reqts if r not in child.unit_reqts]

    def set_degree_template_attributes(self, template):
        data = template.data
        template.name = f"{data['name']} {self.test_id}"

        template_unit_reqts = []
        for unit_reqt_data in data['unit_reqts']:
            template_unit_reqts.append(DegreeReqtUnits({
                'name': f"{unit_reqt_data.get('name')} {self.test_id}",
                'unit_count': unit_reqt_data.get('unit_count'),
            }))
        template.unit_reqts = template_unit_reqts

        template_categories = []
        if data.get('categories'):
            for cat_data in data['categories']:
                cat_unit_reqts = self.get_degree_template_category_unit_reqts(template, cat_data)
                cat_course_reqts = self.get_degree_template_category_course_reqts(template, cat_data)

                sub_cats = []
                if cat_data.get('sub_categories'):
                    for sub_cat_data in cat_data['sub_categories']:
                        sub_cat_unit_reqts = self.get_degree_template_category_unit_reqts(template, sub_cat_data)
                        sub_cat_course_reqts = self.get_degree_template_category_course_reqts(template, sub_cat_data)
                        sub_cats.append(DegreeReqtCategory({
                            'name': f"{sub_cat_data.get('name')} {self.test_id}",
                            'desc': sub_cat_data.get('desc'),
                            'column_num': sub_cat_data.get('column_num'),
                            'course_reqts': sub_cat_course_reqts,
                            'unit_reqts': sub_cat_unit_reqts,
                        }))

                template_categories.append(DegreeReqtCategory({
                    'name': f"{cat_data['name']} {self.test_id}",
                    'desc': cat_data.get('desc'),
                    'column_num': cat_data['column_num'],
                    'course_reqts': cat_course_reqts,
                    'sub_categories': sub_cats,
                    'unit_reqts': cat_unit_reqts,
                }))

        for category in template_categories:
            self.set_degree_template_inheritance(category, category.course_reqts)
            self.set_degree_template_inheritance(category, category.sub_categories)
            for sub_category in category.sub_categories:
                self.set_degree_template_inheritance(sub_category, sub_category.course_reqts)
        template.categories = template_categories

    def set_degree_templates(self):
        test_data = utils.parse_test_data()
        templates = []
        for data in test_data['degree_checks']:
            template = DegreeCheckTemplate(data)
            self.set_degree_template_attributes(template)
            templates.append(template)
        self.degree_templates = templates
