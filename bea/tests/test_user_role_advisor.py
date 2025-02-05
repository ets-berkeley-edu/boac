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
import random

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.cohort import Cohort
from bea.models.cohorts_and_groups.cohort_admit_filter import CohortAdmitFilter
from bea.models.cohorts_and_groups.cohort_filter import CohortFilter
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.models.department import Department
from bea.models.squad import Squad
from bea.test_utils import boa_utils
from bea.test_utils import nessie_filter_students_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest


test = BEATestConfig()
test.user_role_advisor()
random.shuffle(test.students)

admin_cohorts = boa_utils.get_everyone_filtered_cohorts(Department.ADMIN)
admin_groups = boa_utils.get_everyone_curated_groups(Department.ADMIN)

# ASC config
test_asc = BEATestConfig()
test_asc.user_role_asc(test)
asc_cohorts = boa_utils.get_everyone_filtered_cohorts(test_asc.dept)
asc_groups = boa_utils.get_everyone_curated_groups(test_asc.dept)

asc_inactive_filter = CohortFilter(data={'asc_inactive': True}, dept=test_asc.dept)
asc_inactive_sids = nessie_filter_students_utils.get_cohort_result(test_asc, asc_inactive_filter)
student_asc_inactive = next(filter(lambda s: s.sid == asc_inactive_sids[0], test.students))

asc_active_filter = CohortFilter(data={'asc_teams': [{'squad': Squad.MTE.value['name']}]}, dept=test_asc.dept)
asc_active_sids = nessie_filter_students_utils.get_cohort_result(test_asc, asc_active_filter)
student_asc_active = next(filter(lambda s: s.sid == asc_active_sids[0], test.students))

nessie_utils.set_student_profiles([student_asc_active, student_asc_inactive])

# CoE config
test_coe = BEATestConfig()
test_coe.user_role_coe(test)
coe_cohorts = boa_utils.get_everyone_filtered_cohorts(test_coe.dept)
coe_groups = boa_utils.get_everyone_curated_groups(test_coe.dept)

coe_inactive_filter = CohortFilter(data={'coe_inactive': True}, dept=test_coe.dept)
coe_inactive_sids = nessie_filter_students_utils.get_cohort_result(test_coe, coe_inactive_filter)
student_coe_inactive = next(filter(lambda s: s.sid == coe_inactive_sids[0], test.students))

coe_standing_filter = CohortFilter(data={'coe_academic_standings': [{'standing': 'U'}]}, dept=test_coe.dept)
coe_standing_sids = nessie_filter_students_utils.get_cohort_result(test_coe, coe_standing_filter)
student_coe_standing = next(filter(lambda s: s.sid == coe_standing_sids[0], test.students))

# L&S config
test_ls = BEATestConfig()
test_ls.user_role_l_and_s(test)
ls_cohorts = boa_utils.get_everyone_filtered_cohorts(test_ls.dept)
ls_groups = boa_utils.get_everyone_curated_groups(test_ls.dept)

# My Students filter
plan = '25429U'
auth_users = boa_utils.get_authorized_users()
my_students_advisor = nessie_utils.get_my_students_test_advisor(plan, auth_users)
test.advisor = my_students_advisor
my_students_filter = CohortFilter(data={'cohort_owner_acad_plans': [{'plan': plan}]}, dept=Department.L_AND_S)
my_students_cohort = FilteredCohort({'search_criteria': my_students_filter, 'name': f'My Students {test.test_id}'})

# CE3 config
test_ce3 = BEATestConfig()
test_ce3.user_role_ce3(test)
admit = nessie_utils.get_admits()[-1]
ce3_filter = CohortAdmitFilter({'urem': True})
ce3_cohort = FilteredCohort({'search_criteria': ce3_filter, 'name': f'CE3 {test_ce3.test_id}'})

