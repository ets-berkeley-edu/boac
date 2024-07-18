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
from flask import current_app as app
from selenium.webdriver.common.by import By


class AdmitPage(AdmitPages):
    NAME = By.ID, 'admit-name-header'
    UC_CPID = By.ID, 'admit-apply-uc-cpid'
    SID = By.ID, 'admit-sid'
    UID = By.ID, 'admit-uid'
    BIRTH_DATE = By.ID, 'admit-birthdate'
    FRESH_TRANS = By.ID, 'admit.freshman-or-transfer'
    STATUS = By.ID, 'admit-admit-status'
    SIR = By.ID, 'admit-current-sir'
    COLLEGE = By.ID, 'admit-college'
    TERM = By.ID, 'admit-admit-term'
    EMAIL = By.ID, 'admit-email'
    CAMPUS_EMAIL = By.ID, 'admit-campus-email'
    DAYTIME_PHONE = By.ID, 'admit-daytime-phone'
    MOBILE = By.ID, 'admit-mobile'
    ADDRESS_STREET_1 = By.ID, 'admit-permanent-street-1'
    ADDRESS_STREET_2 = By.ID, 'admit-permanent-street-2'
    ADDRESS_CITY_REGION_POSTAL = By.ID, 'admit-permanent-city-region-postal'
    ADDRESS_COUNTRY = By.ID, 'admit-permanent-country'
    X_ETHNIC = By.ID, 'admit-x-ethnic'
    HISPANIC = By.ID, 'admit-hispanic'
    UREM = By.ID, 'admit-urem'
    RESIDENCY_CAT = By.ID, 'admit-residency-category'
    CITIZEN_STATUS = By.ID, 'admit-us-citizenship-status'
    NON_CITIZEN_STATUS = By.ID, 'admit-us-non-citizen-status'
    CITIZENSHIP = By.ID, 'admit-citizenship-country'
    RESIDENCE_COUNTRY = By.ID, 'admit-permanent-residence-country'
    VISA_STATUS = By.ID, 'admit-non-immigrant-visa-current'
    VISA_PLANNED = By.ID, 'admit-non-immigrant-visa-planned'
    FIRST_GEN_COLLEGE = By.ID, 'admit-first-generation-college'
    PARENT_1_EDUC = By.ID, 'admit-parent-1-education-level'
    PARENT_2_EDUC = By.ID, 'admit-parent-2-education-level'
    PARENT_HIGHEST_EDUC = By.ID, 'admit-highest-parent-education-level'
    GPA_HS_UNWEIGHTED = By.ID, 'admit-gpa-hs-unweighted'
    GPA_HS_WEIGHTED = By.ID, 'admit-gpa-hs-weighted'
    GPA_TRANSFER = By.ID, 'admit-gpa-transfer'
    FEE_WAIVER = By.ID, 'admit-application-fee-waiver-flag'
    FOSTER_CARE = By.ID, 'admit-foster-care-flag'
    FAMILY_SINGLE_PARENT = By.ID, 'admit-family-is-single-parent'
    STUDENT_SINGLE_PARENT = By.ID, 'admit-student-is-single-parent'
    FAMILY_DEPENDENTS = By.ID, 'admit-family-dependents-num'
    STUDENT_DEPENDENTS = By.ID, 'admit-student-dependents-num'
    FAMILY_INCOME = By.ID, 'admit-family-income'
    STUDENT_INCOME = By.ID, 'admit-student-income'
    MILITARY_DEPENDENT = By.XPATH, '//div[text()="Is Military Dependent"]/following-sibling::div'
    MILITARY_STATUS = By.ID, 'admit-military-status'
    RE_ENTRY_STATUS = By.ID, 'admit-reentry-status'
    ATHLETE_STATUS = By.ID, 'admit-athlete-status'
    SUMMER_BRIDGE_STATUS = By.ID, 'admit-summer-bridge-status'
    LAST_SCHOOL_LCFF_PLUS = By.ID, 'admit-last-school-lcff-plus-flag'
    SPECIAL_PGM_CEP = By.ID, 'admit-special-program-cep'

    def hit_page_url(self, admit_csid):
        self.driver.get(f'{boa_utils.get_boa_base_url()}/admit/student/{admit_csid}')

    def load_page(self, admit_csid):
        app.logger.info(f'Loading admit page for CS ID {admit_csid}')
        self.hit_page_url(admit_csid)
        self.wait_for_spinner()
        self.when_present(self.NAME)
        self.hide_boa_footer()

    @staticmethod
    def concatenated_name(admit):
        middle = f' {admit.middle_name}' if admit.middle_name else ''
        return f'{admit.first_name}{middle} {admit.last_name}'

    def student_page_link_loc(self, admit):
        return By.XPATH, f"//a[contains(., \"View {self.concatenated_name(admit)}'s profile page\")]"

    def click_student_page_link(self, admit):
        app.logger.info(f'Clicking the student page link for SID {admit.sid}')
        self.wait_for_page_and_click(self.student_page_link_loc(admit))
