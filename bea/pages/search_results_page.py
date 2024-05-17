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

from bea.pages.curated_add_selector import CuratedAddSelector
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class SearchResultsPage(CuratedAddSelector):

    RESULTS_LOADED_MSG = By.XPATH, '//h1[text()="Search Results"]'
    NO_RESULTS_MSG = By.XPATH, '//div[text()="No matching records found."]'

    def wait_for_no_results(self):
        self.when_visible(self.NO_RESULTS_MSG, utils.get_short_timeout())

    # ADMIT SEARCH

    ADMIT_RESULTS_BUTTON = By.ID, 'search_results-tab-admits'
    ADMIT_RESULTS_COUNT = By.ID, 'search-results-count-admits'

    def admit_search_results_count(self):
        self.wait_for_spinner()
        return int(self.element(self.ADMIT_RESULTS_COUNT).text)

    @staticmethod
    def admit_link_loc(admit):
        return By.ID, f'link-to-admit-{admit.sid}'

    def is_admit_in_search_result(self, admit):
        self.wait_for_element_and_click(self.ADMIT_RESULTS_BUTTON)
        time.sleep(1)
        return self.is_present(self.admit_link_loc(admit))

    def click_admit_result(self, admit):
        self.wait_for_element_and_click(self.ADMIT_RESULTS_BUTTON)
        self.wait_for_element_and_click(self.admit_link_loc(admit))
        self.wait_for_spinner()

    # STUDENT SEARCH

    STUDENT_RESULTS_BUTTON = By.ID, 'search-results-tab-students'
    STUDENT_RESULTS_COUNT = By.ID, 'search-results-count-students'

    def student_search_results_count(self):
        self.wait_for_spinner()
        return int(self.element(self.STUDENT_RESULTS_COUNT).text)

    @staticmethod
    def student_link_loc(student):
        return By.ID, f'link-to-student-{student.uid}'

    def is_student_in_search_result(self, student):
        self.wait_for_element_and_click(self.STUDENT_RESULTS_BUTTON)
        time.sleep(1)
        return self.is_present(self.student_link_loc(student))

    def click_student_result(self, student):
        self.wait_for_element_and_click(self.STUDENT_RESULTS_BUTTON)
        self.wait_for_element_and_click(self.student_link_loc(student))
        self.wait_for_spinner()

    # CLASS SEARCH

    CLASS_RESULTS_BUTTON = By.ID, 'search-results-tab-courses'
    CLASS_RESULTS_COUNT = By.ID, 'search-results-count-courses'
    CLASS_ROW = By.XPATH, '//*[contains(@id, "course-results-page-h")]/../following-sibling::table/tr'
    PARTIAL_RESULTS_MSG = By.XPATH, '//div[text()=" Showing the first 50 classes. "]'

    @staticmethod
    def class_link(course_code, section_number):
        return By.XPATH, f'//a[contains(.,"{course_code}")][contains(.,"{section_number}")]'

    def is_class_in_search_result(self, course_code, section_number):
        self.wait_for_element_and_click(self.CLASS_RESULTS_BUTTON)
        time.sleep(1)
        return self.is_present(self.class_link(course_code, section_number))

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
        return int(self.element(self.NOTE_RESULTS_COUNT).text)

    def wait_for_note_search_result_rows(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.NOTE_SEARCH_RESULT))

    @staticmethod
    def note_link(note):
        return By.XPATH, f'//a[contains(@href, "note-{note.record_id}")]'

    def is_note_in_search_result(self, note):
        self.wait_for_element_and_click(self.NOTE_RESULTS_BUTTON)
        time.sleep(1)
        return self.is_present(self.note_link(note))

    def note_result(self, student, note):
        Wait(self.driver, utils.get_short_timeout()).until(ec.visibility_of_element_located(self.note_link(note)))
        student_name = self.element(self.note_link(note)).text.strip() if self.is_present(self.note_link(note)) else None
        sid_loc = By.XPATH, f'//div[@id="advising-note-search-result-{note.record_id}"]/h3'
        sid = self.element(sid_loc).text.replace(student.full_name, '').strip()[1:-1] if self.is_present(sid_loc) else None
        snippet_loc = By.ID, f'advising-note-search-result-snippet-{note.record_id}'
        snippet = self.element(snippet_loc).text if self.is_present(snippet_loc) else None
        advisor_loc = By.ID, f'advising-note-search-result-advisor-{note.record_id}'
        advisor_name = self.element(advisor_loc).text.replace('-', '').strip() if self.is_present(advisor_loc) else None
        date_loc = By.XPATH, f'//div[@id="advising-note-search-result-{note.record_id}"]/div[@class="advising-note-search-result-footer"]'
        date = self.element(date_loc).text.split('-')[-1].strip() if self.is_present(date_loc) else None
        return {
            'student_name': student_name,
            'student_sid': sid,
            'snippet': snippet,
            'advisor_name': advisor_name,
            'date': date,
        }

    def note_result_uids(self):
        els = self.elements(self.NOTE_SEARCH_RESULT)
        return list(map(lambda el: el.get_attribute('href').split('/')[-1].split('#')[0], els))

    def click_note_link(self, note):
        self.wait_for_element_and_click(self.note_link(note))

    # APPOINTMENTS

    APPT_RESULTS_BUTTON = By.ID, 'search-results-tab-appointments'
    APPT_RESULTS_COUNT = By.ID, 'search-results-count-appointments'
    APPT_SEARCH_RESULT = By.XPATH, '//div[contains(@id, "appointment-search-result-")]//a'

    def appt_results_count(self):
        self.wait_for_spinner()
        return int(self.element(self.APPT_RESULTS_COUNT).text)

    def wait_for_appt_search_result_rows(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.APPT_SEARCH_RESULT))

    @staticmethod
    def appt_link(appt):
        return By.XPATH, f'//a[contains(@href, "#appointment-{appt.record_id}")]'

    def is_appt_in_search_result(self, appt):
        count = self.appt_results_count()
        if count == 0:
            return False
        else:
            try:
                self.wait_for_appt_search_result_rows()
                Wait(self.driver, 2).until(ec.presence_of_element_located(self.appt_link(appt)))
                return True
            except TimeoutError:
                return False

    def appt_result(self, student, appt):
        Wait(self.driver, utils.get_short_timeout()).until(ec.visibility_of_element_located(self.appt_link(appt)))
        student_name = self.element(self.appt_link(appt)).text.strip() if self.is_present(self.appt_link(appt)) else None
        sid_loc = By.XPATH, f'//div[@id="appointment-search-result-{appt.record_id}"]/h3'
        sid = self.element(sid_loc).text.replace(student.full_name, '').strip()[1:-1] if self.is_present(sid_loc) else None
        snippet_loc = By.ID, f'appointment-search-result-snippet-{appt.record_id}'
        snippet = self.element(snippet_loc).text if self.is_present(snippet_loc) else None
        advisor_loc = By.ID, f'appointment-search-result-advisor-{appt.record_id}'
        advisor_name = self.element(advisor_loc).text.strip() if self.is_present(advisor_loc) else None
        date_loc = By.XPATH, f'//div[@id="appointment-search-result-{appt.record_id}"]/div[@class="appointment-search-result-footer"]'
        date = self.element(date_loc).text.split('-')[-1].strip() if self.is_present(date_loc) else None
        return {
            'student_name': student_name,
            'student_sid': sid,
            'snippet': snippet,
            'advisor_name': advisor_name,
            'date': date,
        }

    def appt_result_uids(self):
        els = self.elements(self.APPT_SEARCH_RESULT)
        return list(map(lambda el: el.get_attribute('href').split('/')[-1].split('#')[0], els))

    def click_appt_link(self, appt):
        self.wait_for_element_and_click(self.appt_link(appt))

    # GROUPS

    @staticmethod
    def student_checkbox_loc(student):
        return By.XPATH, f'//input[@id="student-{student.sid}-curated-group-checkbox"]/..'

    def select_students_to_add(self, students):
        app.logger.info(f'Selecting SIDs to add to group: {list(map(lambda s: s.sis, students))}')
        for s in students:
            self.wait_for_element_and_click(self.student_checkbox_loc(s))

    def select_and_add_students_to_grp(self, students, group):
        self.select_students_to_add(students)
        self.add_members_to_grp(students, group)

    def select_and_add_students_to_new_grp(self, students, group):
        self.select_students_to_add(students)
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
        self.add_members_to_grp(students, group)
