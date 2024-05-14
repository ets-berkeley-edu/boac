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
from bea.pages.curated_modal import CuratedModal
from bea.pages.list_view_student_pages import ListViewStudentPages
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class ClassPage(ListViewStudentPages,
                CuratedAddSelector,
                CuratedModal):
    # COURSE DATA

    COURSE_CODE = By.ID, 'course-header'
    COURSE_DETAILS = By.XPATH, '//h2[text()="Details"]/..'
    COURSE_TITLE = By.CLASS_NAME, 'course-section-title'
    TERM_NAME = By.CLASS_NAME, 'course-term-name'
    CCN = By.ID, 'courses-class-number'
    MEETING_DIV = By.ID, 'meetings-0'

    def hit_class_page_url(self, term_id, ccn, student=None):
        app.logger.info(f'Loading class page for term {term_id} section {ccn}')
        param = f'?u={student.uid}' if student else ''
        self.driver.get(f'{boa_utils.get_boa_base_url()}/course/{term_id}/{ccn}{param}')

    def load_page(self, term_id, ccn, student=None):
        self.hit_class_page_url(term_id, ccn, student)
        self.wait_for_spinner()
        self.when_visible(self.MEETING_DIV, utils.get_medium_timeout())
        self.hide_boa_footer()

    def visible_course_data(self):
        return {
            'code': (self.element(self.COURSE_CODE).text if self.is_present(self.COURSE_CODE) else None),
            'format': (
                self.element(self.COURSE_DETAILS).text.split(' ')[1] if self.is_present(self.COURSE_DETAILS) else None),
            'number': (
                self.element(self.COURSE_DETAILS).text.split(' ')[2] if self.is_present(self.COURSE_DETAILS) else None),
            'units_completed': (
                self.element(self.COURSE_DETAILS).text.split(' ')[4] if self.is_present(self.COURSE_DETAILS) else None),
            'title': (self.element(self.COURSE_TITLE).text.strip() if self.is_present(self.COURSE_TITLE) else None),
            'term': (self.element(self.TERM_NAME).text if self.is_present(self.TERM_NAME) else None),
            'ccn': (self.element(self.CCN).text.split(' ')[-2]),
        }

    # COURSE MEETING DATA

    def meeting_instructors(self, index):
        loc = By.XPATH, '//span[contains(@id, "instructors-")]/..'
        if self.is_present(loc) and self.element(loc).text:
            names = self.element(loc).text.replace('Instructor:', '').replace('Instructors:', '').strip()
            return names.split(', ')
        else:
            return []

    @staticmethod
    def meeting_schedule_xpath(index):
        return f'//div[@id="meetings-{index}"]'

    def meeting_days(self, index):
        loc = By.XPATH, f'{self.meeting_schedule_xpath(index)}//div[1]'
        return self.element(loc).text if self.is_present(loc) and self.element(loc).text else None

    def meeting_time(self, index):
        loc = By.XPATH, f'{self.meeting_schedule_xpath(index)}//div[2]'
        return self.element(loc).text if self.is_present(loc) and self.element(loc).text else None

    def meeting_location(self, index):
        loc = By.XPATH, f'{self.meeting_schedule_xpath(index)}//div[3]'
        return self.element(loc).text if self.is_present(loc) and self.element(loc).text else None

    def visible_meeting_data(self, index):
        return {
            'instructors': self.meeting_instructors(index),
            'days': self.meeting_days(index),
            'time': self.meeting_time(index),
            'location': self.meeting_location(index),
        }

    # STUDENT SIS DATA

    STUDENT_LINK = By.XPATH, '//tr//a[contains(@href, "/student/")]'
    STUDENT_SID = By.XPATH, '//div[@class="student-sid"]'

    def class_list_view_sids(self):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.presence_of_all_elements_located(self.STUDENT_LINK))
        time.sleep(utils.get_click_sleep())
        sids = []
        for el in self.elements(self.STUDENT_SID):
            sids.append(el.text.replace('INACTIVE', '').replace('WAITLISTED', '').strip())

    @staticmethod
    def student_xpath(student):
        return f'//tr[contains(.,"{student.sis_id}")]'

    def student_level(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[contains(@id, "-level")]/span[@class="student-text"]'
        return self.element(loc).text if self.is_present(loc) else None

    def inactive_label(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[contains(@class,"student-sid")]/span[contains(@id,"-inactive")]'
        return self.element(loc).text.strip() if self.is_present(loc) else None

    def student_majors(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[contains(@id, "-majors"]/div[@class="student-text"]'
        return list(map(lambda el: el.text, self.elements(loc)))

    def student_sports(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[contains(@id, "-teams")]/div[@class="student-text"]'
        return list(map(lambda el: el.text, self.elements(loc)))

    def student_mid_point_grade(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}/td[@data-label="Mid"]//span'
        return self.element(loc).text if self.is_present(loc) else None

    def student_grading_basis(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}/td[@data-label="Final"]//span[@class="cohort-grading-basis"]'
        return self.element(loc).text if self.is_present(loc) else None

    def student_graduation_colleges(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[contains(@id, "-graduated-colleges")]/div[@class="student-text"]'
        return list(map(lambda el: el.text.strip(), self.elements(loc)))

    def student_graduation(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[starts-with(text()," Graduated")]'
        return self.element(loc).text.replace('Graduated', '').strip() if self.is_present(loc) else None

    def student_final_grade(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}/td[@data-label="Final"]//span'
        return self.element(loc).text if self.is_present(loc) else None

    def visible_student_sis_data(self, student):
        return {
            'level': self.student_level(student),
            'majors': self.student_majors(student),
            'graduation': self.student_graduation(student),
            'sports': self.student_sports(student),
            'mid_point_grade': self.student_mid_point_grade(student),
            'grading_basis': self.student_grading_basis(student),
            'final_grade': self.student_final_grade(student),
            'inactive': (self.inactive_label(student) == 'INACTIVE'),
        }

    # STUDENT SITE DATA

    def site_code(self, student, node):
        loc = By.XPATH, f'{self.student_xpath(student)}/td[@data-label="Course Site(s)"]/div/div/div[{node}]/strong'
        return self.element(loc).text if self.is_present(loc) else None

    def assignment_data(self, score_xpath):
        boxplot_xpath = f'{score_xpath}{self.boxplot_trigger_xpath()}'
        app.logger.info(f'Checking assignment submission score at {self.boxplot_xpath()}')
        has_boxplot = self.is_present((By.XPATH, boxplot_xpath))
        app.logger.info(f'Has-boxplot is {has_boxplot}')
        if has_boxplot:
            loc = By.XPATH, '//div[@class="highcharts-tooltip-container"][last()]//div[contains(text(), "User Score")]/following-sibling::div'
            self.mouseover(self.element(self.boxplot_xpath()))
            if not self.is_present(loc):
                self.mouseover(self.element(self.boxplot_xpath()), horizontal_offset=-15)
            if not self.is_present(loc):
                self.mouseover(self.element(self.boxplot_xpath()), horizontal_offset=15)
        else:
            loc = By.XPATH, f'{score_xpath}//strong'
        return self.element(loc).text.split(' ')[-1] if self.is_present(loc) else None

    def assignment_no_data(self, xpath):
        loc = By.XPATH, f'{xpath}/div[contains(., "No Data")]'
        return self.element(loc).text if self.is_present(loc) else None

    def assigns_submit_xpath(self, student, node):
        return f'{self.student_xpath(student)}/td[@data-label="Assignments Submitted"]/div/div/div[{node}]'

    def assigns_submit_score(self, student, node):
        return self.assignment_data(self.assigns_submit_xpath(student, node))

    def assigns_submit_no_data(self, student, node):
        return self.assignment_no_data(self.assigns_submit_xpath(student, node))

    def assigns_grade_xpath(self, student, node):
        return f'{self.student_xpath(student)}/td[@data-label="Assignment Grades"]/div/div/div[{node}]'

    def assigns_grade_score(self, student, node):
        return self.assignment_data(self.assigns_grade_xpath(student, node))

    def assigns_grade_no_data(self, student, node):
        return self.assignment_no_data(self.assigns_grade_xpath(student, node))

    def visible_assigns_data(self, student, index):
        node = index + 1
        return {
            'site_code': self.site_code(student, node),
            'assigns_submitted': self.assigns_submit_score(student, node),
            'assigns_submit_no_data': self.assigns_submit_no_data(student, node),
            'assigns_grade': self.assigns_grade_score(student, node),
            'assigns_grade_no_data': self.assigns_grade_no_data(student, node),
        }

    def last_activity(self, student, node):
        loc = By.XPATH, f'{self.student_xpath(student)}/td[@data-label="bCourses Activity"]//div/div/div[{node}]'
        return self.element(loc).text.split(' ')[0] if self.is_present(loc) else None

    def visible_last_activity(self, student, index):
        node = index + 1
        return {
            'site_code': self.site_code(student, node),
            'days': self.last_activity(student, node),
        }
