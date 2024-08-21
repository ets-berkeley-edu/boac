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

from bea.pages.cohort_and_group_admit_pages import CohortAndGroupAdmitPages
from bea.pages.curated_add_selector import CuratedAddSelector
from bea.pages.curated_modal import CuratedModal
from bea.pages.filtered_students_page_filters import FilteredStudentsPageFilters
from bea.pages.filtered_students_page_results import FilteredStudentsPageResults
from bea.pages.list_view_admit_pages import ListViewAdmitPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class FilteredAdmitsPage(CohortAndGroupAdmitPages,
                         ListViewAdmitPages,
                         FilteredStudentsPageFilters,
                         FilteredStudentsPageResults,
                         CuratedAddSelector,
                         CuratedModal):

    CREATE_COHORT_BUTTON = By.ID, 'admitted-students-cohort-create'
    DEPEND_CHAR_ERROR_MSG = By.XPATH, '//div[text()="Dependents must be an integer greater than or equal to 0."]'
    DEPEND_LOGIC_ERROR_MSG = By.XPATH, '//div[text()="Dependents inputs must be in ascending order."]'

    def load_cohort(self, cohort):
        app.logger.info(f'Loading CE3 cohort {cohort.name}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/cohort/{cohort.cohort_id}')
        self.wait_for_boa_title(cohort.name)

    def click_create_cohort(self):
        app.logger.info('Clicking the Create Cohort button')
        self.wait_for_page_and_click(self.CREATE_COHORT_BUTTON)

    def perform_admit_search(self, cohort):
        for fresh_trans in cohort.search_criteria.freshman_or_transfer:
            self.select_new_filter('Freshman or Transfer', fresh_trans)
        if cohort.search_criteria.current_sir:
            self.select_new_filter('Current SIR')
        for college in cohort.search_criteria.colleges:
            self.select_new_filter('College', college)
        for xeth in cohort.search_criteria.xethnic:
            self.select_new_filter('XEthnic', xeth)
        if cohort.search_criteria.hispanic:
            self.select_new_filter('Hispanic')
        if cohort.search_criteria.urem:
            self.select_new_filter('UREM')
        if cohort.search_criteria.first_gen_college:
            self.select_new_filter('First Generation College')
        if cohort.search_criteria.fee_waiver:
            self.select_new_filter('Application Fee Waiver')
        for res in cohort.search_criteria.residency:
            self.select_new_filter('Residency', res)
        if cohort.search_criteria.foster_care:
            self.select_new_filter('Foster Care')
        if cohort.search_criteria.family_single_parent:
            self.select_new_filter('Family Is Single Parent')
        if cohort.search_criteria.student_single_parent:
            self.select_new_filter('Student Is Single Parent')
        for f_dep in cohort.search_criteria.family_dependents:
            self.select_new_filter('Family Dependents', f_dep)
        for s_dep in cohort.search_criteria.student_dependents:
            self.select_new_filter('Student Dependents', s_dep)
        if cohort.search_criteria.re_entry_status:
            self.select_new_filter('Re-entry Status')
        if cohort.search_criteria.last_school_lcff_plus:
            self.select_new_filter('Last School LCFF+')
        for cep in cohort.search_criteria.special_program_cep:
            self.select_new_filter('Special Program CEP', cep)

        self.execute_search()

    def verify_admit_filters_present(self, cohort):
        filters = cohort.search_criteria
        has_non_empty_filters = any([True for k, v in filters.data.items() if v])
        if filters and has_non_empty_filters:
            self.show_filters()
            Wait(self.driver, utils.get_short_timeout()).until(
                ec.presence_of_all_elements_located(self.COHORT_FILTER_ROW))
            for c in filters.colleges:
                assert self.is_present(self.existing_filter_loc('College', c))
            if filters.current_sir:
                assert self.is_present(self.existing_filter_loc('Current SIR'))
            for f_dep in filters.family_dependents:
                assert self.is_present(self.existing_filter_loc('Family Dependents', f_dep))
            if filters.family_single_parent:
                assert self.is_present(self.existing_filter_loc('Family Is Single Parent'))
            if filters.fee_waiver:
                assert self.is_present(self.existing_filter_loc('Application Fee Waiver'))
            if filters.first_gen_college:
                assert self.is_present(self.existing_filter_loc('First Generation College'))
            if filters.foster_care:
                assert self.is_present(self.existing_filter_loc('Foster Care'))
            for fr in filters.freshman_or_transfer:
                assert self.is_present(self.existing_filter_loc('Freshman or Transfer', fr))
            if filters.hispanic:
                assert self.is_present(self.existing_filter_loc('Hispanic'))
            if filters.last_school_lcff_plus:
                assert self.is_present(self.existing_filter_loc('Last School LCFF+'))
            if filters.re_entry_status:
                assert self.is_present(self.existing_filter_loc('Re-entry Status'))
            for res in filters.residency:
                assert self.is_present(self.existing_filter_loc('Residency', res))
            for pro in filters.special_program_cep:
                assert self.is_present(self.existing_filter_loc('Special Program CEP', pro))
            for s_dep in filters.student_dependents:
                assert self.is_present(self.existing_filter_loc('Student Dependents', s_dep))
            if filters.student_single_parent:
                assert self.is_present(self.existing_filter_loc('Student Is Single Parent'))
            if filters.urem:
                assert self.is_present(self.existing_filter_loc('UREM'))
            for eth in filters.xethnic:
                assert self.is_present(self.existing_filter_loc('XEthnic', eth))

        else:
            self.when_not_visible(self.UNSAVED_FILTER_APPLY_BUTTON, utils.get_short_timeout())
            assert not self.elements(self.COHORT_FILTER_ROW)
