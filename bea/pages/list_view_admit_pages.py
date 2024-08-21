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
import time

from bea.pages.admit_pages import AdmitPages
from bea.pages.pagination import Pagination
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class ListViewAdmitPages(Pagination, AdmitPages):

    @staticmethod
    def admit_row_xpath(admit):
        return f'//a[contains(@href, "/admit/student/{admit.sid}")]/ancestor::tr'

    def visible_admit_row_text(self, admit, node, label_text=None):
        loc = By.XPATH, f'{self.admit_row_xpath(admit)}/td[{node}]'
        return self.element(loc).text.replace(label_text, '').strip() if self.is_present(loc) else None

    def visible_admit_name(self, admit):
        loc = By.ID, f'link-to-admit-{admit.sid}'
        return self.element(loc).text if self.is_present(loc) else None

    def visible_admit_sid(self, admit):
        return self.visible_admit_row_text(admit, 3, 'C S I D')

    def visible_admit_sir(self, admit):
        return self.visible_admit_row_text(admit, 4, 'S I R')

    def visible_admit_cep(self, admit):
        return self.visible_admit_row_text(admit, 5, 'C E P')

    def visible_admit_re_entry(self, admit):
        return self.visible_admit_row_text(admit, 6, 'Re-entry')

    def visible_admit_1st_gen_college(self, admit):
        return self.visible_admit_row_text(admit, 7, 'First generation')

    def visible_admit_urem(self, admit):
        return self.visible_admit_row_text(admit, 8, 'U R E M')

    def visible_admit_fee_waiver(self, admit):
        return self.visible_admit_row_text(admit, 9, 'Waiver')

    def visible_admit_residency(self, admit):
        return self.visible_admit_row_text(admit, 10, 'Residency')

    def visible_admit_fresh_trans(self, admit):
        return self.visible_admit_row_text(admit, 11, 'Freshman or Transfer')

    @staticmethod
    def last_updated_msg_loc():
        return By.XPATH, '//div[contains(text(), "Admit data was last updated on")]'

    def verify_admit_row_data(self, admit, failures):
        try:
            app.logger.info(f'Checking visible data for CS ID {admit.sid}')
            admit_data = admit.admit_data
            utils.assert_equivalence(self.visible_admit_cep(admit), (admit_data['special_program_cep'] or 'No data'))
            utils.assert_equivalence(self.visible_admit_re_entry(admit), admit_data['reentry_status'])
            utils.assert_equivalence(
                self.visible_admit_1st_gen_college(admit), (admit_data['first_generation_college'] or '—\nNo data'))
            utils.assert_equivalence(self.visible_admit_urem(admit), admit_data['urem'])
            utils.assert_equivalence(
                self.visible_admit_fee_waiver(admit), ('Fee' if admit_data['application_fee_waiver_flag'] else '—\nNo data'))
            utils.assert_equivalence(self.visible_admit_fresh_trans(admit), admit_data['freshman_or_transfer'])
            utils.assert_equivalence(self.visible_admit_residency(admit), admit_data['residency_category'])
        except AssertionError:
            failures.append(admit.sid)
        return failures

    def click_admit_link(self, cs_id):
        app.logger.info(f'Clicking the link for CS ID {cs_id}')
        self.wait_for_element_and_click((By.ID, f'link-to-admit-{cs_id}'))

    # LIST VIEW - COHORT/GROUP

    ADMIT_COHORT_SID = By.XPATH, '//span[contains(@id, "-cs-empl-id")]'

    def admit_cohort_row_sids(self):
        return [el.text for el in self.elements(self.ADMIT_COHORT_SID)]

    def wait_for_admit_sids(self):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_all_elements_located(self.ADMIT_COHORT_SID))

    def list_view_admit_sids(self, cohort):
        if cohort.members:
            visible_sids = []
            time.sleep(1)
            page_count = self.list_view_page_count()
            page = 1
            visible_sids.extend(self.admit_cohort_row_sids())
            if page_count == 1:
                app.logger.info('There is 1 page')
            else:
                app.logger.info(f'There are {page_count} pages')
                for i in range(page_count - 1):
                    page += 1
                    self.wait_for_element_and_click(self.go_to_page_link(page))
                    self.wait_for_admit_sids()
                    visible_sids.extend(self.admit_cohort_row_sids())
            return visible_sids

    # ADMIT ADD-TO-GRP

    ADMIT_ROW_CBX = By.XPATH, '//input[contains(@id, "-admissions-group-checkbox")]'

    def admit_row_cbx_sids(self):
        return [el.get_attribute('id').split('-')[1] for el in self.elements(self.ADMIT_ROW_CBX)]

    def wait_for_admit_checkboxes(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.ADMIT_ROW_CBX))

    def admits_available_to_add_to_grp(self, test, group):
        group_sids = list(map(lambda m: m.sid, group.members))
        self.wait_for_admit_checkboxes()
        visible_sids = self.admit_row_cbx_sids()
        available_sids = [sid for sid in visible_sids if sid not in group_sids]
        return [admit for admit in test.admits if admit.sid in available_sids]