app.logger.info(f'ASC advisor: {test_asc.advisor.uid}')
app.logger.info(f'CoE advisor: {test_coe.advisor.uid}')
app.logger.info(f'L&S advisor: {test_ls.advisor.uid}')
app.logger.info(f'My Students advisor: {test.advisor.uid}')
app.logger.info(f'CE3 advisor: {test_ce3.advisor.uid}')
app.logger.info(f'ASC active: {student_asc_active.uid}')
app.logger.info(f'ASC inactive: {student_asc_inactive.uid}')
app.logger.info(f'CoE inactive: {student_coe_inactive.uid}')
app.logger.info(f'CoE standing: {student_coe_standing.uid}')
app.logger.info(f'Admit: {admit.sid}')


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_create_ce3_cohort(self):
        self.homepage.load_page()
        self.homepage.dev_auth(test_ce3.advisor)
        self.homepage.click_sidebar_create_ce3_filtered()
        self.filtered_admits_page.perform_admit_search(ce3_cohort)
        self.filtered_admits_page.create_new_cohort(ce3_cohort)


@pytest.mark.usefixtures('page_objects')
class TestASCAdvisor:

    # Cohort visibility

    def test_cohorts_all(self):
        self.filtered_admits_page.log_out()
        self.homepage.dev_auth(test_asc.advisor)
        self.homepage.click_view_everyone_cohorts()
        expected = [c.name for c in asc_cohorts]
        expected.sort()
        visible = self.cohorts_all_page.visible_student_cohorts()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_cannot_reach_admin_cohort(self):
        if admin_cohorts:
            self.filtered_students_page.hit_non_auth_cohort(admin_cohorts[0])

    def test_cannot_reach_other_dept_cohort(self):
        if coe_cohorts:
            self.filtered_students_page.hit_non_auth_cohort(coe_cohorts[0])

    def test_cannot_reach_admit_cohort(self):
        self.filtered_admits_page.hit_non_auth_cohort(ce3_cohort)

    # Groups

    def test_groups_all(self):
        self.homepage.click_view_everyone_groups()
        expected = [g.name for g in asc_groups]
        expected.sort()
        visible = self.curated_all_page.visible_student_groups()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_cannot_reach_admin_group(self):
        if admin_groups:
            self.curated_students_page.hit_non_auth_group(admin_groups[0])

    def test_cannot_reach_other_dept_group(self):
        if coe_groups:
            self.curated_students_page.hit_non_auth_group(coe_groups[0])

    # Student / Admit pages

    def test_student_page_asc_inactive_sports_visible(self):
        self.student_page.load_page(student_asc_inactive)
        assert self.student_page.is_present(self.student_page.INACTIVE_ASC_FLAG)
        squads = student_asc_inactive.profile_data.asc_teams()
        squads.sort()
        utils.assert_equivalence(self.student_page.sports(), squads)

    def test_student_page_asc_active_sports_visible(self):
        self.student_page.load_page(student_asc_active)
        assert not self.student_page.is_present(self.student_page.INACTIVE_ASC_FLAG)
        squads = student_asc_active.profile_data.asc_teams()
        squads.sort()
        utils.assert_equivalence(self.student_page.sports(), squads)

    def test_student_page_coe_inactive_not_visible(self):
        self.student_page.load_page(student_coe_inactive)
        assert not self.student_page.is_present(self.student_page.INACTIVE_COE_FLAG)

    def test_student_page_coe_standing_not_visible(self):
        self.student_page.load_page(student_coe_standing)
        assert not self.student_page.is_present(self.student_page.ACADEMIC_STANDING_COE)

    def test_student_api_coe_profile_not_present(self):
        assert not self.api_student_page.coe_profile(student_coe_inactive)

    def test_cannot_reach_admit_profile(self):
        self.admit_page.hit_page_url(admit.sid)
        self.admit_page.wait_for_404()

    def test_admit_api_not_reachable(self):
        response = self.api_admit_page.hit_endpoint(admit)
        utils.assert_equivalence(self.api_admit_page.message(response), 'Unauthorized')

    # Cohort search

    def test_cohort_filter_options(self):
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        opts = self.filtered_students_page.filter_options()
        utils.assert_actual_includes_expected(opts, 'Inactive (ASC)')
        utils.assert_actual_includes_expected(opts, 'Intensive (ASC)')
        utils.assert_actual_includes_expected(opts, 'Team (ASC)')
        assert 'Advisor (COE)' not in opts
        assert 'Ethnicity (COE)' not in opts
        assert 'Inactive (COE)' not in opts
        assert 'PREP (COE)' not in opts
        assert 'Probation (COE)' not in opts
        assert 'Underrepresented Minority (COE)' not in opts

    def test_cohort_filter_results(self):
        cohort = FilteredCohort(data={'search_criteria': asc_inactive_filter})
        self.filtered_students_page.perform_student_search(cohort)
        squads = student_asc_inactive.profile_data.asc_teams()
        squads.sort()
        visible_sports = self.filtered_students_page.student_sports(student_asc_inactive)
        visible_sports.sort()
        utils.assert_equivalence(visible_sports, squads)

    def test_cohort_asc_inactive_flag(self):
        assert self.filtered_students_page.student_has_inactive_asc_flag(student_asc_inactive)

    # Advanced search

    def test_no_admits_search_option(self):
        self.homepage.open_adv_search()
        assert not self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)

    def test_no_admit_search_results(self):
        self.homepage.click_adv_search_cxl_button()
        self.homepage.enter_simple_search_and_hit_enter(admit.sid)
        assert not self.search_results_page.are_admits_in_results()

    # Profile links, admin features

    def test_no_header_degree_check_link(self):
        self.homepage.click_header_dropdown()
        assert not self.homepage.is_present(self.homepage.DEGREE_CHECKS_LINK)

    def test_no_header_fdr_link(self):
        assert not self.homepage.is_present(self.homepage.FLIGHT_DATA_RECORDER_LINK)

    def test_no_header_flight_deck_link(self):
        assert not self.homepage.is_present(self.homepage.FLIGHT_DECK_LINK)

    def test_no_header_pax_manifest_link(self):
        assert not self.homepage.is_present(self.homepage.PAX_MANIFEST_LINK)

    def test_no_profile_admin_features(self):
        self.homepage.load_page()
        self.homepage.click_profile_link()
        assert not self.flight_deck_page.is_present(self.flight_deck_page.POST_SERVICE_ALERT_CHECKBOX)
        assert not self.flight_deck_page.is_present(self.flight_deck_page.TOPIC_SEARCH_INPUT)

    def test_cannot_reach_cachejob_endpoint(self):
        response = self.api_admin_page.load_cachejob()
        utils.assert_actual_includes_expected(self.api_admin_page.message(response), 'Unauthorized')


