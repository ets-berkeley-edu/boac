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

import re
import time

from bea.pages.class_page import ClassPage
from bea.pages.curated_add_selector import CuratedAddSelector
from bea.pages.student_page_advising_note import StudentPageAdvisingNote
from bea.pages.student_page_appointment import StudentPageAppointment
from bea.pages.student_page_e_form import StudentPageEForm
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class StudentPage(CuratedAddSelector, StudentPageAdvisingNote, StudentPageAppointment, StudentPageEForm):

    def load_page(self, student):
        app.logger.info(f'Loading student page for UID {student.uid}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/student/{student.uid}')
        self.wait_for_spinner()

    NOT_FOUND_MSG = By.XPATH, '//h1[text()="Not Found"]'
    TOGGLE_PERSONAL_DETAILS = By.ID, 'show-hide-personal-details'
    ADDITIONAL_INFO_OUTER = By.XPATH, '//h3[text()=" Advisor(s) "]'

    def is_personal_details_expanded(self):
        return self.is_present(self.ADDITIONAL_INFO_OUTER) and self.element(self.ADDITIONAL_INFO_OUTER).is_displayed()

    def expand_personal_details(self):
        self.when_present(self.TOGGLE_PERSONAL_DETAILS, utils.get_medium_timeout())
        if self.is_personal_details_expanded():
            app.logger.info('Personal details tab is already expanded')
        else:
            app.logger.info('Expanding personal details tab')
            self.wait_for_element_and_click(self.TOGGLE_PERSONAL_DETAILS)
            self.when_present(self.ADDITIONAL_INFO_OUTER, utils.get_medium_timeout())
        time.sleep(1)

    # SIS PROFILE DATA

    ACADEMIC_STANDING = By.XPATH, '//span[contains(@id, "academic-standing-term-")]'
    ADVISOR_EMAIL = By.XPATH, '//div[@id="student-profile-advisors"]//div[contains(@id,"-email")]'
    ADVISOR_NAME = By.XPATH, '//div[@id="student-profile-advisors"]//div[contains(@id,"-name")]'
    ADVISOR_PLAN = By.XPATH, '//div[@id="student-profile-advisors"]//div[contains(@id,"-plan")]'
    COLLEGE = By.XPATH, '//div[@id="student-bio-majors"]//div[@class="text-medium-emphasis"]'
    CUMULATIVE_UNITS = By.ID, 'cumulative-units'
    CUMULATIVE_GPA = By.ID, 'cumulative-gpa'
    DISCONTINUED_COLLEGE = By.XPATH, '//div[@id="student-details-discontinued-majors"]//div[@class="text-medium-emphasis"]'
    DISCONTINUED_MAJOR = By.XPATH, '//div[@id="student-details-discontinued-majors"]//div[@class="font-weight-bold"]'
    DISCONTINUED_MINOR = By.XPATH, '//div[@id="student-details-discontinued-minors"]//div[@class="font-weight-bold"]'
    EMAIL = By.ID, 'student-mailto'
    EMAIL_ALTERNATE = By.ID, 'student-profile-other-email'
    ENTERED_TERM = By.ID, 'student-bio-matriculation'
    EXPECTED_GRADUATION = By.ID, 'student-bio-expected-graduation'
    INACTIVE = By.ID, 'student-bio-inactive'
    INACTIVE_ASC_FLAG = By.ID, 'student-bio-inactive-asc'
    INACTIVE_COE_FLAG = By.ID, 'student-bio-inactive-coe'
    INTENDED_MAJOR = By.XPATH, '//div[@id="student-details-intended-majors"]/div'
    LEVEL = By.XPATH, '//div[@id="student-bio-level"]/div'
    MAJOR = By.XPATH, '//div[@id="student-bio-majors"]//div[@class="font-weight-bold"]'
    MINOR = By.XPATH, '//div[@id="student-bio-minors"]//div[@class="font-weight-bold"]'
    PHONE = By.ID, 'student-phone-number'
    PREFERRED_NAME = By.XPATH, '//div[@id="student-preferred-name"]/span[2]'
    SID = By.XPATH, '//div[@id="student-bio-sid"]/span'
    SQUAD = By.XPATH, '//div[@id="student-bio-athletics"]/div'
    SUB_PLAN = By.XPATH, '//div[@id="student-bio-subplans"]/div'
    TERMS_IN_ATTENDANCE = By.ID, 'student-bio-terms-in-attendance'
    TRANSFER = By.ID, 'student-profile-transfer'
    VISA = By.ID, 'student-profile-visa'

    @staticmethod
    def calcentral_link(student):
        return By.XPATH, f'//a[@href="https://calcentral.berkeley.edu/user/overview/{student.uid}"]'

    @staticmethod
    def perceptive_link():
        return By.XPATH, '//a[contains(text(), "Perceptive Content (Image Now) documents")]'

    def academic_standing(self):
        return self.el_text_if_exists(self.ACADEMIC_STANDING)

    def advisor_plans(self):
        return self.els_text_if_exist(self.ADVISOR_PLAN)

    def advisor_names(self):
        return self.els_text_if_exist(self.ADVISOR_NAME)

    def advisor_emails(self):
        return self.els_text_if_exist(self.ADVISOR_EMAIL)

    def colleges(self):
        return self.els_text_if_exist(self.COLLEGE)

    def colleges_discontinued(self):
        return self.els_text_if_exist(self.DISCONTINUED_COLLEGE)

    def cumulative_units(self):
        return self.el_text_if_exists(self.CUMULATIVE_UNITS, 'UNITS COMPLETED')

    def cumulative_gpa(self):
        return self.el_text_if_exists(self.CUMULATIVE_GPA, 'No data')

    def degree(self, field):
        time.sleep(1)
        xpath = f'//h3[contains(text(), "Degree")]/following-sibling::div[contains(., "{field}")]'
        deg_type_loc = By.XPATH, f'{xpath}/div[contains(@id, "student-bio-degree-type")]'
        deg_date_loc = By.XPATH, f'{xpath}/div[contains(@class, "text-medium-emphasis")][1]'
        deg_college_loc_1 = By.XPATH, f'{xpath}/div[contains(@class, "text-medium-emphasis")][2]'
        deg_college_loc_2 = By.XPATH, f'{xpath}/div[contains(@class, "text-medium-emphasis")][3]'
        college = self.el_text_if_exists(deg_college_loc_1) or self.el_text_if_exists(deg_college_loc_2)
        return {
            'deg_type': self.el_text_if_exists(deg_type_loc),
            'deg_date': self.el_text_if_exists(deg_date_loc),
            'deg_college': college,
        }

    def degree_minor(self, field):
        xpath = '//h3[contains(text(), "Minor")]/following-sibling::'
        min_type_loc = By.XPATH, f'{xpath}div[contains(., "{field}")]/div'
        min_date_loc = By.XPATH, f'{xpath}span'
        return {
            'min_type': self.el_text_if_exists(min_type_loc),
            'min_date': self.el_text_if_exists(min_date_loc),
        }

    def email(self):
        return self.element(self.EMAIL).text.split()[3] if self.is_present(self.EMAIL) else None

    def email_alternate(self):
        return self.el_text_if_exists(self.EMAIL_ALTERNATE)

    def entered_term(self):
        return self.el_text_if_exists(self.ENTERED_TERM, 'Entered')

    def expected_graduation(self):
        return self.el_text_if_exists(self.EXPECTED_GRADUATION, 'Expected graduation')

    def intended_majors(self):
        return self.els_text_if_exist(self.INTENDED_MAJOR)

    def is_inactive(self):
        return self.is_present(self.INACTIVE) and self.el_text_if_exists(self.INACTIVE) == 'INACTIVE'

    def level(self):
        return self.el_text_if_exists(self.LEVEL)

    def majors(self):
        return self.els_text_if_exist(self.MAJOR)

    def majors_discontinued(self):
        return self.els_text_if_exist(self.DISCONTINUED_MAJOR)

    def minors(self):
        return self.els_text_if_exist(self.MINOR)

    def minors_discontinued(self):
        return self.els_text_if_exist(self.DISCONTINUED_MINOR)

    def name(self):
        return self.el_text_if_exists(self.STUDENT_NAME_HEADING)

    def phone(self):
        return self.el_text_if_exists(self.PHONE)

    def preferred_name(self):
        return self.el_text_if_exists(self.PREFERRED_NAME)

    def sid(self):
        return self.el_text_if_exists(self.SID)

    def sports(self):
        time.sleep(1)
        return self.els_text_if_exist(self.SQUAD)

    def sub_plans(self):
        return self.els_text_if_exist(self.SUB_PLAN)

    def transfer(self):
        return self.el_text_if_exists(self.TRANSFER)

    def terms_in_attendance(self):
        return self.el_text_if_exists(self.TERMS_IN_ATTENDANCE, 'Terms in Attendance')

    def visa(self):
        return self.el_text_if_exists(self.VISA)

    # TIMELINE

    TIMELINE_LOADED_MSG = By.XPATH, '//div[text()="Academic Timeline has loaded"]'
    TIMELINE_ALL_BUTTON = By.ID, 'timeline-tab-all'
    SHOW_HIDE_ALL_BUTTON = By.ID, 'timeline-tab-all-previous-messages'

    def wait_for_timeline(self):
        self.when_visible(self.TIMELINE_ALL_BUTTON, utils.get_short_timeout())

    # Requirements

    REQTS_BUTTON = By.ID, 'timeline-tab-requirement'
    SHOW_HIDE_REQTS_BUTTON = By.ID, 'timeline-tab-requirement-previous-messages'
    WRITING_REQT = By.XPATH, '//span[contains(text(),"Entry Level Writing")]'
    HISTORY_REQT = By.XPATH, '//span[contains(text(),"American History")]'
    INSTITUTIONS_REQT = By.XPATH, '//span[contains(text(),"American Institutions")]'
    CULTURES_REQT = By.XPATH, '//span[contains(text(),"American Cultures")]'

    def show_reqts(self):
        if self.is_present(self.REQTS_BUTTON) and self.element(self.REQTS_BUTTON).is_enabled():
            self.wait_for_element_and_click(self.REQTS_BUTTON)

    def visible_writing_reqt(self):
        self.show_reqts()
        return self.el_text_if_exists(self.WRITING_REQT)

    def visible_history_reqt(self):
        self.show_reqts()
        return self.el_text_if_exists(self.HISTORY_REQT)

    def visible_institutions_reqt(self):
        self.show_reqts()
        return self.el_text_if_exists(self.INSTITUTIONS_REQT)

    def visible_cultures_reqt(self):
        self.show_reqts()
        return self.el_text_if_exists(self.CULTURES_REQT)

    # Holds

    HOLDS_BUTTON = By.ID, 'timeline-tab-hold'
    SHOW_HIDE_HOLDS_BUTTON = By.ID, 'timeline-tab-hold-previous-messages'
    HOLD = By.XPATH, '//div[contains(@id,"timeline-tab-hold-message")]/span[2]'

    def visible_holds(self):
        if self.is_present(self.HOLDS_BUTTON) and self.element(self.HOLDS_BUTTON).is_enabled():
            self.wait_for_element_and_click(self.HOLDS_BUTTON)
        if self.is_present(self.SHOW_HIDE_HOLDS_BUTTON) and 'Show' in self.element(self.SHOW_HIDE_HOLDS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_HOLDS_BUTTON)
        return list(map(lambda el: re.sub(r'\W+', '', el.text), self.elements(self.HOLD)))

    # Alerts

    ALERTS_BUTTON = By.ID, 'timeline-tab-alert'
    SHOW_HIDE_ALERTS_BUTTON = By.ID, 'timeline-tab-alert-previous-messages'
    ALERT = By.XPATH, '//tr[contains(@id, "permalink-alert-")]'
    ALERT_TEXT = By.XPATH, '//div[contains(@id,"timeline-tab-alert-message")]/span[1]'
    ALERT_DATE = By.XPATH, '//tr[contains(@id, "permalink-alert-")]//div[contains(@id, "collapsed-alert-")][contains(@id, "-created-at")]'

    def visible_alerts(self):
        if self.is_present(self.HOLDS_BUTTON) and self.element(self.HOLDS_BUTTON).is_enabled():
            self.wait_for_element_and_click(self.HOLDS_BUTTON)
        if self.is_present(self.SHOW_HIDE_HOLDS_BUTTON) and 'Show' in self.element(self.SHOW_HIDE_HOLDS_BUTTON).text:
            self.wait_for_element_and_click(self.SHOW_HIDE_HOLDS_BUTTON)
        alerts = []
        alert_els = self.elements(self.ALERT)
        alert_text_els = self.elements(self.ALERT_TEXT)
        alert_date_els = self.elements(self.ALERT_DATE)
        for el in alert_els:
            idx = alert_els.index(el)
            alerts.append({
                'text': alert_text_els[idx].text.strip(),
                'date': alert_date_els[idx].text.replace('Last updated on', '').strip(),
            })
        return alerts

    # Notes - see StudentPageAdvisingNote

    # TERM DATA

    DEGREE_CHECKS_LINK = By.ID, 'view-degree-checks-link'
    WITHDRAWAL_MSG = By.XPATH, '//span[contains(@id, "withdrawal-term-")]'
    TOGGLE_COLLAPSE_ALL_YEARS = By.ID, 'toggle-collapse-all-years'

    def click_degree_checks_button(self):
        app.logger.info('Clicking the degree checks link')
        current_windows = self.driver.window_handles
        self.wait_for_element_and_click(self.DEGREE_CHECKS_LINK)
        Wait(self.driver, 2).until(ec.new_window_is_opened(current_windows))
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    @staticmethod
    def term_data_xpath(term_name):
        return f'//h3[text()="{term_name}"]'

    def term_data_heading(self, term_name):
        return By.XPATH, self.term_data_xpath(term_name)

    def click_expand_collapse_years_toggle(self):
        self.wait_for_element_and_click(self.TOGGLE_COLLAPSE_ALL_YEARS)

    def expand_all_years(self):
        if self.is_present(self.TOGGLE_COLLAPSE_ALL_YEARS) and 'Expand' in self.element(self.TOGGLE_COLLAPSE_ALL_YEARS).text:
            self.wait_for_element_and_click(self.TOGGLE_COLLAPSE_ALL_YEARS)

    def expand_academic_year(self, term_name):
        if self.is_visible(self.term_data_heading(term_name)):
            app.logger.info(f'Row containing {term_name} is already expanded')
        else:
            app.logger.info(f'Expanding row containing {term_name}')
            year = int(term_name.split(' ')[-1])
            if 'Fall' in term_name:
                year = year + 1
            self.wait_for_element_and_click((By.ID, f'academic-year-{year}-toggle'))

    def wait_for_term_data(self, term_sis_id):
        self.when_visible((By.ID, f'term-{term_sis_id}-units'), 1)

    def visible_term_units(self, term_sis_id):
        self.wait_for_term_data(term_sis_id)
        return self.el_text_if_exists((By.ID, f'term-{term_sis_id}-units'))

    def visible_term_gpa(self, term_sis_id):
        self.wait_for_term_data(term_sis_id)
        return self.el_text_if_exists((By.ID, f'term-{term_sis_id}-gpa'))

    def visible_term_units_min(self, term_sis_id):
        self.wait_for_term_data(term_sis_id)
        return self.el_text_if_exists((By.ID, f'term-{term_sis_id}-min-units'))

    def visible_term_units_max(self, term_sis_id):
        self.wait_for_term_data(term_sis_id)
        return self.el_text_if_exists((By.ID, f'term-{term_sis_id}-max-units'))

    def visible_term_academic_standing(self, term_sis_id):
        self.wait_for_term_data(term_sis_id)
        return self.el_text_if_exists((By.ID, f'classes-academic-standing-term-{term_sis_id}'))

    def visible_term_concurrent_enrollment(self, term_sis_id):
        self.wait_for_term_data(term_sis_id)
        term_concurrent_enroll_loc = By.XPATH, f'{self.term_data_xpath(term_sis_id)}/following-sibling::span[text()="UCBX"]'
        return self.is_present(term_concurrent_enroll_loc)

    # COURSES

    @staticmethod
    def course_row_id(term_sis_id, ccn):
        return f'term-{term_sis_id}-course-{ccn}'

    def collapsed_course_code(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-name'))

    def collapsed_course_wait_list_flag(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'waitlisted-for-{term_sis_id}-{ccn}'))

    def collapsed_course_midterm_grade(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-midterm-grade'), 'No data')

    def collapsed_course_final_grade(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-final-grade'))

    def is_collapsed_course_final_grade_alert(self, term_sis_id, ccn):
        return self.is_present((By.ID, f'term-{term_sis_id}-course-{ccn}-has-grade-alert'))

    def collapsed_course_units(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-units'))

    def expand_course_data(self, term_sis_id, ccn):
        self.wait_for_element_and_click((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-toggle'))
        time.sleep(utils.get_click_sleep())

    def expanded_course_xpath(self, term_sis_id, ccn):
        return f'//div[@id="{self.course_row_id(term_sis_id, ccn)}-details"]'

    def expanded_course_code(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-details-name'))

    def expanded_course_title(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'{self.course_row_id(term_sis_id, ccn)}-title'))

    def expanded_course_sections(self, term_sis_id, ccn):
        xpath = f'//div[@id="term-{term_sis_id}-course-{ccn}-details-name"]/following-sibling::div'
        return self.el_text_if_exists((By.XPATH, xpath))

    def expanded_course_incomplete_alert(self, term_sis_id, ccn):
        return self.el_text_if_exists((By.ID, f'term-{term_sis_id}-section-{ccn}-has-incomplete-grade'))

    def expanded_course_reqts(self, term_sis_id, ccn):
        xpath = self.expanded_course_xpath(term_sis_id, ccn)
        return self.els_text_if_exist((By.XPATH, f'{xpath}//div[contains(@id, "term-{term_sis_id}-section-{ccn}-meets-")]'))

    CLASS_PAGE_LINKS = By.XPATH, '//a[contains(@href, "/course/")]'

    @staticmethod
    def class_page_link(term_sis_id, ccn):
        return By.ID, f'term-{term_sis_id}-section-{ccn}'

    def click_class_page_link(self, term_sis_id, ccn):
        app.logger.info(f'Clicking link for term {term_sis_id} section {ccn}')
        if not self.is_present(self.class_page_link(term_sis_id, ccn)):
            self.expand_all_years()
            self.expand_course_data(term_sis_id, ccn)
        self.wait_for_element_and_click(self.class_page_link(term_sis_id, ccn))
        self.wait_for_spinner()
        self.when_visible(ClassPage.MEETING_DIV, utils.get_medium_timeout())

    def dropped_section_data(self, term_sis_id, course_code, component, number):
        xpath = f'//div[contains(@id, "term-{term_sis_id}-dropped-course")][contains(.,"{course_code} - {component} {number}")]'
        return self.el_text_if_exists((By.XPATH, xpath))

    # COURSE SITES

    @staticmethod
    def course_site_xpath(term_sis_id, ccn, idx):
        return f'//div[@id="term-{term_sis_id}-course-{ccn}"]/following-sibling::div//h5[@class="bcourses-site-code"][contains(@id, "site-{idx}")]'

    @staticmethod
    def site_analytics_percentile_xpath(site_xpath, label):
        return f'{site_xpath}/following-sibling::table//th[contains(text(), "{label}")]/following-sibling::td[1]'

    @staticmethod
    def site_analytics_score_xpath(site_xpath, label):
        return f'{site_xpath}/following-sibling::table//th[contains(text(), "{label}")]/following-sibling::td[2]'

    def site_boxplot_xpath(self, site_xpath, label):
        return f'{self.site_analytics_score_xpath(site_xpath, label)}{self.boxplot_trigger_xpath()}'

    def analytics_trigger_loc(self, site_xpath, label):
        return By.XPATH, self.site_boxplot_xpath(site_xpath, label)

    def is_no_data_loc(self, site_xpath, label):
        return self.is_present((By.XPATH, f'{self.site_analytics_score_xpath(site_xpath, label)}[contains(., "No Data")]'))

    def perc_round(self, site_xpath, label):
        xpath = f'{self.site_analytics_percentile_xpath(site_xpath, label)}//strong'
        return self.el_text_if_exists((By.XPATH, xpath))

    def graphable_user_score_xpath(self, site_xpath, label):
        return f'{self.site_analytics_score_xpath(site_xpath, label)}//div[text()="User Score"]/following-sibling::div'

    def graphable_user_score(self, site_xpath, label):
        return self.el_text_if_exists((By.XPATH, self.graphable_user_score_xpath(site_xpath, label)))

    def non_graphable_user_score(self, site_xpath, label):
        xpath = f'{self.site_analytics_score_xpath(site_xpath, label)}//strong'
        return self.el_text_if_exists((By.XPATH, xpath))

    def non_graphable_maximum(self, site_xpath, label):
        xpath = f'{self.site_analytics_score_xpath(site_xpath, label)}//span[contains(text(), "Max:")]'
        return self.el_text_if_exists((By.XPATH, xpath))

    def visible_analytics(self, site_xpath, label, analytics):
        boxplot = analytics['graphable']
        if boxplot:
            self.when_present(self.analytics_trigger_loc(site_xpath, label), utils.get_short_timeout())
            app.logger.info(f'Mousing over element at {self.analytics_trigger_loc(site_xpath, label)}')
            self.mouseover(self.element((self.analytics_trigger_loc(site_xpath, label))))
            app.logger.info(f'Checking user score at {self.graphable_user_score(site_xpath, label)}')
            self.when_present(self.graphable_user_score(site_xpath, label), utils.get_short_timeout())
        tool_tip_detail_loc = f'{self.graphable_user_score_xpath(site_xpath, label)}/../following-sibling::div/div'
        visible_details = self.els_text_if_exist(tool_tip_detail_loc)
        app.logger.info(f'Visible details: {visible_details}')
        return {
            'perc_round': self.perc_round(site_xpath, label),
            'score': (self.graphable_user_score(site_xpath, label) if boxplot else self.non_graphable_user_score(site_xpath, label)),
            'max': (visible_details[0] if boxplot and visible_details else self.non_graphable_maximum(site_xpath, label)),
            'perc_70': (visible_details[1] if visible_details else None),
            'perc_50': (visible_details[2] if visible_details else None),
            'perc_30': (visible_details[3] if visible_details else None),
            'minimum': (visible_details[4] if visible_details else None),
        }

    def visible_assignment_analytics(self, site_xpath, analytics):
        return self.visible_analytics(site_xpath, 'Assignments Submitted', analytics)

    def visible_grades_analytics(self, site_xpath, analytics):
        return self.visible_analytics(site_xpath, 'Assignment Grades', analytics)

    def visible_last_activity(self, term_id, ccn, idx):
        xpath = f'{self.course_site_xpath(term_id, ccn, idx)}//th[contains(.,\"Last bCourses Activity\")]/following-sibling::td/div'
        app.logger.info(f'Checking for last activity at {xpath}')
        self.when_present((By.XPATH, xpath), utils.get_click_sleep())
        visible = self.el_text_if_exists((By.XPATH, xpath))
        return {
            'days': (visible.split('.')[0] if visible else None),
            'context': (visible.split('.')[1] if visible else None),
        }
