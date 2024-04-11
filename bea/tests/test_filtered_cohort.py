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
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.models.department import Department
from bea.test_utils import boa_utils
from bea.test_utils import nessie_filter_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.filtered_cohorts()
pre_existing_cohorts = boa_utils.get_user_filtered_cohorts(test.advisor)


@pytest.mark.usefixtures('page_objects')
class TestFilteredCohortDeletion:

    def test_no_existing_cohorts(self):
        self.homepage.dev_auth(test.advisor)
        for c in pre_existing_cohorts:
            self.filtered_students_page.load_cohort(c)
            self.filtered_students_page.delete_cohort(c)
        self.homepage.load_page()
        self.homepage.when_visible(self.homepage.NO_FILTERED_COHORTS_MSG, utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('cohort', test.searches, scope='class',
                         ids=[f'{vars(cohort.search_criteria)}' for cohort in test.searches])
class TestFilteredCohortResults:

    def test_cohort_search_results_default_by_last_name(self, cohort):
        app.logger.info(f'Testing cohort {test.searches.index(cohort)} with criteria {vars(cohort.search_criteria)}')
        self.filtered_students_page.cancel_cohort()
        self.filtered_students_page.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(cohort)
        expected = nessie_filter_utils.cohort_by_last_name(test, cohort.search_criteria)
        if cohort.members:
            visible = self.filtered_students_page.visible_sids(cohort)
            utils.assert_equivalence(visible, expected)
            self.filtered_students_page.verify_list_view_sorting(expected, visible)
        else:
            utils.assert_equivalence(self.filtered_students_page.results_count(), 0)

    def test_cohort_search_results_export_button(self, cohort):
        enabled = self.filtered_students_page.element(self.filtered_students_page.EXPORT_LIST_BUTTON).is_enabled()
        assert enabled if cohort.members else not enabled

    def test_cohort_search_cohort_creation(self, cohort):
        self.filtered_students_page.create_new_cohort(cohort)

    def test_saved_cohort_on_homepage(self, cohort):
        self.homepage.load_page()
        assert cohort.name in self.homepage.filtered_cohorts()

    def test_saved_cohort_homepage_member_count(self, cohort):
        utils.assert_equivalence(self.homepage.member_count(cohort), len(cohort.members))


@pytest.mark.usefixtures('page_objects')
class TestFilteredCohortExport:

    test.searches.sort(key=lambda c: len(c.members), reverse=True)
    cohort = test.searches[0]

    def test_ferpa_before_export(self):
        self.filtered_students_page.load_cohort(self.cohort)
        self.filtered_students_page.click_export_list()
        title = 'FERPA (Privacy Disclosure) - Office of the Registrar'
        assert self.filtered_students_page.is_external_link_valid(self.filtered_students_page.FERPA_WARNING_LINK, title)

    def test_default_cohort_export(self):
        self.filtered_students_page.click_cancel_export_list()
        downloaded_csv = self.filtered_students_page.export_default_student_list(self.cohort)
        self.filtered_students_page.verify_default_export_student_list(self.cohort, downloaded_csv)

    def test_custom_cohort_export(self):
        downloaded_csv = self.filtered_students_page.export_custom_student_list(self.cohort)
        self.filtered_students_page.verify_custom_export_student_list(self.cohort, downloaded_csv)


@pytest.mark.usefixtures('page_objects')
class TestFilteredCohortSorting:

    cohort = next(filter(lambda c: len(c.members) in list(range(50, 150)), test.searches))
    cohort_alerts = boa_utils.get_un_dismissed_users_alerts(cohort.members, test.advisor)

    def test_sort_cohort_by_first_name(self):
        self.filtered_students_page.load_cohort(self.cohort)
        self.filtered_students_page.sort_by_first_name()
        expected = nessie_filter_utils.cohort_by_first_name(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_team(self):
        if test.dept in [Department.ADMIN, Department.ASC]:
            self.filtered_students_page.sort_by_team()
            expected = nessie_filter_utils.cohort_by_team(test, self.cohort.search_criteria)
            self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_cumulative_gpa_asc(self):
        self.filtered_students_page.sort_by_gpa_cumulative()
        expected = nessie_filter_utils.cohort_by_gpa_asc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_cumulative_gpa_desc(self):
        self.filtered_students_page.sort_by_gpa_cumulative_desc()
        expected = nessie_filter_utils.cohort_by_gpa_desc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_last_term_gpa_asc(self):
        self.filtered_students_page.sort_by_last_term_gpa()
        expected = nessie_filter_utils.cohort_by_gpa_last_term_asc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_last_term_gpa_desc(self):
        self.filtered_students_page.sort_by_last_term_gpa_desc()
        expected = nessie_filter_utils.cohort_by_gpa_last_term_desc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_last_last_term_gpa_asc(self):
        term = utils.get_previous_term(utils.get_previous_term())
        self.filtered_students_page.sort_by_last_term_gpa(term)
        expected = nessie_filter_utils.cohort_by_gpa_last_term_asc(test, self.cohort.search_criteria, term)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_last_last_term_gpa_desc(self):
        term = utils.get_previous_term(utils.get_previous_term())
        self.filtered_students_page.sort_by_last_term_gpa_desc()
        expected = nessie_filter_utils.cohort_by_gpa_last_term_desc(test, self.cohort.search_criteria, term)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_level(self):
        self.filtered_students_page.sort_by_level()
        expected = nessie_filter_utils.cohort_by_level(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_major(self):
        self.filtered_students_page.sort_by_major()
        expected = nessie_filter_utils.cohort_by_major(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_entering_term(self):
        self.filtered_students_page.sort_by_entering_term()
        expected = nessie_filter_utils.cohort_by_matriculation(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_expected_grad_term(self):
        self.filtered_students_page.sort_by_expected_grad()
        expected = nessie_filter_utils.cohort_by_expected_grad(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_terms_in_attendance_asc(self):
        self.filtered_students_page.sort_by_terms_in_attend()
        expected = nessie_filter_utils.cohort_by_terms_in_attend_asc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_terms_in_attendance_desc(self):
        self.filtered_students_page.sort_by_terms_in_attend_desc()
        expected = nessie_filter_utils.cohort_by_terms_in_attend_desc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_units_in_progress_asc(self):
        self.filtered_students_page.sort_by_units_in_progress()
        expected = nessie_filter_utils.cohort_by_units_in_prog_asc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_units_in_progress_desc(self):
        self.filtered_students_page.sort_by_units_in_progress_desc()
        expected = nessie_filter_utils.cohort_by_units_in_prog_desc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_units_completed_asc(self):
        self.filtered_students_page.sort_by_units_completed()
        expected = nessie_filter_utils.cohort_by_units_complete_asc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)

    def test_sort_cohort_by_units_completed_desc(self):
        self.filtered_students_page.sort_by_units_completed_desc()
        expected = nessie_filter_utils.cohort_by_units_complete_desc(test, self.cohort.search_criteria)
        self.filtered_students_page.compare_visible_sid_sorting_to_expected(expected)


@pytest.mark.usefixtures('page_objects')
class TestFilteredCohortHomepage:

    cohort = next(filter(lambda c: len(c.members) in list(range(50, 150)), test.searches))
    cohort_alerts = boa_utils.get_un_dismissed_users_alerts(cohort.members, test.advisor)
    alert_members = boa_utils.get_members_with_alerts(cohort, cohort_alerts)
    sids = list(map(lambda m: m.sid, alert_members))

    def test_homepage_cohort_link(self):
        self.homepage.load_page()
        self.homepage.expand_member_rows(self.cohort)
        self.homepage.click_filtered_cohort(self.cohort)
        self.filtered_students_page.when_visible(self.filtered_students_page.cohort_heading_loc(self.cohort),
                                                 utils.get_medium_timeout())

    def test_homepage_cohort_alerts(self):
        self.homepage.load_page()
        self.homepage.expand_member_rows(self.cohort)
        self.homepage.verify_member_alerts(self.cohort, test.advisor)

    def test_homepage_cohort_alerts_default_sort(self):
        if self.cohort_alerts:
            expected_sequence = self.homepage.expected_sids_by_alerts_desc(self.alert_members)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_alerts_asc(self):
        if self.cohort_alerts:
            expected_sequence = self.homepage.expected_sids_by_alerts(self.alert_members)
            self.homepage.sort_by_alert_count(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_name_asc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_last_name_asc(self.sids)
            self.homepage.sort_by_name(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_name_desc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_last_name_desc(self.sids)
            self.homepage.sort_by_name(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_sid_asc(self):
        if self.cohort_alerts:
            self.sids.sort()
            self.homepage.sort_by_sid(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), self.sids)

    def test_homepage_cohort_sid_desc(self):
        if self.cohort_alerts:
            self.sids.reverse()
            self.homepage.sort_by_sid(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), self.sids)

    def test_homepage_cohort_major_asc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_major_asc(self.sids)
            self.homepage.sort_by_major(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_major_desc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_major_desc(self.sids)
            self.homepage.sort_by_major(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_grad_date_asc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_grad_term_asc(self.sids)
            self.homepage.sort_by_expected_grad(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_grad_date_desc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_grad_term_desc(self.sids)
            self.homepage.sort_by_expected_grad(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_term_units_asc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_units_in_prog_asc(self.sids)
            self.homepage.sort_by_term_units(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_term_units_desc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_units_in_prog_desc(self.sids)
            self.homepage.sort_by_term_units(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_cumul_units_asc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_units_complete_asc(self.sids)
            self.homepage.sort_by_cumul_units(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_cumul_units_desc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_units_complete_desc(self.sids)
            self.homepage.sort_by_cumul_units(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_gpa_asc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_gpa_asc(self.sids)
            self.homepage.sort_by_gpa(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)

    def test_homepage_cohort_gpa_desc(self):
        if self.cohort_alerts:
            expected_sequence = nessie_filter_utils.list_by_gpa_desc(self.sids)
            self.homepage.sort_by_gpa(self.cohort)
            utils.assert_equivalence(self.homepage.all_row_sids(self.cohort), expected_sequence)


@pytest.mark.usefixtures('page_objects')
class TestFilteredCohortValidation:

    def test_title_required(self):
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(test.searches[0])
        self.filtered_students_page.click_save_cohort_button_one()
        assert not self.filtered_students_page.element(self.filtered_students_page.SAVE_COHORT_BUTTON_TWO).is_enabled()

    def test_title_255_chars_max_truncated(self):
        cohort = FilteredCohort({
            'name': f'{test.test_id}{"A loooooong title " * 16}',
        })
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(test.searches[0])
        self.filtered_students_page.save_and_name_cohort(cohort)
        cohort.name = cohort.name[0:255]
        self.filtered_students_page.wait_for_filtered_cohort(cohort)
        test.searches.append(cohort)

    def test_title_unique_among_user_cohorts(self):
        cohort = FilteredCohort({
            'name': test.searches[0].name,
        })
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(test.searches[0])
        self.filtered_students_page.save_and_name_cohort(cohort)
        self.filtered_students_page.when_visible(self.filtered_students_page.DUPE_FILTERED_NAME_MSG,
                                                 utils.get_short_timeout())

    def test_own_cohorts_only_on_homepage(self):
        self.homepage.load_page()
        expected = list(map(lambda c: c.name, test.searches))
        expected.sort()
        visible = self.homepage.filtered_cohorts()
        visible.sort()
        utils.assert_equivalence(visible, expected)


@pytest.mark.usefixtures('page_objects')
class TestFilteredCohortEdits:

    def test_edit_college_filter(self):
        self.filtered_students_page.search_and_create_new_cohort(test.cohort)
        test.cohort.search_criteria.colleges = [{'college': 'Undergrad Chemistry'}]
        self.filtered_students_page.edit_filter('College', test.cohort.search_criteria.colleges[0])
        self.filtered_students_page.verify_student_filters_present(test.cohort)

    def test_remove_college_filter(self):
        self.filtered_students_page.cancel_cohort_update()
        test.cohort.search_criteria.colleges = []
        self.filtered_students_page.remove_filter_of_type('College')
        self.filtered_students_page.verify_student_filters_present(test.cohort)

    def test_remove_holds_filter(self):
        self.filtered_students_page.cancel_cohort_update()
        test.cohort.search_criteria.holds = None
        self.filtered_students_page.remove_filter_of_type('Holds')
        self.filtered_students_page.verify_student_filters_present(test.cohort)

    def test_edit_advisor_coe_filter(self):
        self.filtered_students_page.cancel_cohort_update()
        uid = boa_utils.get_dept_advisors(Department.COE)[-1].uid
        test.cohort.search_criteria.coe_advisor = [str(uid)]
        self.filtered_students_page.edit_filter('Advisor (COE)', test.cohort.search_criteria.coe_advisors[0])
        self.filtered_students_page.verify_student_filters_present(test.cohort)

    def test_remove_advisor_coe_filter(self):
        self.filtered_students_page.cancel_cohort_update()
        test.cohort.search_criteria.coe_advisors = []
        self.filtered_students_page.remove_filter_of_type('Advisor (COE)')
        self.filtered_students_page.verify_student_filters_present(test.cohort)

    def test_rename_cohort(self):
        cohort = test.searches[0]
        self.filtered_students_page.rename_cohort(cohort, f'{cohort.name} - Renamed')

    def test_delete_cohort(self):
        self.filtered_students_page.load_cohort(test.searches[0])
        self.filtered_students_page.delete_cohort(test.searches[0])
        self.driver.get(f'{boa_utils.get_boa_base_url()}/cohort/{test.searches[0].cohort_id}')
        self.filtered_students_page.wait_for_404()