@pytest.mark.usefixtures('page_objects')
class TestCoEAdvisor:

    # Cohort visibility

    def test_cohorts_all(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(test_coe.advisor)
        self.homepage.click_view_everyone_cohorts()
        expected = [c.name for c in coe_cohorts]
        expected.sort()
        visible = self.cohorts_all_page.visible_student_cohorts()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_cannot_reach_admin_cohort(self):
        if admin_cohorts:
            self.filtered_students_page.hit_non_auth_cohort(admin_cohorts[0])

    def test_cannot_reach_other_dept_cohort(self):
        if asc_cohorts:
            self.filtered_students_page.hit_non_auth_cohort(asc_cohorts[0])

    def test_cannot_reach_admit_cohort(self):
        self.filtered_admits_page.hit_non_auth_cohort(ce3_cohort)

    # Group visibility

    def test_groups_all(self):
        self.homepage.click_view_everyone_groups()
        expected = [g.name for g in coe_groups]
        expected.sort()
        visible = self.curated_all_page.visible_student_groups()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_cannot_reach_admin_group(self):
        if admin_groups:
            self.curated_students_page.hit_non_auth_group(admin_groups[0])

    def test_cannot_reach_other_dept_group(self):
        if asc_groups:
            self.curated_students_page.hit_non_auth_group(asc_groups[0])

    # Student / Admit pages

    def test_student_page_asc_inactive_not_visible(self):
        self.student_page.load_page(student_asc_inactive)
        assert not self.student_page.is_present(self.student_page.INACTIVE_ASC_FLAG)

    def test_student_page_asc_inactive_sports_not_visible(self):
        assert not self.student_page.sports()

    def test_student_page_coe_inactive_visible(self):
        self.student_page.load_page(student_coe_inactive)
        assert self.student_page.is_present(self.student_page.INACTIVE_COE_FLAG)

    def test_student_page_coe_standing_visible(self):
        self.student_page.load_page(student_coe_standing)
        assert self.student_page.is_present(self.student_page.ACADEMIC_STANDING_COE)

    def test_student_api_asc_profile_not_present(self):
        assert not self.api_student_page.asc_profile(student_asc_inactive)

    def test_cannot_reach_admit_profile(self):
        self.admit_page.hit_page_url(admit.sid)
        self.admit_page.wait_for_404()

    def test_admit_api_not_reachable(self):
        response = self.api_admit_page.hit_endpoint(admit)
        utils.assert_equivalence(self.api_admit_page.message(response), 'Unauthorized')

    # Cohort search

    def test_cohort_filter_options(self):
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        opts = self.filtered_students_page.filter_options()
        utils.assert_actual_includes_expected(opts, 'Advisor (COE)')
        utils.assert_actual_includes_expected(opts, 'Ethnicity (COE)')
        utils.assert_actual_includes_expected(opts, 'Inactive (COE)')
        utils.assert_actual_includes_expected(opts, 'PREP (COE)')
        utils.assert_actual_includes_expected(opts, 'Academic Standing (COE)')
        utils.assert_actual_includes_expected(opts, 'Underrepresented Minority (COE)')
        assert 'Inactive (ASC)' not in opts
        assert 'Intensive (ASC)' not in opts
        assert 'Team (ASC)' not in opts

    def test_cohort_coe_inactive_flag(self):
        cohort = FilteredCohort(data={'search_criteria': coe_inactive_filter})
        self.filtered_students_page.perform_student_search(cohort)
        assert self.filtered_students_page.student_has_inactive_coe_flag(student_coe_inactive)

    # Advanced search

    def test_no_admits_search_option(self):
        self.homepage.open_adv_search()
        assert not self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)

    def test_no_admit_search_results(self):
        self.homepage.click_adv_search_cxl_button()
        self.homepage.enter_simple_search_and_hit_enter(admit.sid)
        assert not self.search_results_page.are_admits_in_results()

    # Profile links, admin features

    def test_header_degree_check_link(self):
        self.homepage.click_header_dropdown()
        assert self.homepage.is_present(self.homepage.DEGREE_CHECKS_LINK)

    def test_no_header_fdr_link(self):
        assert not self.homepage.is_present(self.homepage.FLIGHT_DATA_RECORDER_LINK)

    def test_no_header_flight_deck_link(self):
        assert not self.homepage.is_present(self.homepage.FLIGHT_DECK_LINK)

    def test_no_header_pax_manifest_link(self):
        assert not self.homepage.is_present(self.homepage.PAX_MANIFEST_LINK)

    def test_no_profile_admin_features(self):
        self.homepage.load_page()
        self.homepage.click_profile_link()
        assert not self.flight_deck_page.is_present(self.flight_deck_page.POST_SERVICE_ALERT_CHECKBOX)
        assert not self.flight_deck_page.is_present(self.flight_deck_page.TOPIC_SEARCH_INPUT)

    def test_cannot_reach_cachejob_endpoint(self):
        response = self.api_admin_page.load_cachejob()
        utils.assert_actual_includes_expected(self.api_admin_page.message(response), 'Unauthorized')


