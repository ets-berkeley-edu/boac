"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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
from bea.test_utils import utils
import pytest


test = BEATestConfig()
test.user_role_notes_only()
test_student = test.test_students[0]


@pytest.mark.usefixtures('page_objects')
class TestAdvisorNoCanvasAccess:

    def test_student_page_new_note_button_visible(self):
        test.advisor = test.get_no_canvas_advisor()
        self.homepage.dev_auth(test.advisor)
        self.student_page.load_page(test_student)
        self.student_page.when_present(self.student_page.NEW_NOTE_BUTTON, utils.get_short_timeout())

    def test_student_page_notes_tab_visible(self):
        assert self.student_page.is_present(self.student_page.NOTES_BUTTON)

    def test_student_page_appts_tab_visible(self):
        assert self.student_page.is_present(self.student_page.APPTS_BUTTON)

    def test_student_page_notes_present(self):
        self.student_page.show_notes()
        assert self.student_page.elements(self.student_page.NOTE_MSG_ROW)

    def test_student_page_no_course_site_details(self):
        self.student_page.expand_all_years()
        assert not self.student_page.elements(self.student_page.CLASS_PAGE_LINKS)
        assert not self.student_page.elements(self.student_page.SITE_HEADING)
        assert not self.student_page.elements(self.student_page.SITE_ASSIGNMENTS_HEADER)
        assert not self.student_page.elements(self.student_page.SITE_GRADES_HEADER)

    def test_student_api_no_site_data(self):
        assert not self.api_student_page.student_sites(test_student)

    def test_class_page_verboten(self):
        self.class_page.hit_class_page_url('2178', '13826')
        self.class_page.wait_for_403()

    def test_class_api_verboten(self):
        assert self.api_section_page.is_unauthorized('2178', '13826')

    def test_cohort_page_no_sites(self):
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(test.default_cohort)
        self.filtered_students_page.wait_for_student_list()
        assert not self.filtered_students_page.elements(self.filtered_students_page.SITE_ACTIVITY_HEADER)

    def test_group_page_no_sites(self):
        group = Cohort({'name': f'Group {test.test_id}'})
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(group, test.default_cohort.members)
        self.curated_students_page.wait_for_student_list()
        assert not self.curated_students_page.elements(self.curated_students_page.SITE_ACTIVITY_HEADER)

    def test_no_sidebar_admits(self):
        assert not self.homepage.is_present(self.homepage.ALL_ADMITS_LINK)
        assert not self.homepage.is_present(self.homepage.CREATE_ADMIT_GROUP_LINK)

    def test_sidebar_notes(self):
        assert self.homepage.is_present(self.homepage.BATCH_NOTE_BUTTON)
        assert self.homepage.is_present(self.homepage.DRAFT_NOTES_LINK)

    def test_search_options(self):
        self.homepage.open_adv_search()
        assert self.homepage.is_present(self.homepage.INCLUDE_STUDENTS_CBX)
        assert not self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)
        assert not self.homepage.is_present(self.homepage.INCLUDE_CLASSES_CBX)
        assert self.homepage.is_present(self.homepage.INCLUDE_NOTES_CBX)

    def test_search_results(self):
        self.homepage.enter_adv_search_and_hit_enter('Math')
        assert self.search_results_page.are_students_in_results()
        assert not self.search_results_page.are_admits_in_results()
        assert not self.search_results_page.are_classes_in_results()
        assert self.search_results_page.are_notes_in_results()
        assert self.search_results_page.are_appts_in_results()

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
class TestAdvisorNoCanvasNoNotesAccess:

    def test_student_page_new_note_button_not_visible(self):
        test.advisor = test.get_no_canvas_no_notes_advisor()
        self.homepage.switch_user(test.advisor)
        self.student_page.load_page(test_student)
        self.student_page.when_present(self.student_page.TOGGLE_COLLAPSE_ALL_YEARS, utils.get_short_timeout())
        assert not self.student_page.is_present(self.student_page.NEW_NOTE_BUTTON)

    def test_student_page_notes_tab_not_visible(self):
        assert not self.student_page.is_present(self.student_page.NOTES_BUTTON)

    def test_student_page_appts_tab_not_visible(self):
        assert not self.student_page.is_present(self.student_page.APPTS_BUTTON)

    def test_student_page_e_forms_tab_not_visible(self):
        assert not self.student_page.is_present(self.student_page.E_FORMS_BUTTON)

    def test_student_api_no_appts(self):
        assert not self.api_student_page.student_appts(test_student)

    def test_student_api_no_e_forms(self):
        assert not self.api_student_page.student_e_forms(test_student)

    def test_student_api_no_notes(self):
        assert not self.api_student_page.student_notes(test_student)

    def test_student_page_no_course_site_details(self):
        self.student_page.expand_all_years()
        assert not self.student_page.elements(self.student_page.CLASS_PAGE_LINKS)
        assert not self.student_page.elements(self.student_page.SITE_HEADING)
        assert not self.student_page.elements(self.student_page.SITE_ASSIGNMENTS_HEADER)
        assert not self.student_page.elements(self.student_page.SITE_GRADES_HEADER)

    def test_student_api_no_site_data(self):
        assert not self.api_student_page.student_sites(test_student)

    def test_class_page_verboten(self):
        self.class_page.hit_class_page_url('2178', '13826')
        self.class_page.wait_for_403()

    def test_class_api_verboten(self):
        assert self.api_section_page.is_unauthorized('2178', '13826')

    def test_cohort_page_no_sites(self):
        self.homepage.load_page()
        self.homepage.click_sidebar_create_filtered()
        self.filtered_students_page.perform_student_search(test.default_cohort)
        self.filtered_students_page.wait_for_student_list()
        assert not self.filtered_students_page.elements(self.filtered_students_page.SITE_ACTIVITY_HEADER)

    def test_group_page_no_sites(self):
        group = Cohort({'name': f'Group {test.test_id}'})
        self.homepage.click_sidebar_create_student_group()
        self.curated_students_page.create_group_with_bulk_sids(group, test.default_cohort.members)
        self.curated_students_page.wait_for_student_list()
        assert not self.curated_students_page.elements(self.curated_students_page.SITE_ACTIVITY_HEADER)

    def test_no_sidebar_admits(self):
        assert not self.homepage.is_present(self.homepage.ALL_ADMITS_LINK)
        assert not self.homepage.is_present(self.homepage.CREATE_ADMIT_GROUP_LINK)

    def test_sidebar_notes(self):
        assert not self.homepage.is_present(self.homepage.BATCH_NOTE_BUTTON)
        assert not self.homepage.is_present(self.homepage.DRAFT_NOTES_LINK)

    def test_no_adv_search(self):
        assert not self.homepage.is_present(self.homepage.OPEN_ADV_SEARCH_BUTTON)

    def test_search_results(self):
        self.homepage.enter_simple_search_and_hit_enter('Math')
        assert self.search_results_page.are_students_in_results()
        assert not self.search_results_page.are_admits_in_results()
        assert not self.search_results_page.are_classes_in_results()
        assert not self.search_results_page.are_notes_in_results()
        assert not self.search_results_page.are_appts_in_results()

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
