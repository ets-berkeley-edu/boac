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

from bea.pages.admit_pages import AdmitPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class AdmitPage(AdmitPages):

    NAME = By.ID, 'admit-name-header'

    def name(self):
        return self.el_text_if_exists(self.NAME)

    def uc_cpid(self):
        return self.el_text_if_exists((By.ID, 'admit-apply-uc-cpid'))

    def sid(self):
        return self.el_text_if_exists((By.ID, 'admit-sid'))

    def uid(self):
        return self.el_text_if_exists((By.ID, 'admit-uid'))

    def birth_date(self):
        return self.el_text_if_exists((By.ID, 'admit-birthdate'))

    def fresh_trans(self):
        return self.el_text_if_exists((By.ID, 'admit.freshman-or-transfer'))

    def status(self):
        return self.el_text_if_exists((By.ID, 'admit-admit-status'))

    def sir(self):
        return self.el_text_if_exists((By.ID, 'admit-current-sir'))

    def college(self):
        return self.el_text_if_exists((By.ID, 'admit-college'))

    def admit_term(self):
        return self.el_text_if_exists((By.ID, 'admit-admit-term'))

    def email(self):
        return self.el_text_if_exists((By.ID, 'admit-email'))

    def campus_email(self):
        return self.el_text_if_exists((By.ID, 'admit-campus-email'))

    def daytime_phone(self):
        return self.el_text_if_exists((By.ID, 'admit-daytime-phone'))

    def mobile_phone(self):
        return self.el_text_if_exists((By.ID, 'admit-mobile'))

    def address_street_1(self):
        return self.el_text_if_exists((By.ID, 'admit-permanent-street-1'))

    def address_street_2(self):
        return self.el_text_if_exists((By.ID, 'admit-permanent-street-2'))

    def address_city_region_postal(self):
        return self.el_text_if_exists((By.ID, 'admit-permanent-city-region-postal'))

    def address_country(self):
        return self.el_text_if_exists((By.ID, 'admit-permanent-country'))

    def x_ethnic(self):
        return self.el_text_if_exists((By.ID, 'admit-x-ethnic'))

    def hispanic(self):
        return self.el_text_if_exists((By.ID, 'admit-hispanic'))

    def urem(self):
        return self.el_text_if_exists((By.ID, 'admit-urem'))

    def residency_category(self):
        return self.el_text_if_exists((By.ID, 'admit-residency-category'))

    def citizen_status(self):
        return self.el_text_if_exists((By.ID, 'admit-us-citizenship-status'))

    def non_citizen_status(self):
        return self.el_text_if_exists((By.ID, 'admit-us-non-citizen-status'))

    def citizenship(self):
        return self.el_text_if_exists((By.ID, 'admit-citizenship-country'))

    def residence_country(self):
        return self.el_text_if_exists((By.ID, 'admit-permanent-residence-country'))

    def visa_status(self):
        return self.el_text_if_exists((By.ID, 'admit-non-immigrant-visa-current'))

    def visa_planned(self):
        return self.el_text_if_exists((By.ID, 'admit-non-immigrant-visa-planned'))

    def first_gen_college(self):
        return self.el_text_if_exists((By.ID, 'admit-first-generation-college'))

    def parent_1_educ(self):
        return self.el_text_if_exists((By.ID, 'admit-parent-1-education-level'))

    def parent_2_educ(self):
        return self.el_text_if_exists((By.ID, 'admit-parent-2-education-level'))

    def parent_highest_educ(self):
        return self.el_text_if_exists((By.ID, 'admit-highest-parent-education-level'))

    def gpa_hs_unweighted(self):
        return self.el_text_if_exists((By.ID, 'admit-gpa-hs-unweighted'))

    def gpa_hs_weighted(self):
        return self.el_text_if_exists((By.ID, 'admit-gpa-hs-weighted'))

    def gpa_transfer(self):
        return self.el_text_if_exists((By.ID, 'admit-gpa-transfer'))

    def fee_waiver(self):
        return self.el_text_if_exists((By.ID, 'admit-application-fee-waiver-flag'))

    def foster_care(self):
        return self.el_text_if_exists((By.ID, 'admit-foster-care-flag'))

    def family_single_parent(self):
        return self.el_text_if_exists((By.ID, 'admit-family-is-single-parent'))

    def student_single_parent(self):
        return self.el_text_if_exists((By.ID, 'admit-student-is-single-parent'))

    def family_dependents(self):
        return self.el_text_if_exists((By.ID, 'admit-family-dependents-num'))

    def student_dependents(self):
        return self.el_text_if_exists((By.ID, 'admit-student-dependents-num'))

    @staticmethod
    def income(visible_income):
        return visible_income if visible_income == '—' else int(visible_income.replace(',', '').replace('$', ''))

    def family_income(self):
        visible = self.el_text_if_exists((By.ID, 'admit-family-income'))
        return visible and self.income(visible)

    def student_income(self):
        visible = self.el_text_if_exists((By.ID, 'admit-student-income'))
        return visible and self.income(visible)

    def military_dependent(self):
        return self.el_text_if_exists((By.XPATH, '//div[text()="Is Military Dependent"]/following-sibling::div'))

    def military_status(self):
        return self.el_text_if_exists((By.ID, 'admit-military-status'))

    def re_entry_status(self):
        return self.el_text_if_exists((By.ID, 'admit-reentry-status'))

    def athlete_status(self):
        return self.el_text_if_exists((By.ID, 'admit-athlete-status'))

    def summer_bridge_status(self):
        return self.el_text_if_exists((By.ID, 'admit-summer-bridge-status'))

    def last_school_lcff_plus(self):
        return self.el_text_if_exists((By.ID, 'admit-last-school-lcff-plus-flag'))

    def special_program_cep(self):
        return self.el_text_if_exists((By.ID, 'admit-special-program-cep'))

    def hit_page_url(self, admit_csid):
        return self.driver.get(f'{boa_utils.get_boa_base_url()}/admit/student/{admit_csid}')

    def load_page(self, admit_csid):
        app.logger.info(f'Loading admit page for CS ID {admit_csid}')
        self.hit_page_url(admit_csid)
        self.wait_for_spinner()
        self.when_present(self.NAME, utils.get_short_timeout())
        self.hide_boa_footer()

    @staticmethod
    def concatenated_name(admit):
        middle = f' {admit.middle_name}' if admit.middle_name else ''
        return f'{admit.first_name}{middle} {admit.last_name}'

    @staticmethod
    def student_page_link_loc():
        return By.XPATH, '//a[contains(@id, "link-to-student")]'

    def click_student_page_link(self, admit):
        app.logger.info(f'Clicking the student page link for SID {admit.sid}')
        self.wait_for_page_and_click(self.student_page_link_loc())
