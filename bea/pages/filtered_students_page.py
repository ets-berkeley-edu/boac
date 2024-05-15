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

from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.pages.cohort_and_group_student_pages import CohortAndGroupStudentPages
from bea.pages.curated_modal import CuratedModal
from bea.pages.filtered_students_page_filters import FilteredStudentsPageFilters
from bea.pages.filtered_students_page_results import FilteredStudentsPageResults
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class FilteredStudentsPage(CohortAndGroupStudentPages,
                           FilteredStudentsPageFilters,
                           FilteredStudentsPageResults,
                           CuratedModal):

    def search_and_create_new_student_cohort(self, cohort):
        self.click_sidebar_create_filtered()
        self.perform_student_search(cohort)
        self.create_new_cohort(cohort)

    EVERYONE_COHORT_LINK = By.XPATH, '//h1[text()="Everyone\'s Cohorts"]/../following-sibling::div//a'
    HISTORY_BUTTON = By.XPATH, '//button[contains(text(), "Back to Cohort")]'

    @staticmethod
    def filtered_cohort_base_url(cohort_id):
        return f'{boa_utils.get_boa_base_url()}/cohort/{cohort_id}'

    def load_cohort(self, cohort):
        app.logger.info(f'Loading cohort {cohort.name}')
        self.driver.get(self.filtered_cohort_base_url(cohort.cohort_id))
        self.wait_for_boa_title(cohort.name)

    def hit_non_auth_cohort(self, cohort):
        self.driver.get(self.filtered_cohort_base_url(cohort.cohort_id))
        self.wait_for_404()

    def load_everyone_cohorts_page(self):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/cohorts/all')
        self.wait_for_boa_title('Cohorts')

    def visible_everyone_cohorts(self):
        self.click_view_everyone_cohorts()
        self.wait_for_spinner()
        cohorts = []
        try:
            Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.EVERYONE_COHORT_LINK))
            links = self.elements(self.EVERYONE_COHORT_LINK)
            for link in links:
                cohort = FilteredCohort({
                    'cohort_id': link.get_attribute('href').replace(f'{boa_utils.get_boa_base_url()}/cohort/', ''),
                    'name': link.text,
                })
                cohorts.append(cohort)
        except TimeoutError:
            app.logger.info('No cohorts visible')
        return cohorts

    def click_history(self):
        app.logger.info('Clicking History')
        self.wait_for_element_and_click(self.HISTORY_BUTTON)
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_element_located(self.BACK_TO_COHORT_BUTTON))
