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

from bea.pages.page import Page
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class SearchForm(Page):

    FILL_IN_FIELD_MSG = (By.XPATH, '//span[contains(text(), "Search input is required")]')

    def clear_input(self, locator):
        self.wait_for_element_and_click(locator)
        time.sleep(utils.get_click_sleep())

    # SIMPLE SEARCH

    SEARCH_INPUT = (By.ID, 'search-students-input')
    SEARCH_BUTTON = (By.ID, 'go-search')

    def enter_simple_search(self, string):
        app.logger.info(f"Searching for '{string}'")
        time.sleep(1)
        self.remove_and_enter_chars(SearchForm.SEARCH_INPUT, string)

    def enter_simple_search_and_hit_enter(self, string):
        self.enter_simple_search(string)
        self.hit_enter()

    def click_simple_search_button(self):
        app.logger.info('Clicking search button')
        self.wait_for_element_and_click(self.SEARCH_BUTTON)

    def clear_simple_search_input(self):
        self.clear_input(self.SEARCH_INPUT)

    # Search history

    SEARCH_HISTORY_ITEM = (By.XPATH, '//div[contains(@id, "search-history-")]')

    def visible_search_history(self):
        time.sleep(1)
        return list(map(lambda el: el.text.strip(), self.elements(self.SEARCH_HISTORY_ITEM)))

    def select_history_item(self, search_string):
        time.sleep(1)
        item = next(filter(lambda el: el.text.strip() == search_string, self.elements(self.SEARCH_HISTORY_ITEM)))
        item.click()

    # ADVANCED SEARCH

    OPEN_ADV_SEARCH_BUTTON = (By.ID, 'search-options-panel-toggle')
    ADV_SEARCH_STUDENT_INPUT = (By.ID, 'advanced-search-students-input')

    def open_adv_search(self):
        app.logger.info('Opening advanced search')
        self.wait_for_element_and_click(self.OPEN_ADV_SEARCH_BUTTON)
        Wait(self.driver, 2).until(ec.visibility_of_element_located(self.ADV_SEARCH_STUDENT_INPUT))

    def clear_adv_search_input(self):
        self.clear_input(self.ADV_SEARCH_STUDENT_INPUT)

    def enter_adv_search(self, string=None):
        string = string or ''
        app.logger.info(f'Searching for "{string}"')
        time.sleep(1)
        self.clear_input(self.ADV_SEARCH_STUDENT_INPUT)
        self.remove_and_enter_chars(self.ADV_SEARCH_STUDENT_INPUT, string)

    def enter_adv_search_and_hit_enter(self, string=None):
        self.enter_adv_search(string)
        self.hit_enter()

    # Search types

    INCLUDE_ADMITS_CBX = (By.ID, 'search-include-admits-checkbox')
    INCLUDE_STUDENTS_CBX = (By.ID, 'search-include-students-checkbox')
    INCLUDE_CLASSES_CBX = (By.ID, 'search-include-courses-checkbox')
    INCLUDE_NOTES_CBX = (By.ID, 'search-include-notes-checkbox')

    def include_parameter(self, checkbox):
        if not self.element(checkbox).is_selected():
            self.click_element_js(checkbox)

    def exclude_parameter(self, checkbox):
        if self.element(checkbox).is_selected():
            self.click_element_js(checkbox)

    def include_students(self):
        self.include_parameter(self.INCLUDE_STUDENTS_CBX)

    def exclude_students(self):
        self.exclude_parameter(self.INCLUDE_STUDENTS_CBX)

    def include_admits(self):
        self.include_parameter(self.INCLUDE_ADMITS_CBX)

    def exclude_admits(self):
        self.exclude_parameter(self.INCLUDE_ADMITS_CBX)

    def include_classes(self):
        self.include_parameter(self.INCLUDE_CLASSES_CBX)

    def exclude_classes(self):
        self.exclude_parameter(self.INCLUDE_CLASSES_CBX)

    def include_notes(self):
        self.include_parameter(self.INCLUDE_NOTES_CBX)

    def exclude_notes(self):
        self.exclude_parameter(self.INCLUDE_NOTES_CBX)

    # Topic

    NOTE_TOPICS_SELECT = (By.ID, 'search-option-note-filters-topic')

    def select_note_topic(self, topic=None):
        topic_name = topic.name if topic else 'Any topic'
        app.logger.info(f'Selecting note topic "{topic_name}"')
        self.wait_for_select_and_click_option(self.NOTE_TOPICS_SELECT, topic_name)

    # Author radio

    NOTES_BY_ANYONE_RADIO = (By.ID, 'search-options-note-filters-posted-by-anyone')
    NOTES_BY_ANYONE_DIV = (By.XPATH, '//input[@id="search-options-note-filters-posted-by-anyone"]/..')
    NOTES_BY_YOU_RADIO = (By.ID, 'search-options-note-filters-posted-by-you')
    NOTES_BY_YOU_DIV = (By.XPATH, '//input[@id="search-options-note-filters-posted-by-you"]/..')

    def select_notes_posted_by_anyone(self):
        if not self.element(self.NOTES_BY_ANYONE_DIV).get_attribute('ischecked') == 'true':
            self.wait_for_element_and_click(self.NOTES_BY_ANYONE_DIV)

    def select_notes_posted_by_you(self):
        if not self.element(self.NOTES_BY_YOU_DIV).get_attribute('ischecked') == 'true':
            self.wait_for_element_and_click(self.NOTES_BY_YOU_DIV)

    # Author / Student

    NOTE_AUTHOR = (By.ID, 'search-options-note-filters-author-input')
    NOTE_STUDENT = (By.ID, 'search-options-note-filters-student-input')
    AUTHOR_SUGGEST = (By.XPATH, '//a[contains(@id, "search-options-note-filters-author-suggestion")]')

    def set_auto_suggest(self, locator, name, alt_names=None):
        names = [name.lower()]
        if alt_names:
            alt_names_lower = list(map(lambda n: n.lower(), alt_names))
            names.extend(alt_names_lower)
        self.wait_for_textbox_and_type(locator, name)
        time.sleep(2)
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.AUTHOR_SUGGEST))
        for el in self.elements(self.AUTHOR_SUGGEST):
            text = el.get_attribute('innerText').lower()
            if text in names:
                el.click()

    def set_notes_author(self, name, alt_names=None):
        app.logger.info(f'Entering notes author name {name}')
        self.set_auto_suggest(self.NOTE_AUTHOR, name, alt_names)

    def set_notes_student(self, student):
        string = f'{student.full_name} ({student.sid})'
        app.logger.info(string)
        self.set_auto_suggest(self.NOTE_STUDENT, string)

    # Dates

    NOTE_DATE_FROM = (By.ID, 'search-options-note-filters-last-updated-from')
    NOTE_DATE_TO = (By.ID, 'search-options-note-filters-last-updated-to')

    def set_notes_date_from(self, date=None):
        from_date = date.strftime('%m/%d/%Y') if date else ''
        app.logger.info(f'Entering note date from {from_date}')
        self.remove_and_enter_chars(self.NOTE_DATE_FROM, from_date)
        for i in range(4):
            self.hit_tab()

    def set_notes_date_to(self, date=None):
        to_date = date.strftime('%m/%d/%Y') if date else ''
        app.logger.info(f'Entering note date to {to_date}')
        self.remove_and_enter_chars(self.NOTE_DATE_TO, to_date)
        for i in range(4):
            self.hit_tab()

    def set_notes_date_range(self, date_from, date_to):
        self.set_notes_date_to(date_to)
        self.set_notes_date_from(date_from)

    # Reset, Search, Cancel

    RESET_ADV_SEARCH_BUTTON = (By.ID, 'reset-advanced-search-form-btn')
    ADV_SEARCH_BUTTON = (By.ID, 'advanced-search')
    ADV_SEARCH_CXL_BUTTON = (By.ID, 'advanced-search-cancel')

    def reset_adv_search(self):
        app.logger.info('Resetting advanced search form')
        if self.is_present(self.RESET_ADV_SEARCH_BUTTON):
            self.wait_for_element_and_click(self.RESET_ADV_SEARCH_BUTTON)

    def click_adv_search_button(self):
        app.logger.info('Submitting advanced search')
        self.wait_for_element_and_click(self.ADV_SEARCH_BUTTON)

    def click_adv_search_cxl_button(self):
        app.logger.info('Canceling advanced search')
        self.wait_for_element_and_click(self.ADV_SEARCH_CXL_BUTTON)

    def close_adv_search_if_open(self):
        if self.is_present(self.ADV_SEARCH_CXL_BUTTON):
            self.wait_for_element_and_click(self.ADV_SEARCH_CXL_BUTTON)

    def reopen_and_reset_adv_search(self):
        self.close_adv_search_if_open()
        self.open_adv_search()
        self.reset_adv_search()
