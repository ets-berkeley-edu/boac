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
    CCN = By.ID, 'course-class-number'
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

    def course_code(self):
        return self.el_text_if_exists(self.COURSE_CODE)

    def section_format(self):
        return self.element(self.COURSE_DETAILS).text.split()[1] if self.is_present(self.COURSE_DETAILS) else None

    def section_number(self):
        return self.element(self.COURSE_DETAILS).text.split()[2] if self.is_present(self.COURSE_DETAILS) else None

    def course_units_completed(self):
        return self.element(self.COURSE_DETAILS).text.split('—')[-1].split(' ')[0] if self.is_present(self.COURSE_DETAILS) else None

    def course_title(self):
        return self.el_text_if_exists(self.COURSE_TITLE)

    def course_term(self):
        return self.el_text_if_exists(self.TERM_NAME)

    def section_ccn(self):
        return self.element(self.CCN).text.split(' ')[-1]

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
        return f'//tr[contains(.,"{student.sid}")]'

    def is_student_inactive(self, student, section):
        loc = By.ID, f'student-{student.uid}-inactive-for-{section.term.sis_id}-{section.ccn}'
        return self.el_text_if_exists(loc) == 'INACTIVE'

    def student_level(self, student):
        loc = By.ID, f'student-{student.uid}-level'
        return self.el_text_if_exists(loc)

    def student_majors(self, student):
        loc = By.ID, f'student-{student.uid}-majors'
        majors = self.el_text_if_exists(loc)
        majors = list(filter(lambda maj: maj, majors.split('\n')))
        return majors

    def student_sports(self, student):
        loc = By.ID, f'student-{student.uid}-teams'
        return self.els_text_if_exist(loc)

    def student_graduation(self, student):
        loc = By.XPATH, f'{self.student_xpath(student)}//div[starts-with(text()," Graduated")]'
        return self.els_text_if_exist(loc, text_to_remove='Graduated')

    def student_mid_point_grade(self, student):
        loc = By.ID, f'td-student-{student.uid}-column-midtermGrade'
        return self.el_text_if_exists(loc, text_to_remove='No data')

    def student_final_grade(self, student):
        loc = By.ID, f'td-student-{student.uid}-column-finalGrade'
        return self.el_text_if_exists(loc)

    # STUDENT SITE DATA

    def site_code(self, student, node):
        loc = By.XPATH, f'{self.student_xpath(student)}/td[3]//div[contains(@class, "canvas-site-count")][{node}]/span'
        return self.el_text_if_exists(loc)

    def assignment_data(self, score_xpath):
        boxplot_xpath = f'{score_xpath}{self.boxplot_trigger_xpath()}'
        app.logger.info(f'Checking assignment submission data at {boxplot_xpath}')
        has_boxplot = self.is_present((By.XPATH, boxplot_xpath))
        app.logger.info(f'Has-boxplot is {has_boxplot}')
        if has_boxplot:
            loc = By.XPATH, '//div[@class="highcharts-tooltip-container"][last()]//div[contains(text(), "User Score")]/following-sibling::div'
            self.mouseover(self.element((By.XPATH, boxplot_xpath)))
            if not self.is_present(loc):
                self.mouseover(self.element((By.XPATH, boxplot_xpath)), horizontal_offset=-15)
            if not self.is_present(loc):
                self.mouseover(self.element((By.XPATH, boxplot_xpath)), horizontal_offset=15)
        else:
            loc = By.XPATH, f'{score_xpath}//strong'
        return self.element(loc).text.split(' ')[-1] if self.is_present(loc) else None

    def assignment_no_data(self, xpath):
        loc = By.XPATH, f'{xpath}/div[contains(., "No Data")]'
        return self.element(loc).text if self.is_present(loc) else None

    @staticmethod
    def assigns_submit_xpath(student, node):
        return f'//td[@id="td-student-{student.uid}-column-assignmentsSubmitted"]/div/div[{node}]'

    def assigns_submit_score(self, student, node):
        return self.assignment_data(self.assigns_submit_xpath(student, node))

    def assigns_submit_no_data(self, student, node):
        return self.assignment_no_data(self.assigns_submit_xpath(student, node))

    @staticmethod
    def assigns_grade_xpath(student, node):
        return f'//td[@id="td-student-{student.uid}-column-assignmentGrades"]/div/div[{node}]'

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
