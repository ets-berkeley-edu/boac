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

from bea.pages.list_view_admit_pages import ListViewAdmitPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class SearchResultsPage(ListViewAdmitPages):

    RESULTS_LOADED_MSG = By.XPATH, '//h1[text()="Search Results"]'
    NO_RESULTS_MSG = By.XPATH, '//div[contains(text(), "No results found for")]'
    EDIT_SEARCH_BUTTON = By.ID, 'edit-search-btn'

    def wait_for_no_results(self):
        self.when_present(self.NO_RESULTS_MSG, utils.get_short_timeout())

    def click_edit_search(self):
        self.wait_for_element_and_click(self.EDIT_SEARCH_BUTTON)

    @staticmethod
    def expected_note_or_appt_date_format(date_time):
        return date_time.strftime('%b %-d, %Y')

    # ADMIT SEARCH

    ADMIT_RESULTS_BUTTON = By.ID, 'search-results-tab-admits'
    ADMIT_RESULTS_COUNT = By.ID, 'search-results-count-admits'

    def admit_search_results_count(self):
        self.wait_for_spinner()
        return self.element(self.ADMIT_RESULTS_COUNT).text

    @staticmethod
    def admit_link_loc(admit):
        return By.ID, f'link-to-admit-{admit.sid}'

    def is_admit_in_search_result(self, admit):
        self.wait_for_page_and_click(self.ADMIT_RESULTS_BUTTON)
        time.sleep(1)
        count = self.admit_search_results_count()
        if count == '50+':
            app.logger.info(f'Skipping test with UID {admit.sid} because there are too many results')
        else:
            self.when_present(self.admit_link_loc(admit), utils.get_short_timeout())
        return True

    def click_admit_result(self, admit):
        self.wait_for_element_and_click(self.ADMIT_RESULTS_BUTTON)
        self.wait_for_element_and_click(self.admit_link_loc(admit))
        self.wait_for_spinner()

    # STUDENT SEARCH

    STUDENT_RESULTS_BUTTON = By.ID, 'search-results-tab-students'
    STUDENT_RESULTS_COUNT = By.ID, 'search-results-count-students'

    def student_search_results_count(self):
        self.wait_for_spinner()
        return self.element(self.STUDENT_RESULTS_COUNT).text

    @staticmethod
    def student_link_loc(student):
        return By.ID, f'link-to-student-{student.uid}'

    def is_student_in_search_result(self, student):
        self.wait_for_spinner()
        self.wait_for_element_and_click(self.STUDENT_RESULTS_BUTTON)
        time.sleep(1)
        count = self.student_search_results_count()
        if count == '50+':
            app.logger.info(f'Skipping test with UID {student.uid} because there are too many results')
        else:
            self.when_present(self.student_link_loc(student), utils.get_short_timeout())
        return True

    def click_student_result(self, student):
        self.wait_for_element_and_click(self.STUDENT_RESULTS_BUTTON)
        self.wait_for_element_and_click(self.student_link_loc(student))
        self.wait_for_spinner()

    # CLASS SEARCH

    CLASS_RESULTS_BUTTON = By.ID, 'search-results-tab-courses'
    CLASS_RESULTS_COUNT = By.ID, 'search-results-count-courses'
    CLASS_ROW = By.XPATH, '//*[contains(@id, "course-results-page-h")]/../following-sibling::table/tr'
    PARTIAL_RESULTS_MSG = By.XPATH, '//div[text()=" Showing the first 50 classes. "]'

    def class_search_results_count(self):
        self.wait_for_spinner()
        return self.element(self.CLASS_RESULTS_COUNT).text

    @staticmethod
    def class_link(course_code, section_number):
        return By.XPATH, f'//a[contains(.,"{course_code}")][contains(.,"{section_number}")]'

    def is_class_in_search_result(self, course_code, section_number):
        count = self.class_search_results_count()
        if count == '50+':
            app.logger.info(f'Skipping test with class {course_code} because there are too many results')
        else:
            self.wait_for_element_and_click(self.CLASS_RESULTS_BUTTON)
            time.sleep(1)
            self.when_present(self.class_link(course_code, section_number), utils.get_short_timeout())
        return True

    def click_class_result(self, course_code, section_number):
        self.wait_for_element_and_click(self.CLASS_RESULTS_BUTTON)
        self.wait_for_element_and_click(self.class_link(course_code, section_number))
        self.wait_for_spinner()

    # NOTES

    NOTE_RESULTS_BUTTON = By.ID, 'search-results-tab-notes'
    NOTE_RESULTS_COUNT = By.ID, 'search-results-count-notes'
    NOTE_SEARCH_RESULT = By.XPATH, '//div[@class="advising-note-search-result"]//a'

    def note_results_count(self):
        self.wait_for_spinner()
        return self.element(self.NOTE_RESULTS_COUNT).text

    def wait_for_note_search_result_rows(self):
        self.wait_for_spinner()
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.NOTE_SEARCH_RESULT))

    @staticmethod
    def note_link(note):
        return By.XPATH, f'//a[contains(@href, "note-{note.record_id}")]'

    def wait_for_note_search_result_count(self):
        self.wait_for_spinner()
        if self.is_present(self.NO_RESULTS_MSG):
            count = '0'
        else:
            count = self.note_results_count()
        app.logger.info(f'Note search results count is {count}')
        return count

    def is_note_in_search_result(self, note):
        return True if self.is_present(self.note_link(note)) else False

    def assert_note_result_present(self, note):
        count = self.wait_for_note_search_result_count()
        if count == '20+':
            app.logger.info(f'Skipping test with note {note.record_id} because there are too many results')
        else:
            if count != '0':
                self.wait_for_element_and_click(self.NOTE_RESULTS_BUTTON)
            assert self.is_note_in_search_result(note)

    def assert_note_result_not_present(self, note):
        count = self.wait_for_note_search_result_count()
        if count == '20+':
            app.logger.info(f'Skipping test with note {note.record_id} because there are too many results')
        else:
            if count != '0':
                self.wait_for_element_and_click(self.NOTE_RESULTS_BUTTON)
            assert not self.is_note_in_search_result(note)

    def note_result_student_name(self, note):
        self.when_present(self.note_link(note), utils.get_short_timeout())
        time.sleep(utils.get_click_sleep())
        return self.el_text_if_exists(self.note_link(note))

    def note_result_sid(self, student, note):
        sid_loc = By.XPATH, f'//div[@id="advising-note-search-result-{note.record_id}"]/h3'
        if self.is_present(sid_loc):
            return self.element(sid_loc).text.replace(student.full_name, '').strip()[1:-1]
        else:
            return None

    def note_result_snippet(self, note):
        return self.el_text_if_exists((By.ID, f'advising-note-search-result-snippet-{note.record_id}'))

    def note_result_advisor_name(self, note):
        advisor_loc = By.ID, f'advising-note-search-result-advisor-{note.record_id}'
        return self.el_text_if_exists(advisor_loc, '-')

    def note_result_date(self, note):
        xpath = f'//div[@id="advising-note-search-result-{note.record_id}"]/div[@class="advising-note-search-result-footer"]'
        date_loc = By.XPATH, xpath
        if self.is_present(date_loc):
            return self.element(date_loc).text.split('-')[-1].strip()
        else:
            return None

    def click_note_link(self, note):
        self.wait_for_element_and_click(self.note_link(note))

    # APPOINTMENTS

    APPT_RESULTS_BUTTON = By.ID, 'search-results-tab-appointments'
    APPT_RESULTS_COUNT = By.ID, 'search-results-count-appointments'
    APPT_SEARCH_RESULT = By.XPATH, '//div[contains(@id, "appointment-search-result-")]//a'

    def appt_results_count(self):
        self.wait_for_spinner()
        return self.element(self.APPT_RESULTS_COUNT).text

    def wait_for_appt_search_result_rows(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.APPT_SEARCH_RESULT))

    @staticmethod
    def appt_link(appt):
        return By.XPATH, f'//a[contains(@href, "appointment-{appt.record_id}")]'

    def wait_for_appt_search_result_count(self):
        self.wait_for_spinner()
        if self.is_present(self.NO_RESULTS_MSG):
            count = '0'
        else:
            count = self.appt_results_count()
        app.logger.info(f'Appointment search results count is {count}')
        return count

    def is_appt_in_search_result(self, appt):
        return True if self.is_present(self.appt_link(appt)) else False

    def assert_appt_result_present(self, appt):
        count = self.wait_for_appt_search_result_count()
        if count == '20+':
            app.logger.info(f'Skipping test with appointment {appt.record_id} because there are too many results')
        else:
            if count != '0':
                self.wait_for_element_and_click(self.APPT_RESULTS_BUTTON)
            assert self.is_appt_in_search_result(appt)

    def assert_appt_result_not_present(self, appt):
        count = self.wait_for_appt_search_result_count()
        if count == '20+':
            app.logger.info(f'Skipping test with appointment {appt.record_id} because there are too many results')
        else:
            if count != '0':
                self.wait_for_element_and_click(self.APPT_RESULTS_BUTTON)
            assert not self.is_appt_in_search_result(appt)

    def appt_result_student_name(self, appt):
        self.when_present(self.appt_link(appt), utils.get_short_timeout())
        time.sleep(utils.get_click_sleep())
        return self.el_text_if_exists(self.appt_link(appt))

    def appt_result_sid(self, student, appt):
        sid_loc = By.XPATH, f'//div[@id="appointment-search-result-{appt.record_id}"]/h3'
        if self.is_present(sid_loc):
            return self.element(sid_loc).text.replace(student.full_name, '').strip()[1:-1]
        else:
            return None

    def appt_result_snippet(self, appt):
        return self.el_text_if_exists((By.ID, f'appointment-search-result-snippet-{appt.record_id}'))

    def appt_result_advisor_name(self, appt):
        advisor_loc = By.ID, f'appointment-search-result-advisor-{appt.record_id}'
        return self.el_text_if_exists(advisor_loc, '-')

    def appt_result_date(self, appt):
        xpath = f'//div[@id="appointment-search-result-{appt.record_id}"]/div[contains(@class, "result-footer")]'
        date_loc = By.XPATH, xpath
        if self.is_present(date_loc):
            return self.element(date_loc).text.split('-')[-1].strip()
        else:
            return None

    def click_appt_link(self, appt):
        self.wait_for_element_and_click(self.appt_link(appt))

    # GROUPS

    @staticmethod
    def student_checkbox_loc(student):
        return By.XPATH, f'//input[@id="student-{student.sid}-curated-group-checkbox"]/..'

    def select_students_to_add(self, students):
        app.logger.info(f'Selecting SIDs to add to group: {list(map(lambda st: st.sid, students))}')
        for s in students:
            self.wait_for_element_and_click(self.student_checkbox_loc(s))

    def select_and_add_students_to_grp(self, students, group):
        self.select_students_to_add(students)
        self.click_add_to_group_from_list_view_header_button(group)
        self.add_members_to_grp(students, group)

    def select_and_add_students_to_new_grp(self, students, group):
        self.select_students_to_add(students)
        self.click_add_to_group_from_list_view_header_button(group)
        self.add_members_to_new_grp(students, group)

    def select_and_add_all_students_to_grp(self, all_students, group):
        Wait(self.driver, utils.get_short_timeout()).until(
            ec.presence_of_all_elements_located(self.ADD_INDIVIDUAL_TO_GROUP_CBX),
        )
        self.wait_for_element_and_click(self.ADD_ALL_TO_GROUP_CBX)
        els = self.elements(self.ADD_INDIVIDUAL_TO_GROUP_CBX)
        app.logger.info(f'There are {len(els)} individual checkboxes')
        visible_sids = list(map(lambda el: el.get_attribute('id').split('-')[1], els))
        students = list(filter(lambda s: s.sid in visible_sids, all_students))
        self.click_add_to_group_from_list_view_header_button(group)
        self.add_members_to_grp(students, group)
