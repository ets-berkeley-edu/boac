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

from bea.pages.search_form import SearchForm
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class BoaPages(SearchForm):

    SPINNER = (By.ID, 'spinner-when-loading')
    MODAL = (By.CLASS_NAME, 'modal-content')
    NOT_FOUND = (By.XPATH, '//img[@alt="A silly boarding pass with the text, \'Error 404: Flight not found\'"]')

    def wait_for_spinner(self):
        time.sleep(1)
        try:
            if self.is_present(BoaPages.SPINNER):
                self.when_not_visible(BoaPages.SPINNER, utils.get_medium_timeout())
        except StaleElementReferenceException as e:
            app.logger.debug(f'{e}')

    def wait_for_boa_title(self, string):
        self.wait_for_title(f'{string} | BOA')

    def wait_for_404(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.visibility_of_element_located(self.NOT_FOUND))

    # HEADER

    HOME_LINK = (By.ID, 'home-header')
    HEADER_DROPDOWN = (By.ID, 'header-dropdown-under-name__BV_toggle_')
    FLIGHT_DATA_RECORDER_LINK = (By.ID, 'header-menu-analytics')
    FLIGHT_DECK_LINK = (By.ID, 'header-menu-flight-deck')
    PAX_MANIFEST_LINK = (By.ID, 'header-menu-passengers')
    PROFILE_LINK = (By.ID, 'header-menu-profile')
    FEEDBACK_LINK = (By.XPATH, '//a[contains(text(), "Feedback/Help")]')
    LOG_OUT_LINK = (By.XPATH, '//a[contains(text(), "Log Out")]')
    CONFIRM_DELETE_OR_DISCARD = (By.ID, 'are-you-sure-confirm')
    CANCEL_DELETE_OR_DISCARD = (By.ID, 'are-you-sure-cancel')
    STUDENT_NAME_HEADING = (By.ID, 'student-name-header')

    SERVICE_ALERT_BANNER = By.ID, 'service-announcement-banner'
    DISMISS_ALERT_BUTTON = By.ID, 'dismiss-service-announcement'

    def click_header_dropdown(self):
        self.wait_for_element_and_click(BoaPages.HEADER_DROPDOWN)

    def open_menu(self):
        if not self.is_present(BoaPages.LOG_OUT_LINK) or not self.element(BoaPages.LOG_OUT_LINK).is_displayed():
            app.logger.info('Clicking header menu button')
            self.click_header_dropdown()

    def log_out(self):
        app.logger.info('Logging out')
        if not self.is_present(BoaPages.HEADER_DROPDOWN):
            self.driver.get(f'{boa_utils.get_boa_base_url()}')
        self.open_menu()
        self.wait_for_element_and_click(BoaPages.LOG_OUT_LINK)

        # In case logout doesn't work the first time, try again
        time.sleep(2)
        if self.is_present(BoaPages.LOG_OUT_LINK):
            if not self.element(BoaPages.LOG_OUT_LINK).is_displayed():
                self.open_menu()
                self.wait_for_element_and_click(BoaPages.LOG_OUT_LINK)
            time.sleep(2)

        self.wait_for_boa_title('Welcome')

    def confirm_delete_or_discard(self):
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)

    def cancel_delete_or_discard(self):
        self.wait_for_element_and_click(self.CANCEL_DELETE_OR_DISCARD)

    # SIDEBAR - FILTERED COHORTS

    CREATE_FILTERED_COHORT_LINK = (By.ID, 'cohort-create')
    VIEW_EVERYONE_COHORTS_LINK = (By.ID, 'cohorts-all')
    FILTERED_COHORT_LINK = (By.XPATH, '//a[contains(@id,"sidebar-cohort")]')
    DUPE_FILTERED_NAME_MSG = (
        By.XPATH,
        '//div[contains(text(), "You have an existing cohort with this name. Please choose a different name.")]')

    def click_sidebar_create_filtered(self):
        app.logger.info('Clicking sidebar button to create a filtered cohort')
        self.wait_for_page_and_click(self.CREATE_FILTERED_COHORT_LINK)
        self.wait_for_boa_title('Create Cohort')
        time.sleep(utils.get_click_sleep())

    def click_view_everyone_cohorts(self):
        time.sleep(1)
        self.wait_for_page_and_click(self.VIEW_EVERYONE_COHORTS_LINK)
        self.wait_for_boa_title('All Cohorts')

    def click_sidebar_filtered_link(self, cohort):
        links = self.elements(self.FILTERED_COHORT_LINK)
        link = next(filter(lambda el: el.text == cohort.name, links))
        link.click()

    @staticmethod
    def sidebar_member_count_loc(cohort):
        if cohort.__class__.__name__ == 'FilteredCohort':
            return By.XPATH, f'//a[contains(@id,"sidebar-cohort")][contains(.,"{cohort.name}")]/div[contains(@id, "count")]'
        else:
            return By.XPATH, f'//a[contains(@id,"sidebar-curated")][contains(.,"{cohort.name}")]/div[contains(@id, "count")]'

    def wait_for_sidebar_member_count(self, cohort):
        app.logger.info(f'Waiting for cohort {cohort.name} member count of {len(cohort.members)}')
        tries = utils.get_short_timeout()
        while tries > 0:
            try:
                tries -= 1
                Wait(self.driver, utils.get_short_timeout()).until(
                    ec.presence_of_element_located(self.sidebar_member_count_loc(cohort)),
                )
                el = self.element(self.sidebar_member_count_loc(cohort))
                visible = el.text.replace(' admitted', '').replace(' students', '')
                assert visible and visible.split()[0] == f'{len(cohort.members)}'
                break
            except (AssertionError, TimeoutError):
                if tries == 0:
                    raise
                else:
                    time.sleep(1)

    #   SIDEBAR - CURATED GROUPS

    CREATE_CURATED_GROUP_LINK = By.ID, 'create-curated-group-from-sidebar'
    VIEW_EVERYONE_GROUPS_LINK = By.ID, 'groups-all'
    SIDEBAR_GROUP_LINK = By.XPATH, '//a[contains(@id, "sidebar-curated-group")]'
    SIDEBAR_GROUP_NAME = By.XPATH, '//a[contains(@id, "sidebar-curated-group")]/div'

    CREATE_ADMIT_GROUP_LINK = By.ID, 'create-admissions-group-from-sidebar'
    SIDEBAR_ADMIT_GROUP_LINK = By.XPATH, '//a[contains(@id, "sidebar-admissions-group")]'

    def click_sidebar_create_student_group(self):
        app.logger.info('Clicking sidebar button to create a curated group')
        self.wait_for_page_and_click(self.CREATE_CURATED_GROUP_LINK)
        time.sleep(1)

    def click_sidebar_create_admit_group(self):
        app.logger.info('Clicking sidebar button to create an admit group')
        self.wait_for_page_and_click(self.CREATE_ADMIT_GROUP_LINK)
        time.sleep(1)

    def sidebar_student_groups(self):
        time.sleep(utils.get_click_sleep())
        return list(map(lambda a: a.text, self.elements(self.SIDEBAR_GROUP_NAME)))

    def sidebar_admit_groups(self):
        time.sleep(utils.get_click_sleep())
        return list(map(lambda a: a.text, self.elements(self.SIDEBAR_ADMIT_GROUP_LINK)))

    def click_view_everyone_groups(self):
        time.sleep(1)
        self.wait_for_page_and_click(self.VIEW_EVERYONE_GROUPS_LINK)
        self.wait_for_boa_title('All Groups')

    def click_sidebar_group_link(self, group):
        els = self.elements(self.SIDEBAR_ADMIT_GROUP_LINK) if group.is_ce3 else self.elements(self.SIDEBAR_GROUP_LINK)
        link = next(filter(lambda a: a.text == group.name, els))
        link.click()

    def wait_for_sidebar_group(self, group):
        # TODO - remove the page reload when groups dynamically appear in the sidebar
        self.reload_page()
        self.wait_for_sidebar_member_count(group)
        if group.is_ce3:
            assert group.name in self.sidebar_admit_groups()
        else:
            assert group.name in self.sidebar_student_groups()

    # BOX_PLOTS

    @staticmethod
    def boxplot_xpath():
        return '//*[name()="svg"]/*[name()="g"][@class="highcharts-series-group"]'

    def boxplot_trigger_xpath(self):
        return f'{self.boxplot_xpath()}/*[name()="g"]/*[name()="g"]/*[name()="path"][3]'

    # BATCH NOTES

    BATCH_NOTE_BUTTON = By.ID, 'batch-note-button'

    # SID LIST ENTRY

    def enter_sid_list(self, el, sids):
        app.logger.info(f'Entering SIDs {sids}')
        self.wait_for_textbox_and_type(el, sids)

    def enter_comma_sep_sids(self, el, students):
        sids = list(map(lambda s: s.sid, students))
        string = ', '.join(sids)
        self.enter_sid_list(el, string)

    def enter_line_sep_sids(self, el, students):
        sids = list(map(lambda s: s.sid, students))
        string = '\n'.join(sids)
        self.enter_sid_list(el, string)

    def enter_space_sep_sids(self, el, students):
        sids = list(map(lambda s: s.sid, students))
        string = ' '.join(sids)
        self.enter_sid_list(el, string)