@pytest.mark.usefixtures('page_objects')
class TestLandSAdvisor:

    # Cohort visibility

    def test_cohorts_all(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(test_ls.advisor)
        self.homepage.click_view_everyone_cohorts()
        expected = [c.name for c in ls_cohorts]
        expected.sort()
        visible = self.cohorts_all_page.visible_student_cohorts()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_cannot_reach_admin_cohort(self):
        if admin_cohorts:
            self.filtered_students_page.hit_non_auth_cohort(admin_cohorts[0])

    def test_cannot_reach_admit_cohort(self):
        self.filtered_admits_page.hit_non_auth_cohort(ce3_cohort)

    def test_can_reach_cohort_in_same_dept(self):
        cohort = next(filter(lambda c: c.owner_uid != test_ls.advisor.uid, ls_cohorts))
        self.filtered_students_page.load_cohort(cohort)

    def test_can_view_filters(self):
        self.filtered_students_page.show_filters()

    def test_cannot_edit_filters(self):
        assert not self.filtered_students_page.elements(self.filtered_students_page.COHORT_EDIT_BUTTON)

    def test_can_export_cohort_student_list(self):
        assert self.filtered_students_page.is_present(self.filtered_students_page.EXPORT_LIST_BUTTON)

    def test_cannot_rename_cohort(self):
        assert not self.filtered_students_page.is_present(self.filtered_students_page.RENAME_COHORT_BUTTON)

    def test_cannot_delete_cohort(self):
        assert not self.filtered_students_page.is_present(self.filtered_students_page.DELETE_COHORT_BUTTON)

    # Groups visibility

    def test_groups_all(self):
        self.homepage.click_view_everyone_groups()
        expected = [g.name for g in ls_groups]
        expected.sort()
        visible = self.curated_all_page.visible_student_groups()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_cannot_reach_admin_group(self):
        if admin_groups:
            self.curated_students_page.hit_non_auth_group(admin_groups[0])

    def test_can_reach_group_in_same_dept(self):
        group = next(filter(lambda c: c.owner_uid != test_ls.advisor.uid, ls_groups))
        self.curated_students_page.load_page(group)

    def test_can_export_group_student_list(self):
        assert self.curated_students_page.is_present(self.curated_students_page.EXPORT_LIST_BUTTON)

    def test_cannot_add_students(self):
        assert not self.curated_students_page.is_present(self.curated_students_page.ADD_STUDENTS_BUTTON)

    def test_cannot_rename_group(self):
        assert not self.curated_students_page.is_present(self.curated_students_page.RENAME_GROUP_BUTTON)

    def test_cannot_delete_group(self):
        assert not self.curated_students_page.is_present(self.curated_students_page.DELETE_GROUP_BUTTON)

    # Student / Admit pages

    def test_student_page_asc_inactive_not_visible(self):
        self.student_page.load_page(student_asc_inactive)
        assert not self.student_page.is_present(self.student_page.INACTIVE_ASC_FLAG)
        assert not self.student_page.sports()

    def test_student_page_asc_active_sports_visible(self):
        self.student_page.load_page(student_asc_active)
        squads = student_asc_active.profile_data.asc_teams()
        squads.sort()
        utils.assert_equivalence(self.student_page.sports(), squads)

    def test_student_page_coe_inactive_not_visible(self):
        self.student_page.load_page(student_coe_inactive)
        assert not self.student_page.is_present(self.student_page.INACTIVE_COE_FLAG)

    def test_student_page_coe_standing_not_visible(self):
        self.student_page.load_page(student_coe_standing)
        assert not self.student_page.is_present(self.student_page.INACTIVE_COE_FLAG)

    def test_student_api_asc_inactive_profile_not_present(self):
        assert not self.api_student_page.asc_profile(student_asc_inactive)

    def test_student_api_coe_profile_not_present(self):
        assert not self.api_student_page.coe_profile(student_coe_inactive)

    def test_cannot_reach_admit_profile(self):
        self.admit_page.hit_page_url(admit.sid)
        self.admit_page.wait_for_404()

    def test_admit_api_not_reachable(self):
        response = self.api_admit_page.hit_endpoint(admit)
        utils.assert_equivalence(self.api_admit_page.message(response), 'Unauthorized')

    # Cohort search

    def test_cohort_filter_options(self):
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        opts = self.filtered_students_page.filter_options()
        assert 'Advisor (COE)' not in opts
        assert 'Ethnicity (COE)' not in opts
        assert 'Inactive (COE)' not in opts
        assert 'PREP (COE)' not in opts
        assert 'Probation (COE)' not in opts
        assert 'Underrepresented Minority (COE)' not in opts
        assert 'Inactive (ASC)' not in opts
        assert 'Intensive (ASC)' not in opts
        assert 'Team (ASC)' not in opts

    # Advanced search

    def test_no_admits_search_option(self):
        self.homepage.open_adv_search()
        assert not self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)

    def test_no_admit_search_results(self):
        self.homepage.click_adv_search_cxl_button()
        self.homepage.enter_simple_search_and_hit_enter(admit.sid)
        assert not self.search_results_page.are_admits_in_results()

    # Profile links, admin features

    def test_no_header_degree_check_link(self):
        self.homepage.click_header_dropdown()
        assert not self.homepage.is_present(self.homepage.DEGREE_CHECKS_LINK)

    def test_no_header_fdr_link(self):
        assert not self.homepage.is_present(self.homepage.FLIGHT_DATA_RECORDER_LINK)

    def test_no_header_flight_deck_link(self):
        assert not self.homepage.is_present(self.homepage.FLIGHT_DECK_LINK)

    def test_no_header_pax_manifest_link(self):
        assert not self.homepage.is_present(self.homepage.PAX_MANIFEST_LINK)

    def test_no_profile_admin_features(self):
        self.homepage.load_page()
        self.homepage.click_profile_link()
        assert not self.flight_deck_page.is_present(self.flight_deck_page.POST_SERVICE_ALERT_CHECKBOX)
        assert not self.flight_deck_page.is_present(self.flight_deck_page.TOPIC_SEARCH_INPUT)

    def test_cannot_reach_cachejob_endpoint(self):
        response = self.api_admin_page.load_cachejob()
        utils.assert_actual_includes_expected(self.api_admin_page.message(response), 'Unauthorized')


