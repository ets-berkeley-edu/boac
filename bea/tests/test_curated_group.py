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
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest


@pytest.mark.usefixtures('page_objects')
class TestCuratedGroup:
    test = BEATestConfig()
    test.curated_groups()
    advisor = test.advisor
    pre_existing_cohorts = boa_utils.get_user_filtered_cohorts(advisor)
    pre_existing_groups = boa_utils.get_user_curated_groups(advisor)
    test_student = test.default_cohort.members[0]
    app.logger.info(f'Test student is UID {test_student.uid}')

    group_1 = Cohort({'name': f'Group 1 {test.test_id}'})
    group_2 = Cohort({'name': f'Group 2 {test.test_id}'})
    group_3 = Cohort({'name': f'Group 3 {test.test_id}'})
    group_4 = Cohort({'name': f'Group 4 {test.test_id}'})
    group_5 = Cohort({'name': f'Group 5 {test.test_id}'})
    group_6 = Cohort({'name': f'Group 6 {test.test_id}'})
    group_7 = Cohort({'name': f'Group 7 {test.test_id}'})
    group_8 = Cohort({'name': f'Group 8 {test.test_id}'})
    group_9 = Cohort({'name': f'Group 9 {test.test_id}'})
    advisor_groups = [group_1, group_2, group_3, group_4, group_5, group_6, group_7, group_8]

    def test_get_test_student_enrollment(self):
        self.homepage.dev_auth(self.advisor)

    def test_delete_pre_existing_cohorts(self):
        for c in self.pre_existing_cohorts:
            self.filtered_students_page.load_and_delete_cohort(c)

    def test_create_default_cohort(self):
        self.filtered_students_page.search_and_create_new_student_cohort(self.test.default_cohort)

    def test_delete_pre_existing_groups(self):
        for g in self.pre_existing_groups:
            self.curated_students_page.load_and_delete_group(g)

    def test_create_group_from_cohort_page_group_selector(self):
        group = Cohort({'name': f'Group created from filtered cohort {self.test.test_id}'})
        self.filtered_students_page.load_cohort(self.test.default_cohort)
        self.filtered_students_page.wait_for_student_list()
        sids = self.filtered_students_page.list_view_sids()
        visible_members = list(filter(lambda s: s.sid in sids, self.test.students))
        self.filtered_students_page.select_and_add_members_to_new_grp(visible_members[0:9], group)

    def test_create_group_from_class_page_group_selector(self):
        term = self.test_student.enrollment_data.enrollment_terms()[0]
        term_id = self.test_student.enrollment_data.term_id(term)
        ccn = self.test_student.enrollment_data.course_section_ccns(self.test_student.enrollment_data.courses(term)[0])[0]
        group = Cohort({'name': f'Group created from class page {self.test.test_id}'})
        self.class_page.load_page(term_id, ccn)
        sids = self.class_page.list_view_sids()
        visible_members = list(filter(lambda s: s.sid in sids, self.test.students))
        self.class_page.select_and_add_members_to_new_grp(visible_members[0:9], group)

    def test_create_group_from_search_results_group_selector(self):
        group = Cohort({'name': f'Group created from search results {self.test.test_id}'})
        self.homepage.enter_simple_search_and_hit_enter(self.test_student.sid)
        self.homepage.wait_for_spinner()
        self.search_results_page.select_and_add_members_to_new_grp([self.test_student], group)

    def test_create_group_from_student_page_group_selector(self):
        group = Cohort({'name': f'Group created from student page {self.test.test_id}'})
        self.student_page.load_page(self.test_student)
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.add_members_to_new_grp([self.test_student], group)

    def test_create_group_from_bulk_sids(self):
        students = self.test.students[0:51]
        group = Cohort({'name': f'Group created with bulk SIDs {self.test.test_id}'})
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(group, students)
        self.curated_students_page.wait_for_sidebar_group(group)
        self.curated_students_page.when_visible(self.curated_students_page.group_name_heading_loc(group),
                                                utils.get_medium_timeout())

    def test_group_name_required(self):
        group = Cohort({'name': None})
        self.student_page.load_page(self.test_student)
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.click_create_new_grp(group)
        assert not self.student_page.element(self.student_page.GROUP_SAVE_BUTTON).is_enabled()

    def test_group_name_truncated_255_chars(self):
        self.student_page.cancel_group_if_modal()
        group = Cohort({'name': ('A llooooong title ' * 15)})
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.click_create_new_grp(group)
        self.student_page.enter_group_name(group)
        self.student_page.when_present(self.student_page.NO_CHARS_LEFT_MSG, 1)

    def test_group_name_cannot_match_existing_group_of_same_advisor(self):
        self.student_page.cancel_group_if_modal()
        existing_group = Cohort({'name': f'Existing Group {self.test.test_id}'})
        self.student_page.load_page(self.test_student)
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.add_members_to_new_grp([self.test_student], existing_group)

        new_group = Cohort({'name': existing_group.name})
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.click_create_new_grp(new_group)
        self.student_page.name_and_save_group(new_group)
        self.student_page.when_visible(self.student_page.DUPE_GROUP_NAME_MSG, utils.get_short_timeout())

    def test_group_name_cannot_match_existing_cohort_of_same_advisor(self):
        self.student_page.cancel_group_if_modal()
        new_group = Cohort({'name': self.test.default_cohort.name})
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.click_create_new_grp(new_group)
        self.student_page.name_and_save_group(new_group)
        self.student_page.when_visible(self.student_page.DUPE_FILTERED_NAME_MSG, utils.get_short_timeout())

    def test_group_name_can_match_deleted_group_of_same_advisor(self):
        self.filtered_students_page.cancel_group_if_modal()
        deleted_group = Cohort({'name': f'Deleted Group {self.test.test_id}'})
        self.student_page.load_page(self.test_student)
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.add_members_to_new_grp([self.test_student], deleted_group)
        self.curated_students_page.load_page(deleted_group)
        self.curated_students_page.delete_group(deleted_group)

        new_group = Cohort({'name': deleted_group.name})
        self.student_page.load_page(self.test_student)
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.add_members_to_new_grp([self.test_student], new_group)

    def test_group_name_can_be_changed(self):
        group = boa_utils.get_user_curated_groups(self.advisor)[0]
        self.curated_students_page.load_page(group)
        self.curated_students_page.rename_group(group, f'{group.name} Renamed')

    def test_group_members_can_be_added_from_student_page(self):
        self.test.default_cohort.members.pop(-1)
        self.student_page.load_page(self.test_student)
        for g in self.advisor_groups:
            self.student_page.click_add_to_group_per_student_button(self.test_student)
            self.student_page.add_members_to_new_grp([self.test_student], g)

    def test_group_members_can_be_added_from_cohort_using_select_all(self):
        self.filtered_students_page.load_cohort(self.test.default_cohort)
        self.filtered_students_page.select_and_add_all_visible_to_grp(self.test.students, self.group_1)
        self.curated_students_page.load_page(self.group_1)
        self.curated_students_page.assert_visible_students_match_expected(self.group_1)

    def test_group_members_can_be_added_from_cohort_using_select_some(self):
        self.filtered_students_page.load_cohort(self.test.default_cohort)
        group_uids = list(map(lambda m: m.uid, self.group_2.members))
        visible_uids = self.filtered_students_page.list_view_uids()
        visible_uids = list(set(visible_uids) - set(group_uids))
        self.test.default_cohort.members = list(filter(lambda m: m.uid in visible_uids, self.test.default_cohort.members))

        self.filtered_students_page.select_and_add_members_to_grp(self.test.default_cohort.members[0:-2], self.group_2)
        self.curated_students_page.load_page(self.group_2)
        self.curated_students_page.assert_visible_students_match_expected(self.group_2)

    def test_group_members_can_be_added_from_bulk_add_sids_page(self):
        self.curated_students_page.load_page(self.group_4)
        self.curated_students_page.add_comma_sep_sids_to_existing_grp(self.group_4, self.test.students[-10:])
        visible_sids = self.curated_students_page.visible_sids()
        visible_sids.sort()
        member_sids = list(map(lambda m: m.sid, self.group_4.members))
        member_sids.sort()
        missing_sids = list(set(member_sids) - set(visible_sids))
        # Account for SIDs that have no associated data and will not appear in Boa
        if missing_sids:
            for sid in missing_sids:
                app.logger.info(f'Checking data for missing SID {sid}')
                student = next(filter(lambda m: m.sid == sid, self.group_4.members))
                if not self.test_student.enrollment_data:
                    app.logger.info(f'Removing SID {sid} from the group since the student does not appear in BOA')
                    missing_sids.remove(sid)
                    self.group_4.members.remove(student)
        assert not missing_sids

    def test_group_members_can_be_added_from_class_page_using_select_all(self):
        term = self.test_student.enrollment_data.enrollment_terms()[0]
        term_id = self.test_student.enrollment_data.term_id(term)
        ccn = self.test_student.enrollment_data.course_section_ccns(self.test_student.enrollment_data.courses(term)[0])[0]
        self.class_page.load_page(term_id, ccn)
        self.class_page.select_and_add_all_visible_to_grp(self.test.students, self.group_5)
        self.curated_students_page.load_page(self.group_5)
        self.curated_students_page.assert_visible_students_match_expected(self.group_5)

    def test_group_members_can_be_added_from_class_page_using_select_some(self):
        term = self.test_student.enrollment_data.enrollment_terms()[0]
        term_id = self.test_student.enrollment_data.term_id(term)
        ccn = self.test_student.enrollment_data.course_section_ccns(self.test_student.enrollment_data.courses(term)[0])[0]
        self.class_page.load_page(term_id, ccn)
        self.class_page.select_and_add_members_to_grp([self.test_student], self.group_6)
        self.curated_students_page.load_page(self.group_6)
        self.curated_students_page.assert_visible_students_match_expected(self.group_6)

    def test_group_members_can_be_added_from_search_results_using_select_all(self):
        self.homepage.enter_simple_search_and_hit_enter(self.test_student.first_name)
        self.homepage.wait_for_spinner()
        self.search_results_page.select_and_add_all_students_to_grp(self.test.students, self.group_7)
        self.curated_students_page.load_page(self.group_7)
        self.curated_students_page.assert_visible_students_match_expected(self.group_7)

    def test_group_members_can_be_added_from_search_results_using_select_some(self):
        self.curated_students_page.enter_simple_search_and_hit_enter(self.test_student.sid)
        self.curated_students_page.wait_for_spinner()
        self.search_results_page.select_and_add_students_to_grp([self.test_student], self.group_8)
        self.curated_students_page.load_page(self.group_8)
        self.curated_students_page.assert_visible_students_match_expected(self.group_8)

    def test_group_membership_shown_on_student_page(self):
        self.student_page.load_page(self.group_1.members[0])
        self.student_page.click_add_to_group_per_student_button(self.group_1.members[0])
        assert self.student_page.is_group_selected(self.group_1)

    def test_group_membership_can_be_removed_on_group_page(self):
        self.curated_students_page.load_page(self.group_2)
        student = self.group_2.members[-1]
        app.logger.info(f'Removing UID {student.uid} from group {self.group_2.name}')
        self.curated_students_page.remove_student_by_row_index(self.group_2, student)
        self.curated_students_page.assert_visible_students_match_expected(self.group_2)

    def test_sidebar_group_member_count_incremented_when_member_added(self):
        self.student_page.load_page(self.test_student)
        self.student_page.click_add_to_group_per_student_button(self.test_student)
        self.student_page.add_members_to_new_grp([self.test_student], self.group_9)
        self.student_page.wait_for_sidebar_member_count(self.group_9)

    def test_sidebar_group_member_count_decremented_when_member_removed(self):
        self.curated_students_page.load_page(self.group_9)
        self.curated_students_page.remove_student_by_row_index(self.group_9, self.test_student)
        self.student_page.wait_for_sidebar_member_count(self.group_9)

    def test_group_bulk_add_sids_rejects_malformed_input(self):
        self.curated_students_page.load_page(self.group_4)
        self.curated_students_page.enter_text_in_sids_input('Fiat Lux')
        self.curated_students_page.click_add_sids_to_group_button()
        self.curated_students_page.click_remove_invalid_sids()

    def test_group_bulk_add_sids_rejects_input_not_matching_boa_students(self):
        self.curated_students_page.load_page(self.group_4)
        self.curated_students_page.enter_text_in_sids_input('9999999990, 9999999991')
        self.curated_students_page.click_add_sids_to_group_button()
        self.curated_students_page.click_remove_invalid_sids()

    def test_group_bulk_add_sids_allows_removal_of_rejected_sids_when_more_than_15(self):
        a = [self.test.students[-1].sid]
        for i in range(16):
            a.append(f'99999999{10 + i}')
        self.curated_students_page.load_page(self.group_4)
        self.curated_students_page.enter_text_in_sids_input(', '.join(a))
        self.curated_students_page.click_add_sids_to_group_button()
        self.curated_students_page.click_remove_invalid_sids()

    def test_group_bulk_add_sids_allows_addition_of_large_sets_of_sids(self):
        self.curated_students_page.load_page(self.group_4)

        students = self.test.students[0:99]
        self.curated_students_page.add_comma_sep_sids_to_existing_grp(self.group_4, students)
        self.curated_students_page.wait_for_student_list()

        students = self.test.students[100:199]
        self.curated_students_page.add_line_sep_sids_to_existing_grp(self.group_4, students)
        self.curated_students_page.wait_for_spinner()

        students = self.test.students[100:199]
        self.curated_students_page.add_space_sep_sids_to_existing_grp(self.group_4, students)
        self.curated_students_page.wait_for_spinner()

        self.curated_students_page.load_page(self.group_4)
        visible_sids = self.curated_students_page.visible_sids()
        visible_sids.sort()
        member_sids = list(map(lambda m: m.sid, self.group_4.members))
        member_sids.sort()
        app.logger.info(f'Expecting {member_sids}, got {visible_sids}')
        missing_sids = list(set(member_sids) - set(visible_sids))
        # Account for SIDs that have no associated data and will not appear in Boa
        if missing_sids:
            for sid in missing_sids:
                app.logger.info(f'Checking data for missing SID {sid}')
                student = next(filter(lambda m: m.sid == sid, self.group_4.members))
                if not self.test_student.enrollment_data:
                    app.logger.info(f'Removing SID {sid} from the group since the student does not appear in BOA')
                    missing_sids.remove(sid)
                    self.group_4.members.remove(student)
        assert not missing_sids

    def test_export_group_membership_with_default_columns(self):
        self.curated_students_page.load_page(self.group_4)
        download = self.curated_students_page.export_default_student_list(self.group_4)
        self.curated_students_page.verify_default_export_student_list(self.group_4, download)

    def test_export_group_membership_with_custom_columns(self):
        self.curated_students_page.load_page(self.group_4)
        download = self.curated_students_page.export_custom_student_list(self.group_4)
        self.curated_students_page.verify_custom_export_student_list(self.group_4, download)

    def test_group_deletion_can_be_canceled(self):
        self.curated_students_page.load_page(self.group_1)
        self.curated_students_page.cancel_group_deletion(self.group_1)

    def test_homepage_shows_group_name(self):
        self.homepage.load_page()
        visible_groups = self.homepage.curated_groups()
        for g in self.advisor_groups:
            assert g.name in visible_groups

    def test_homepage_shows_group_member_count(self):
        for g in self.advisor_groups:
            assert self.homepage.member_count(g) == len(g.members)

    def test_homepage_shows_group_members_with_alerts(self):
        for g in self.advisor_groups:
            self.homepage.expand_member_rows(g)
            self.homepage.verify_member_alerts(g, self.test.advisor)
