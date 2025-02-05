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
import datetime
import random

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.department import Department
from bea.test_utils import boa_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest


@pytest.mark.usefixtures('page_objects')
class TestCuratedAdmitGroup:

    test = BEATestConfig()
    test.curated_admits()
    random.shuffle(test.admits)
    admit = test.admits[0]
    latest_update_date = nessie_utils.get_admit_data_update_date()
    app.logger.info(f'Test student is Empl ID {admit.sid}')

    pre_existing_groups = boa_utils.get_user_curated_groups(test.advisor, admits=True)
    pre_existing_cohorts = boa_utils.get_user_filtered_cohorts(test.advisor, admits=True)

    cohort = test.searches[0]

    group_0 = Cohort({'name': f'Group 0 {test.test_id}', 'is_ce3': True})
    group_1 = Cohort({'name': f'Group 1 {test.test_id}', 'is_ce3': True})
    group_2 = Cohort({'name': f'Group 2 {test.test_id}', 'is_ce3': True})
    group_3 = Cohort({'name': f'Group 3 {test.test_id}', 'is_ce3': True})
    group_4 = Cohort({'name': f'Group 4 {test.test_id}', 'is_ce3': True})
    group_5 = Cohort({'name': f'Group 5 {test.test_id}', 'is_ce3': True})
    group_6 = Cohort({'name': f'Group 6 {test.test_id}', 'is_ce3': True})
    advisor_groups = [group_1, group_2, group_3, group_4, group_5, group_6]

    def test_cohort_setup(self):
        self.homepage.dev_auth(self.test.advisor)
        for c in self.pre_existing_cohorts:
            self.filtered_admits_page.load_cohort(c)
            self.filtered_admits_page.delete_cohort(c)
        self.filtered_admits_page.search_and_create_new_admit_cohort(self.cohort)

    def test_delete_groups(self):
        for g in self.pre_existing_groups:
            self.curated_admits_page.load_page(g)
            self.curated_admits_page.delete_group(g)

    def test_group_creation_from_cohort_list_view_selector(self):
        group = Cohort({'name': f'CE3 group from cohort {self.test.test_id}', 'is_ce3': True})
        self.filtered_admits_page.load_cohort(self.cohort)
        self.filtered_admits_page.wait_for_admit_checkboxes()
        sids = self.filtered_admits_page.admit_cohort_row_sids()
        visible_cohort_members = [a for a in self.test.admits if a.sid in sids]
        self.filtered_admits_page.select_and_add_members_to_new_grp(visible_cohort_members[-10:], group)

    def test_group_creation_from_search_results(self):
        group = Cohort({'name': f'CE3 group from search {self.test.test_id}', 'is_ce3': True})
        self.homepage.enter_simple_search_and_hit_enter(self.admit.sid)
        self.search_results_page.click_admit_results_tab()
        self.search_results_page.select_and_add_members_to_new_grp([self.admit], group)

    def test_group_creation_from_admit_page(self):
        group = Cohort({'name': f'CE3 group from admit page {self.test.test_id}', 'is_ce3': True})
        self.admit_page.load_page(self.admit.sid)
        self.admit_page.click_add_to_admissions_grp(self.admit)
        self.admit_page.add_members_to_new_grp([self.admit], group)

    def test_group_creation_from_bulk_sids(self):
        admits = self.test.admits[0:52]
        group = Cohort({'name': f'CE3 group from CS IDs {self.test.test_id}', 'is_ce3': True})
        self.admit_page.click_sidebar_create_admit_group()
        self.curated_admits_page.create_group_with_bulk_sids(group, admits)

    def test_group_name_required(self):
        self.admit_page.load_page(self.admit.sid)
        self.admit_page.click_add_to_admissions_grp(self.admit)
        self.admit_page.click_create_new_grp(self.group_0)
        assert not self.admit_page.element(self.admit_page.GROUP_SAVE_BUTTON).is_enabled()

    def test_group_name_max_255_chars(self):
        self.group_0.name = 'A llooooong title ' * 15
        self.admit_page.enter_group_name(self.group_0)
        self.admit_page.when_present(self.admit_page.NO_CHARS_LEFT_MSG, 1)

    def test_group_name_unique(self):
        self.group_0.name = self.cohort.name
        self.admit_page.enter_group_name(self.group_0)
        self.admit_page.when_present(self.admit_page.DUPE_GROUP_NAME_MSG, utils.get_short_timeout())

    def test_group_renamed(self):
        self.group_0.name = f'CE3 Name Validation {self.test.test_id}'
        self.admit_page.load_page(self.admit.sid)
        self.admit_page.click_add_to_admissions_grp(self.admit)
        self.admit_page.add_members_to_new_grp([self.admit], self.group_0)
        self.curated_admits_page.load_page(self.group_0)
        self.curated_admits_page.rename_group(self.group_0, f'Renamed {self.group_0.name}')

    def test_set_up_advisor_grps(self):
        admit = self.test.admits[-1]
        self.admit_page.load_page(admit.sid)
        for grp in self.advisor_groups:
            self.admit_page.click_add_to_admissions_grp(admit)
            self.admit_page.add_members_to_new_grp([admit], grp)

    def test_group_members_can_be_added_from_cohort_select_all(self):
        self.filtered_admits_page.load_cohort(self.cohort)
        self.filtered_admits_page.select_and_add_all_visible_to_grp(self.test.admits, self.group_1)
        self.curated_admits_page.load_page(self.group_1)
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_1)

    def test_group_members_can_be_added_from_cohort_select_some(self):
        self.filtered_admits_page.load_cohort(self.cohort)
        available_admits = self.filtered_admits_page.admits_available_to_add_to_grp(self.test, self.group_2)
        admits_to_add = available_admits[0:10]
        self.filtered_admits_page.select_and_add_members_to_grp(admits_to_add, self.group_2)
        self.curated_admits_page.load_page(self.group_2)
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_2)

    def test_group_members_can_be_added_from_admit_page(self):
        self.admit_page.load_page(self.admit.sid)
        self.admit_page.click_add_to_admissions_grp(self.admit)
        self.admit_page.add_members_to_grp([self.admit], self.group_3)
        self.curated_admits_page.load_page(self.group_3)
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_3)

    def test_group_members_can_be_added_from_bulk_sids(self):
        self.curated_admits_page.load_page(self.group_4)
        self.curated_admits_page.add_comma_sep_sids_to_existing_grp(self.group_4, self.test.admits[-10:])
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_4)

    def test_group_members_can_be_added_from_search_results_select_all(self):
        self.homepage.enter_simple_search_and_hit_enter(self.admit.sid)
        self.search_results_page.click_admit_results_tab()
        self.search_results_page.select_and_add_all_visible_to_grp(self.test.admits, self.group_5)
        self.curated_admits_page.load_page(self.group_5)
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_5)

    def test_group_members_can_be_added_from_search_results_select_some(self):
        self.homepage.enter_simple_search_and_hit_enter(self.admit.sid)
        self.search_results_page.click_admit_results_tab()
        self.search_results_page.select_and_add_members_to_grp([self.admit], self.group_6)
        self.curated_admits_page.load_page(self.group_6)
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_6)

    def test_group_membership_shown_on_admit_page(self):
        admit = self.group_1.members[0]
        self.admit_page.load_page(admit.sid)
        self.admit_page.click_add_to_admissions_grp(admit)
        assert self.admit_page.is_group_selected(self.group_1)

    def test_group_membership_can_be_removed_on_group_page(self):
        admit = self.group_2.members[-1]
        self.curated_admits_page.load_page(self.group_2)
        self.curated_admits_page.remove_admit_by_row_index(self.group_2, admit)

    def test_group_membership_can_be_removed_on_admit_page(self):
        admit = self.group_1.members[-1]
        self.admit_page.load_page(admit.sid)
        self.admit_page.click_add_to_admissions_grp(admit)
        self.admit_page.remove_member_from_grp(admit, self.group_1)
        self.curated_admits_page.load_page(self.group_1)
        self.curated_admits_page.verify_visible_admits_match_group_members(self.group_1)

    def test_bulk_sids_page_rejects_malformed_input(self):
        self.curated_admits_page.load_page(self.group_4)
        self.curated_admits_page.click_add_sids_button()
        self.curated_admits_page.enter_text_in_sids_input('nullum magnum ingenium sine mixtura dementiae fuit')
        self.curated_admits_page.click_add_sids_to_group_button()
        self.curated_admits_page.click_remove_invalid_sids()

    def test_bulk_sids_page_rejects_nonexistent_sids(self):
        self.curated_admits_page.load_page(self.group_4)
        self.curated_admits_page.click_add_sids_button()
        self.curated_admits_page.enter_text_in_sids_input('9999999990, 9999999991')
        self.curated_admits_page.click_add_sids_to_group_button()
        self.curated_admits_page.click_remove_invalid_sids()

    def test_bulk_sids_page_comma_separated_sids(self):
        admits = self.test.admits[100:150]
        self.curated_admits_page.load_page(self.group_4)
        self.curated_admits_page.add_comma_sep_sids_to_existing_grp(self.group_4, admits)
        self.curated_admits_page.wait_for_spinner()

    def test_bulk_sids_page_line_separated_sids(self):
        admits = self.test.admits[200:250]
        self.curated_admits_page.load_page(self.group_4)
        self.curated_admits_page.add_line_sep_sids_to_existing_grp(self.group_4, admits)
        self.curated_admits_page.wait_for_spinner()

    def test_bulk_sids_page_space_separated_sids(self):
        admits = self.test.admits[300:350]
        self.curated_admits_page.load_page(self.group_4)
        self.curated_admits_page.add_space_sep_sids_to_existing_grp(self.group_4, admits)
        self.curated_admits_page.wait_for_spinner()

    def test_group_appears_in_everyone_groups(self):
        self.curated_admits_page.click_view_everyone_groups()
        visible = self.curated_all_page.visible_admit_groups()
        utils.assert_actual_includes_expected(visible, self.group_4.name)

    def test_group_shows_date_if_stale(self):
        self.curated_admits_page.load_page(self.group_4)
        is_stale = self.curated_admits_page.is_present(
            self.curated_admits_page.data_update_date_heading(self.latest_update_date))
        if datetime.datetime.strptime(self.latest_update_date, '%b %d, %Y').date() == datetime.date.today():
            assert not is_stale
        else:
            assert is_stale

    def test_group_can_be_exported(self):
        admits_csv = self.curated_admits_page.export_admit_list(self.group_4)
        self.curated_admits_page.verify_admits_present_in_export(self.group_4, admits_csv)

    def test_group_export_contains_no_emails(self):
        admits_csv = self.curated_admits_page.export_admit_list(self.group_4)
        self.curated_admits_page.verify_no_email_in_export(admits_csv)

    def test_rename_group(self):
        self.curated_admits_page.load_page(self.group_1)
        self.curated_admits_page.rename_group(self.group_1, f'Renamed {self.group_1.name}')

    def test_admit_group_not_reachable_by_non_ce3_advisor(self):
        self.test.dept = Department.L_AND_S
        self.test.set_advisor()
        self.homepage.switch_user(self.test.advisor)
        self.curated_admits_page.hit_non_auth_group(self.group_1)