@pytest.mark.usefixtures('page_objects')
class TestMyStudents:

    def test_my_students_cohort_search(self):
        self.homepage.load_page()
        self.homepage.log_out()
        self.homepage.dev_auth(my_students_advisor)
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(my_students_cohort)
        self.filtered_students_page.set_cohort_members(test, my_students_cohort)
        expected = [m.sid for m in my_students_cohort.members]
        expected.sort()
        visible = self.filtered_students_page.visible_sids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_create_my_students_cohort(self):
        self.filtered_students_page.create_new_cohort(my_students_cohort)

    def test_default_my_students_cohort_export(self):
        test_group = Cohort({'name': f'Group {test.test_id}'})
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(test_group, my_students_cohort.members)

        self.filtered_students_page.load_cohort(my_students_cohort)
        downloaded_csv = self.filtered_students_page.export_default_student_list(my_students_cohort)
        self.filtered_students_page.verify_default_export_student_list(my_students_cohort, downloaded_csv)

    def test_custom_my_students_cohort_export(self):
        downloaded_csv = self.filtered_students_page.export_custom_student_list(my_students_cohort, my_students_advisor)
        self.filtered_students_page.verify_custom_export_student_list(my_students_cohort, downloaded_csv,
                                                                      my_students_advisor)

    def test_my_students_cohort_visible_to_others(self):
        self.filtered_students_page.log_out()
        self.homepage.dev_auth()
        self.filtered_students_page.load_cohort(my_students_cohort)
        expected = [m.sid for m in my_students_cohort.members]
        expected.sort()
        visible = self.filtered_students_page.visible_sids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_other_user_default_my_students_cohort_export(self):
        downloaded_csv = self.filtered_students_page.export_default_student_list(my_students_cohort)
        self.filtered_students_page.verify_default_export_student_list(my_students_cohort, downloaded_csv)
