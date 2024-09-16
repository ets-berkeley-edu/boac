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

import re

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.test_utils import boa_utils
from bea.test_utils import nessie_timeline_utils
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.sis_student_data()
tcs = [test_case for test_case in test.test_cases if not test_case.term and not test_case.course]


@pytest.mark.usefixtures('page_objects')
class TestCreateGroup:

    def test_login(self):
        self.homepage.dev_auth(test.advisor)

    def test_create_group(self):
        group = Cohort({'name': f'SIS Student Profile {test.test_id}'})
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(group, [tc.student for tc in tcs])
        self.curated_students_page.wait_for_sidebar_group(group)
        self.curated_students_page.when_visible(self.curated_students_page.group_name_heading_loc(group),
                                                utils.get_medium_timeout())
        self.curated_students_page.wait_for_players()


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('tc', tcs, ids=[f'UID {tc.student.uid}' for tc in tcs], scope='class')
class TestListViewProfileData:

    def test_student(self, tc):
        self.curated_students_page.when_present(self.curated_students_page.student_link_loc(tc.student),
                                                utils.get_short_timeout())

    def test_level(self, tc):
        visible_level = self.curated_students_page.level(tc.student)
        if tc.student.profile_data.academic_career_status() == 'Completed':
            utils.assert_equivalence(visible_level, None)
        else:
            utils.assert_equivalence(visible_level, tc.student.profile_data.level())

    def test_entered_term(self, tc):
        visible_entered_term = self.curated_students_page.entered_term(tc.student)
        if tc.student.profile_data.entered_term():
            utils.assert_equivalence(visible_entered_term, tc.student.profile_data.entered_term())
        else:
            utils.assert_equivalence(visible_entered_term, None)

    def test_graduation(self, tc):
        grads = tc.student.profile_data.graduations()
        visible_graduation = self.curated_students_page.graduation(tc.student)
        if tc.student.profile_data.academic_career_status() == 'Completed' and grads:
            grads.sort(key=lambda g: g['date'], reverse=True)
            latest_grad = grads[0]
            utils.assert_actual_includes_expected(visible_graduation, latest_grad['date'].strftime('%b %-d, %Y'))
            for major in latest_grad['majors']:
                utils.assert_actual_includes_expected(visible_graduation, major['plan'])
            for minor in latest_grad['minors']:
                assert minor['plan'] not in visible_graduation
        else:
            assert not visible_graduation

    def test_inactive(self, tc):
        is_visibly_inactive = self.curated_students_page.inactive_flag(tc.student)
        if tc.student.profile_data.academic_career_status() == 'Inactive':
            assert is_visibly_inactive
        else:
            assert not is_visibly_inactive

    def test_withdrawal(self, tc):
        withdrawal = tc.student.profile_data.withdrawal()
        if withdrawal:
            visible_withdrawal_msg = self.curated_students_page.cxl_msg(tc.student)
            assert visible_withdrawal_msg
            if visible_withdrawal_msg:
                utils.assert_actual_includes_expected(visible_withdrawal_msg, withdrawal['desc'])
                utils.assert_actual_includes_expected(visible_withdrawal_msg, withdrawal['date'])

    def test_academic_standing(self, tc):
        standings = tc.student.academic_standings
        visible_standing = self.curated_students_page.academic_standing(tc.student)
        if standings:
            standings.sort(key=lambda s: s.term.sis_id, reverse=True)
            latest_standing = standings[0]
            if latest_standing.code == 'GST':
                utils.assert_equivalence(visible_standing, None)
            else:
                expected_standing = f'{latest_standing.descrip} ({latest_standing.term.name})'
                utils.assert_equivalence(visible_standing, expected_standing)
        else:
            utils.assert_equivalence(visible_standing, None)

    def test_majors(self, tc):
        active_major_data = [m for m in tc.student.profile_data.majors() if m['active']]
        majors = list(map(lambda maj: maj['major'], active_major_data))
        visible_majors = self.curated_students_page.majors(tc.student)
        if majors:
            utils.assert_equivalence(visible_majors, majors)
        else:
            utils.assert_equivalence(visible_majors, [])

    # TODO - sub-plans?

    def test_expected_graduation(self, tc):
        visible_expected_grad = self.curated_students_page.grad_term(tc.student)
        if tc.student.profile_data.academic_career_status() == 'Completed':
            utils.assert_equivalence(visible_expected_grad, None)
        else:
            utils.assert_equivalence(visible_expected_grad, tc.student.profile_data.expected_grad_term_name())

    def test_cumulative_gpa(self, tc):
        assert self.curated_students_page.gpa(tc.student) in tc.student.profile_data.cumulative_gpa()

    # TODO - most recent term GPA

    def test_cumulative_units(self, tc):
        cumulative_units = tc.student.profile_data.cumulative_units()
        visible_units = self.curated_students_page.cumulative_units(tc.student)
        if cumulative_units:
            utils.assert_equivalence(visible_units, cumulative_units)
        else:
            utils.assert_equivalence(visible_units, '0')


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('tc', tcs, ids=[f'UID {tc.student.uid}' for tc in tcs], scope='class')
class TestStudentPageProfileData:

    def test_load_student_page(self, tc):
        self.student_page.load_page(tc.student)
        self.student_page.expand_personal_details()

    def test_name(self, tc):
        utils.assert_equivalence(self.student_page.name(), tc.student.full_name)

    def test_email(self, tc):
        utils.assert_equivalence(self.student_page.email(), tc.student.profile_data.email())

    def test_email_alternate(self, tc):
        utils.assert_equivalence(self.student_page.email_alternate(), tc.student.profile_data.email_alternate())

    def test_cumulative_units(self, tc):
        cumulative_units = tc.student.profile_data.cumulative_units()
        visible_units = self.student_page.cumulative_units()
        if cumulative_units and cumulative_units != 0:
            utils.assert_equivalence(visible_units, cumulative_units)
        else:
            utils.assert_equivalence(visible_units.replace('No data', '').strip(), '--')

    def test_phone(self, tc):
        utils.assert_equivalence(self.student_page.phone(), tc.student.profile_data.phone())

    def test_cumulative_gpa(self, tc):
        assert self.student_page.cumulative_gpa() in tc.student.profile_data.cumulative_gpa()

    def test_active_majors(self, tc):
        utils.assert_equivalence(self.student_page.majors(), tc.student.profile_data.majors_active())
        utils.assert_equivalence(self.student_page.colleges(), tc.student.profile_data.colleges_active())

    def test_discontinued_majors(self, tc):
        visible_discontinued_majors = self.student_page.majors_discontinued()
        visible_discontinued_colleges = self.student_page.colleges_discontinued()
        if tc.student.profile_data.academic_career_status() == 'Completed':
            assert not visible_discontinued_majors
            assert not visible_discontinued_colleges
        else:
            utils.assert_equivalence(visible_discontinued_majors, tc.student.profile_data.majors_discontinued())
            utils.assert_equivalence(visible_discontinued_colleges, tc.student.profile_data.colleges_discontinued())

    def test_minors(self, tc):
        visible_active_minors = self.student_page.minors()
        visible_discontinued_minors = self.student_page.minors_discontinued()
        if tc.student.profile_data.academic_career_status() == 'Completed':
            assert not visible_active_minors
            assert not visible_discontinued_minors
        else:
            utils.assert_equivalence(visible_active_minors, tc.student.profile_data.minors_active())
            utils.assert_equivalence(visible_discontinued_minors, tc.student.profile_data.minors_discontinued())

    def test_advisor_plans(self, tc):
        utils.assert_equivalence(self.student_page.advisor_plans(), tc.student.profile_data.advisor_plans())

    def test_advisor_names(self, tc):
        expected_names = tc.student.profile_data.advisor_names()
        visible_names = self.student_page.advisor_names()
        for name in expected_names:
            utils.assert_actual_includes_expected(visible_names, name)

    def test_advisor_emails(self, tc):
        expected_emails = tc.student.profile_data.advisor_emails()
        visible_emails = self.student_page.advisor_emails()
        for email in expected_emails:
            utils.assert_actual_includes_expected(visible_emails, email)

    def test_entered_term(self, tc):
        utils.assert_equivalence(self.student_page.entered_term(), tc.student.profile_data.entered_term())

    def test_intended_majors(self, tc):
        if tc.student.profile_data.academic_career() and tc.student.profile_data.academic_career() != 'UGRD':
            utils.assert_equivalence(self.student_page.intended_majors(), [])
        elif tc.student.profile_data.intended_majors():
            utils.assert_equivalence(self.student_page.intended_majors(), tc.student.profile_data.intended_majors())

    def test_visa_status(self, tc):
        demo = tc.student.profile_data.demographics()
        if demo and demo['visa'] and demo['visa']['status'] == 'G':
            visa_type = demo['visa']['type']
            if visa_type == 'F1':
                expected = 'F-1 International Student'
            elif visa_type == 'J1':
                expected = 'J-1 International Student'
            elif visa_type == 'PR':
                expected = 'PR Verified International Student'
            else:
                expected = 'Other Verified International Student'
            utils.assert_equivalence(self.student_page.visa(), expected)
        else:
            utils.assert_equivalence(self.student_page.visa(), None)

    def test_graduation_majors(self, tc):
        if tc.student.profile_data.academic_career_status() == 'Completed':
            for grad in tc.student.profile_data.graduations():
                for maj in grad['majors']:
                    visible_degree = self.student_page.degree(maj['plan'])
                    utils.assert_actual_includes_expected(visible_degree['deg_type'], maj['plan'])
                    utils.assert_equivalence(visible_degree['deg_date'], f"Awarded {grad['date'].strftime('%b %-d, %Y')}")
                    utils.assert_equivalence(visible_degree['deg_college'], maj['college'])

    def test_graduation_minors(self, tc):
        if tc.student.profile_data.academic_career_status() == 'Completed':
            for grad in tc.student.profile_data.graduations():
                for minor in grad['minors']:
                    visible_minor = self.student_page.degree_minor(minor['plan'])
                    utils.assert_actual_includes_expected(visible_minor['min_type'], minor['plan'])
                    utils.assert_equivalence(visible_minor['min_date'], f"Awarded {grad['date'].strftime('%b %d, %Y')}")

    def test_inactive_status(self, tc):
        if tc.student.profile_data.academic_career_status() == 'Inactive':
            assert self.student_page.is_inactive()
        else:
            assert not self.student_page.is_inactive()

    def test_academic_standing(self, tc):
        standings = tc.student.academic_standings
        visible_standing = self.student_page.academic_standing()
        if standings:
            standings.sort(key=lambda s: s.term.sis_id, reverse=True)
            latest_standing = standings[0]
            if latest_standing.code == 'GST':
                utils.assert_equivalence(visible_standing, None)
            else:
                expected_standing = f'{latest_standing.descrip} ({latest_standing.term.name})'
                utils.assert_equivalence(visible_standing, expected_standing)
        else:
            utils.assert_equivalence(visible_standing, None)

    def test_terms_in_attendance(self, tc):
        term_count = tc.student.profile_data.terms_in_attendance()
        visible_term_count = self.student_page.terms_in_attendance()
        if term_count and tc.student.profile_data.level() != 'Graduate':
            utils.assert_equivalence(visible_term_count, term_count)
        else:
            utils.assert_equivalence(visible_term_count, None)

    def test_transfer(self, tc):
        visible_transfer = self.student_page.transfer()
        if tc.student.profile_data.transfer():
            utils.assert_equivalence(visible_transfer, 'Transfer')
        else:
            utils.assert_equivalence(visible_transfer, None)

    def test_expected_graduation(self, tc):
        level = tc.student.profile_data.level()
        visible_expected_grad = self.student_page.expected_graduation()
        if level in ['Doctoral Candidate', 'Graduate', 'Masters/Professional']:
            utils.assert_equivalence(visible_expected_grad, None)
        else:
            utils.assert_equivalence(visible_expected_grad, tc.student.profile_data.expected_grad_term_name())

    def test_timeline_reqts(self, tc):
        reqts = tc.student.profile_data.degree_progress()
        if reqts:
            utils.assert_equivalence(self.student_page.visible_writing_reqt(), reqts['writing'])
            utils.assert_equivalence(self.student_page.visible_history_reqt(), reqts['history'])
            utils.assert_equivalence(self.student_page.visible_institutions_reqt(), reqts['institutions'])
            utils.assert_equivalence(self.student_page.visible_cultures_reqt(), reqts['cultures'])
        else:
            utils.assert_equivalence(self.student_page.visible_writing_reqt(), None)
            utils.assert_equivalence(self.student_page.visible_history_reqt(), None)
            utils.assert_equivalence(self.student_page.visible_institutions_reqt(), None)
            utils.assert_equivalence(self.student_page.visible_cultures_reqt(), None)

    def test_timeline_alerts(self, tc):
        alerts = boa_utils.get_students_alerts([tc.student])
        alert_data = [{'text': a.message, 'date': self.student_page.expected_item_short_date_format(a.date)} for a in alerts]
        visible_alerts = self.student_page.visible_alerts()
        if alerts:
            visible_alerts.sort(key=lambda a: a['date'])
            alert_data.sort(key=lambda a: a['date'])
            utils.assert_equivalence(visible_alerts, alert_data)

        standings = tc.student.academic_standings
        if standings:
            standings.sort(key=lambda s: s.term.sis_id, reverse=True)
            latest_standing = standings[0]
            standing_alert_msg = f"Student's academic standing is '{latest_standing.descrip}'."
            visible_alert_msgs = [a['text'] for a in visible_alerts]
            if latest_standing.code == 'GST' or not latest_standing.code:
                assert standing_alert_msg not in visible_alert_msgs
            else:
                assert standing_alert_msg in visible_alert_msgs

    def test_timeline_holds(self, tc):
        holds = nessie_timeline_utils.get_student_holds(tc.student)
        hold_msgs = [re.sub('\W', '', h.message) for h in holds]
        hold_msgs.sort()
        visible_holds = self.student_page.visible_holds()
        visible_holds.sort()
        utils.assert_equivalence(visible_holds, hold_msgs)
