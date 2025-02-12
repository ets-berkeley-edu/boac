"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

from bea.pages.boa_pages import BoaPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class DegreeCheckBatchPage(BoaPages):

    # Students

    STUDENT_INPUT = By.ID, 'degree-check-add-student-input'
    STUDENT_ADD_BUTTON = By.ID, 'degree-check-add-sids-btn'

    @staticmethod
    def added_student_loc(student):
        return By.XPATH, f'//div[contains(text(), "{student.sid}")]'

    @staticmethod
    def student_remove_button(student):
        return By.XPATH, f'//div[contains(text(), "{student.sid}")]/following-sibling::div/button'

    def add_sids_to_batch(self, degree_batch, students):
        sids = [s.sid for s in students]
        app.logger.info(f'Adding SIDS {sids} to batch degree')
        self.wait_for_textbox_and_type(self.STUDENT_INPUT, ', '.join(sids))
        self.wait_for_element_and_click(self.STUDENT_ADD_BUTTON)
        for stu in students:
            self.when_present(self.added_student_loc(stu), utils.get_short_timeout())
            degree_batch.students.append(stu)

    def remove_students_from_batch(self, degree_batch, students):
        for stu in students:
            app.logger.info(f'Removing SID {stu.sid} from batch degree')
            self.wait_for_element_and_click(self.student_remove_button(stu))
            self.when_not_present(self.student_remove_button(stu), 2)
            degree_batch.students.remove(stu)

    # Cohorts

    COHORT_SELECT = By.ID, 'batch-degree-check-cohort'

    @staticmethod
    def added_cohort_loc(cohort):
        return By.XPATH, f'//div[text()="{cohort.name}"]'

    @staticmethod
    def cohort_remove_button(cohort):
        return By.XPATH, f'//div[text()="{cohort.name}"]/following-sibling::div/button'

    def add_cohorts_to_batch(self, degree_batch, cohorts):
        for cohort in cohorts:
            app.logger.info(f'Adding cohort {cohort.name} to batch degree')
            self.wait_for_element(self.COHORT_SELECT, utils.get_short_timeout())
            sel = Select(self.element(self.COHORT_SELECT))
            opt = next(filter(lambda o: cohort.name in o.text, sel.options))
            sel.select_by_visible_text(opt.text)
            self.when_present(self.added_cohort_loc(cohort), utils.get_short_timeout())
            degree_batch.cohorts.append(cohort)

    def remove_cohorts_from_batch(self, degree_batch, cohorts):
        for cohort in cohorts:
            app.logger.info(f'Removing cohort {cohort.name} from batch degree check')
            self.wait_for_element_and_click(self.cohort_remove_button(cohort))
            self.when_not_present(self.cohort_remove_button(cohort), 2)
            degree_batch.cohorts.remove(cohort)

    # Groups

    GROUP_SELECT = By.ID, 'batch-degree-check-curated'

    @staticmethod
    def added_group_loc(group):
        return By.XPATH, f'//div[text()="{group.name}"]'

    @staticmethod
    def group_remove_button(group):
        return By.XPATH, f'//div[text()="{group.name}"]/following-sibling::div/button'

    def add_groups_to_batch(self, degree_batch, groups):
        for group in groups:
            app.logger.info(f'Adding group {group.name} to batch degree')
            self.wait_for_element(self.GROUP_SELECT, utils.get_short_timeout())
            sel = Select(self.element(self.GROUP_SELECT))
            opt = next(filter(lambda o: group.name in o.text, sel.options))
            sel.select_by_visible_text(opt.text)
            self.when_present(self.added_group_loc(group), utils.get_short_timeout())
            degree_batch.groups.append(group)

    def remove_groups_from_batch(self, degree_batch, groups):
        for group in groups:
            app.logger.info(f'Removing group {group.name} from batch degree check')
            self.wait_for_element_and_click(self.group_remove_button(group))
            self.when_not_present(self.group_remove_button(group), 2)
            degree_batch.groups.remove(group)

    # Degrees

    DEGREE_SELECT = By.ID, 'degree-template-select'

    def select_degree(self, degree):
        app.logger.info(f'Selecting {degree.name}')
        self.wait_for_select_and_click_option(self.DEGREE_SELECT, degree.name)

    # Save / Cancel

    DUPE_DEGREE_CHECK_MSG = By.XPATH, '//div[contains(text(), "The degree check will not be added to their student record")]'
    STUDENT_COUNT_MSG = By.ID, 'target-student-count-alert'
    BATCH_DEGREE_SAVE_BUTTON = By.ID, 'batch-degree-check-save'
    BATCH_DEGREE_CXL_BUTTON = By.ID, 'batch-degree-check-cancel'

    def click_save_batch_degree_check(self):
        app.logger.info('Clicking batch degree check save button')
        self.wait_for_element_and_click(self.BATCH_DEGREE_SAVE_BUTTON)

    def click_cancel_batch_degree_check(self):
        app.logger.info('Clicking batch degree check cancel button')
        self.wait_for_element_and_click(self.BATCH_DEGREE_CXL_BUTTON)
