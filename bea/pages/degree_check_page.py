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

from bea.models.degree_progress.degree_reqt_category import DegreeReqtCategory
from bea.models.degree_progress.degree_reqt_course import DegreeReqtCourse
from bea.pages.degree_template_page import DegreeTemplatePage
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import boa_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class DegreeCheckPage(DegreeTemplatePage):

    @staticmethod
    def degree_check_heading(degree):
        return By.XPATH, f'//h2[text()="{degree.name}"]'

    def load_page(self, degree):
        app.logger.info(f'Loading degree check {degree.check_id}')
        self.driver.get(f'{boa_utils.get_boa_base_url()}/student/degree/{degree.check_id}')
        self.wait_for_spinner()

    TEMPLATE_UPDATED_MSG = By.XPATH, '//div[contains(., "Please update below if necessary")]'
    TEMPLATE_LINK = By.ID, 'original-degree-template'
    LAST_UPDATED_MSG = By.XPATH, '//div[contains(text(), "Last updated by")]'
    CREATE_NEW_DEGREE_LINK = By.ID, 'create-new-degree'
    VIEW_DEGREE_HISTORY_LINK = By.ID, 'view-degree-history'

    def click_create_new_degree(self):
        app.logger.info('Clicking create-new-degree link')
        self.wait_for_element_and_click(self.CREATE_NEW_DEGREE_LINK)

    def click_view_degree_history(self):
        app.logger.info('Clicking view-degree-history link')
        self.wait_for_element_and_click(self.VIEW_DEGREE_HISTORY_LINK)
        self.wait_for_spinner()

    # NOTES

    CREATE_NOTE_BUTTON = By.ID, 'create-degree-note-btn'
    EDIT_NOTE_BUTTON = By.ID, 'edit-degree-note-btn'
    PRINT_NOTE_TOGGLE = By.ID, 'degree-note-print-toggle'
    NOTE_UPDATE_ADVISOR = By.ID, 'degree-note-updated-by'
    NOTE_UPDATE_DATE = By.ID, 'degree-note-updated-at'
    NOTE_INPUT = By.ID, 'degree-note-input'
    SAVE_NOTE_BUTTON = By.ID, 'save-degree-note-btn'
    CANCEL_NOTE_BUTTON = By.ID, 'cancel-degree-note-btn'
    NOTE_BODY = By.ID, 'degree-note-body'

    def click_print_note_toggle(self):
        self.wait_for_element_and_click(self.PRINT_NOTE_TOGGLE)
        time.sleep(utils.get_click_sleep())

    def is_print_note_selected(self):
        return self.element(self.PRINT_NOTE_TOGGLE).is_selected()

    def click_create_degree_note(self):
        self.wait_for_element_and_click(self.CREATE_NOTE_BUTTON)

    def click_edit_degree_note(self):
        self.wait_for_element_and_click(self.EDIT_NOTE_BUTTON)

    def enter_note_body(self, string):
        self.wait_for_textbox_and_type(self.NOTE_INPUT, string)

    def click_save_note(self):
        self.wait_for_element_and_click(self.SAVE_NOTE_BUTTON)

    def click_cancel_note(self):
        self.wait_for_element_and_click(self.CANCEL_NOTE_BUTTON)
        time.sleep(1)

    def create_note(self, string):
        app.logger.info(f'Entering degree note {string}')
        self.click_create_degree_note()
        self.enter_note_body(string)
        self.click_save_note()

    def edit_note(self, string):
        app.logger.info(f'Entering degree note {string}')
        self.click_edit_degree_note()
        self.enter_note_body(string)
        self.click_save_note()

    def visible_note_body(self):
        self.when_present(self.NOTE_BODY, utils.get_short_timeout())
        return self.element(self.NOTE_BODY).text

    def visible_note_update_advisor(self):
        self.when_present(self.NOTE_UPDATE_ADVISOR, utils.get_short_timeout())
        return self.element(self.NOTE_UPDATE_ADVISOR).text

    # UNIT REQUIREMENTS

    def visible_unit_reqt_completed(self, reqt):
        loc = By.XPATH, f'{self.unit_reqt_row_xpath(reqt)}/td[3]'
        self.when_visible(loc, utils.get_short_timeout())
        return self.element(loc).text

    def is_unit_reqt_updated(self, reqt, expected):
        tries = 3
        while tries > 0:
            try:
                tries -= 1
                app.logger.info(f'Checking for {expected}, got {self.visible_unit_reqt_completed(reqt)}')
                assert self.visible_unit_reqt_completed(reqt) == str(expected)
                reqt.units_completed = expected
                return True
            except AssertionError:
                if tries == 0:
                    return False

    def are_units_added_to_unit_reqt(self, reqt, course):
        expected = utils.formatted_units(float(reqt.units_completed) + float(course.units))
        return self.is_unit_reqt_updated(reqt, expected)

    def are_units_removed_from_unit_reqt(self, reqt, course):
        expected = utils.formatted_units(float(reqt.units_completed) - float(course.units))
        return self.is_unit_reqt_updated(reqt, expected)

    def is_unit_reqt_course_present(self, reqt, course):
        return self.is_present((By.ID, f'unit-requirement-{reqt.reqt_id}-course-{course.course_id}'))

    def unit_reqt_course_units(self, reqt, course):
        self.scroll_to_top()
        if self.is_present((By.XPATH, f'{self.unit_reqt_row_xpath(reqt)}//button[contains(., "Show fulfillments of")]')):
            self.wait_for_element_and_click((By.ID, f'unit-requirement-{reqt.reqt_id}-toggle'))
            time.sleep(1)
        return self.el_text_if_exists(
            (By.XPATH, f'//tr[@id="unit-requirement-{reqt.reqt_id}-course-{course.course_id}"]/td[3]'))

    # COURSE REQUIREMENTS

    BIG_DOT_CBX = By.ID, 'recommended-course-checkbox'
    SAVE_EDIT_REQT_BUTTON = By.ID, 'update-requirement-btn'
    CANCEL_EDIT_REQT_BUTTON = By.ID, 'cancel-edit-requirement-btn'

    def is_course_row_assign_cell_present(self, row_xpath):
        return self.is_present((By.XPATH, f'{row_xpath}/td[contains(@class, "td-assign")]'))

    def course_reqt_name(self, course):
        return By.XPATH, f'{self.course_reqt_xpath(course)}/td[2]/span[last()]/span'

    def visible_course_reqt_name(self, course):
        return self.el_text_if_exists(self.course_reqt_name(course))

    def is_visible_course_reqt_name_struck(self, course):
        return 'strikethrough' in self.element(self.course_reqt_name(course)).get_attribute('class')

    def visible_course_reqt_grade(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.course_reqt_xpath(course)}/td[3]//span'))

    def visible_course_reqt_units(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.course_reqt_xpath(course)}/td[4]//div'))

    def visible_course_reqt_note(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.course_reqt_xpath(course)}/td[5]//a'))

    def click_edit_course_reqt(self, course):
        self.click_edit_cat(course)

    def toggle_course_reqt_dot(self):
        self.click_element_js(self.BIG_DOT_CBX)

    def click_save_reqt_edit(self):
        self.wait_for_element_and_click(self.SAVE_EDIT_REQT_BUTTON)
        time.sleep(1)

    @staticmethod
    def is_recommended_loc(course):
        return By.XPATH, f'//*[@id="category-{course.course_id}-is-recommended"]'

    # COMPLETED COURSES

    HIDE_NOTE_BUTTON = By.XPATH, '//tr[contains(., "Hide note")]//button'

    def click_hide_note(self):
        self.wait_for_element_and_click(self.HIDE_NOTE_BUTTON)
        time.sleep(1)

    # IN PROGRESS COURSES

    IN_PROGRESS_COURSE = By.XPATH, '//tr[contains(@id, "tr-in-progress")]'

    def in_progress_course_ccns(self):
        ccns = []
        for el in self.elements(self.IN_PROGRESS_COURSE):
            parts = el.get_attribute('id').split('-')
            ccns.append(f'{parts[4]}-{parts[6]}')
        return ccns

    @staticmethod
    def in_progress_course_xpath(course):
        return f'//tr[@id="tr-in-progress-term-{course.term_id}-section-{course.ccn}"]'

    def in_progress_course_row(self, course):
        return By.XPATH, self.in_progress_course_xpath(course)

    def in_progress_course_code(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.in_progress_course_xpath(course)}/td[1]'))

    def in_progress_course_units(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.in_progress_course_xpath(course)}/td[2]'))

    # UNASSIGNED COURSES

    UNASSIGNED_COURSE = By.XPATH, '//tr[contains(@id, "unassigned-course-")]'
    UNASSIGNED_DROP_ZONE = By.ID, 'drop-zone-unassigned-courses'

    def unassigned_course_ccns(self):
        ids = list(map(lambda el: el.get_attribute('id'), self.elements(self.UNASSIGNED_COURSE)))
        ids = [i for i in ids if '-manually-created' not in i]
        return ['-'.join(i.split('-')[2:4]) for i in ids]

    @staticmethod
    def unassigned_course_xpath(course):
        string = f'{course.course_id}-manually-created' if course.is_manual else f'{course.term_id}-{course.ccn}'
        return f'//tr[@id="unassigned-course-{string}"]'

    def unassigned_course_row(self, course):
        return By.XPATH, self.unassigned_course_xpath(course)

    def unassigned_course_code(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.unassigned_course_xpath(course)}/td[2]/span'))

    def unassigned_course_units(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.unassigned_course_xpath(course)}/td[4]/span'))

    def is_unassigned_course_units_flagged(self, course):
        flag = By.XPATH, f'{self.unassigned_course_xpath(course)}/td[4]//*[name()="svg"]'
        hover = By.XPATH, f'{self.unassigned_course_xpath(course)}/td[4]//span[contains(text(), "updated from")]'
        return self.is_present(flag) and self.is_present(hover)

    def unassigned_course_grade(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.unassigned_course_xpath(course)}/td[3]/span'))

    def unassigned_course_term(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.unassigned_course_xpath(course)}/td[5]'))

    def unassigned_course_note(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.unassigned_course_xpath(course)}/td[6]'))

    def expand_unassigned_course_note(self, course):
        self.wait_for_element_and_click((By.XPATH, f'{self.unassigned_course_xpath(course)}/td[6]/a'))
        self.when_visible(self.HIDE_NOTE_BUTTON, 1)

    # JUNK DRAWER

    JUNK_DROP_ZONE = By.ID, 'drop-zone-ignored-courses'

    @staticmethod
    def junk_course_xpath(course):
        string = f'{course.course_id}-manually-created' if course.is_manual else f'{course.term_id}-{course.ccn}'
        return f'//tr[@id="ignored-course-{string}"]'

    def junk_course_row(self, course):
        return By.XPATH, self.junk_course_xpath(course)

    def junk_course_code(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.junk_course_xpath(course)}/td[2]'))

    def junk_course_units(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.junk_course_xpath(course)}/td[4]/span'))

    def is_junk_course_units_flagged(self, course):
        flag = By.XPATH, f'{self.junk_course_xpath(course)}/td[4]//*[name()="svg"]'
        hover = By.XPATH, f'{self.junk_course_xpath(course)}/td[4]//span[contains(text(), "updated from")]'
        return self.is_present(flag) and self.is_present(hover)

    def junk_course_grade(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.junk_course_xpath(course)}/td[3]/span'))

    def junk_course_note(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.junk_course_xpath(course)}/td[5]'))

    def expand_junk_course_note(self, course):
        self.wait_for_element_and_click((By.XPATH, f'{self.junk_course_xpath(course)}/td[5]/a'))
        self.when_visible(self.HIDE_NOTE_BUTTON, 1)

    # ASSIGNED COURSES

    @staticmethod
    def category_courses(category):
        table = f'column-{category.column_num}-courses-of-category-{category.category_id}'
        return By.XPATH, f'//table[@id="{table}"]/tbody/tr[not(contains(., "No completed requirements"))]'

    @staticmethod
    def assigned_course_xpath(course):
        table = f'column-{course.course_reqt.parent.column_num}-courses-of-category-{course.course_reqt.parent.category_id}'
        return f'//table[@id="{table}"]//tr[contains(.,"{course.name}")]'

    def assigned_course_row(self, course):
        return By.XPATH, self.assigned_course_xpath(course)

    def assigned_course_name(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.assigned_course_xpath(course)}/td[2]'))

    def is_assigned_course_copy_flagged(self, course):
        flag = By.XPATH, f'{self.assigned_course_xpath(course)}/td[2]//*[name()="svg"]'
        hover = By.XPATH, f'{self.assigned_course_xpath(course)}/td[2]//i[@title="Course satisfies multiple requirements."]'
        return self.is_present(flag) and self.is_present(hover)

    def assigned_course_units(self, course):
        loc = By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-units")]//div'
        return self.el_text_if_exists(loc)

    def is_assigned_course_units_flagged(self, course):
        flag = By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-units")]//*[name()="svg"]'
        hover = By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-units")]//span[contains(text(), "updated from")]'
        return self.is_present(flag) and self.is_present(hover)

    def is_assigned_course_fulfill_flagged(self, course):
        flag = By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-units")]//i'
        return self.is_present(flag)

    def assigned_course_grade(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-grade")]//span'))

    def assigned_course_note(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-note")]'))

    def expand_assigned_course_note(self, course):
        loc = By.XPATH, f'{self.assigned_course_xpath(course)}/td[contains(@class, "td-note")]//a'
        self.wait_for_element_and_click(loc)
        self.when_visible(self.HIDE_NOTE_BUTTON, 1)

    def verify_assigned_course_fulfillment(self, course):
        self.click_edit_assigned_course(course)
        self.when_present(self.COL_REQT_COURSE_UNITS_REQT_SELECT, 1)
        if course.unit_reqts:
            utils.assert_equivalence(len(self.elements(self.COL_REQT_COURSE_UNITS_REQT_PILL)), len(course.unit_reqts))
            for req in course.unit_reqts:
                self.when_present(self.col_reqt_unit_reqt_pill(req), 1)
        else:
            assert not self.elements(self.COL_REQT_COURSE_UNITS_REQT_PILL)

    # COURSE ASSIGNMENT

    ASSIGN_COURSE_BUTTON = By.XPATH, '//button[contains(@id, "assign-course-")]'
    UNASSIGNED_OPTION = By.ID, 'assign-course-to-option-null'
    JUNK_OPTION = By.ID, 'course-to-option-ignore'
    ASSIGNMENT_OPTION = By.XPATH, '//button[contains(@id, "assign-course-to-option")]'

    def click_assignment_select(self, select_button_loc):
        self.wait_for_element_and_click(select_button_loc)
        self.when_present(self.ASSIGNMENT_OPTION, utils.get_short_timeout())

    def click_unassigned_course_select(self, course):
        loc = By.XPATH, f'{self.unassigned_course_xpath(course)}/td[1]//button'
        self.click_assignment_select(loc)

    def click_junk_course_select(self, course):
        loc = By.XPATH, f'{self.junk_course_xpath(course)}//button[contains(@id, "assign-course-")]'
        self.click_assignment_select(loc)

    def assigned_course_select(self, course):
        return By.XPATH, f'{self.assigned_course_xpath(course)}//button[contains(@id, "assign-course-")]'

    def click_assigned_course_select(self, course):
        self.click_assignment_select(self.assigned_course_select(course))

    def assignment_reqt_options(self):
        return self.els_text_if_exist(self.ASSIGNMENT_OPTION)

    @staticmethod
    def assignment_reqt_option(reqt):
        reqt_id = reqt.course_id if isinstance(reqt, DegreeReqtCourse) else reqt.category_id
        return By.ID, f'assign-course-to-option-{reqt_id}'

    def click_unassigned_option(self):
        self.wait_for_element_and_click(self.UNASSIGNED_OPTION)

    def click_junk_option(self):
        self.wait_for_element_and_click(self.JUNK_OPTION)

    @staticmethod
    def set_assigned_course_attributes(course, reqt):
        # If course is assigned to a cat, create a dummy course reqt within the cat
        if isinstance(reqt, DegreeReqtCourse):
            course_reqt = reqt
        else:
            course_reqt = DegreeReqtCourse({
                'is_dummy': True,
                'parent': reqt,
                'unit_reqts': reqt.unit_reqts,
            })
            reqt.course_reqts.append(course_reqt)
        course_reqt.completed_course = course
        course.course_reqt = course_reqt
        course.unit_reqts = course_reqt.unit_reqts

    def assign_completed_course(self, course, reqt):
        app.logger.info(f'Assigning {course.name}, {course.term_id}-{course.ccn} to {reqt.name}')
        # TODO - drag and drop
        if course.is_junk:
            self.click_junk_course_select(course)
        else:
            self.click_unassigned_course_select(course)
        self.wait_for_element_and_click(self.assignment_reqt_option(reqt))
        time.sleep(1)
        course.is_junk = False
        self.set_assigned_course_attributes(course, reqt)
        utils.assert_actual_includes_expected(self.assigned_course_name(course), course.name)

    # COURSE UN-ASSIGNMENT

    def unassign_course(self, course, reqt=None):
        app.logger.info(f'Un-assigning {course.name}, {course.term_id}-{course.ccn}')
        # TODO - drag-and-drop
        if course.is_junk:
            self.click_junk_course_select(course)
        else:
            self.click_assigned_course_select(course)
        self.click_unassigned_option()
        time.sleep(2)
        course.is_junk = False

        # If course was assigned to course reqt, verify the reqt row reverts to template version
        if reqt:
            if isinstance(reqt, DegreeReqtCourse):
                reqt.completed_course = None
                utils.assert_actual_includes_expected(self.visible_course_reqt_name(reqt), reqt.name)
            else:
                self.when_not_present(self.assigned_course_row(course), utils.get_short_timeout())
        course.course_reqt = None
        course.unit_reqts = []

    # COURSE REASSIGNMENT

    def reassign_course(self, course, old_reqt, new_reqt):
        app.logger.info(f'Reassigning {course.name} {course.term_id}-{course.ccn} from {old_reqt.name} to {new_reqt.name}')
        self.click_assigned_course_select(course)
        self.wait_for_element_and_click(self.assignment_reqt_option(new_reqt))
        time.sleep(1)

        # Detach the course from the old course reqt, dummy or otherwise
        old_course_reqt = old_reqt if isinstance(old_reqt, DegreeReqtCourse) else course.course_reqt
        if isinstance(old_reqt, DegreeReqtCategory) and old_course_reqt in old_reqt.course_reqts:
            old_reqt.course_reqts.remove(old_course_reqt)
        old_course_reqt.completed_course = None

        # Attach the course to the new course reqt, dummy or otherwise
        if isinstance(new_reqt, DegreeReqtCourse):
            new_course_reqt = new_reqt
        else:
            new_course_reqt = DegreeReqtCourse({
                'is_dummy': True,
                'parent': new_reqt,
                'unit_reqts': new_reqt.unit_reqts,
            })
            new_reqt.course_reqts.append(new_course_reqt)
        new_course_reqt.completed_course = course
        course.course_reqt = new_course_reqt
        course.unit_reqts = new_course_reqt.unit_reqts

        if isinstance(old_reqt, DegreeReqtCourse):
            utils.assert_equivalence(self.visible_course_reqt_name(old_reqt), old_reqt.name)
        utils.assert_equivalence(self.assigned_course_name(course), course.name)

    # COURSE JUNKIFICATION

    def wish_to_cornfield(self, course, old_reqt=None):
        app.logger.info(f'Wishing {course.name}, {course.term_id}-{course.ccn} to the cornfield')
        el = self.assigned_course_row(course) if old_reqt else self.unassigned_course_row(course)
        if old_reqt:
            self.click_assigned_course_select(course)
        else:
            self.click_unassigned_course_select(course)
        self.click_junk_option()
        time.sleep(1)
        utils.assert_equivalence(self.junk_course_code(course), course.name)
        course.is_junk = True
        if old_reqt:
            if isinstance(old_reqt, DegreeReqtCourse):
                utils.assert_equivalence(self.visible_course_reqt_name(old_reqt), old_reqt.name)
                old_reqt.completed_course = None
            else:
                self.when_not_present(el, 2)
                old_reqt.course_reqts.remove(course.course_reqt)
        course.course_reqt = None
        course.unit_reqts = []

    # COURSE CREATE / EDIT / DELETE

    CREATE_COURSE_BUTTON = By.ID, 'create-course-button'
    COURSE_NAME_INPUT = By.ID, 'course-name-input'
    COURSE_UNITS_INPUT = By.ID, 'course-units-input'
    COURSE_GRADE_INPUT = By.ID, 'course-grade-input'
    COURSE_COLOR_BUTTON = By.XPATH, '//button[contains(@id, "color-code-select")]'
    COURSE_COLOR_SELECT = By.ID, 'color-code-select'
    COURSE_NOTE_INPUT = By.ID, 'course-note-textarea'

    CREATE_COURSE_SAVE_BUTTON = By.ID, 'create-course-save-btn'
    CREATE_COURSE_CANCEL_BUTTON = By.ID, 'create-course-cancel-btn'
    COURSE_UPDATE_BUTTON = By.ID, 'update-note-btn'
    COURSE_CANCEL_BUTTON = By.ID, 'cancel-update-note-btn'

    # Any

    @staticmethod
    def create_course_button(reqt):
        return By.ID, f'create-course-under-parent-category-{reqt.category_id}'

    def enter_course_name(self, name):
        app.logger.info(f'Entering course name {name}')
        self.wait_for_textbox_and_type(self.COURSE_NAME_INPUT, name)

    def enter_course_units(self, units):
        units = '' if units == '0' else units
        app.logger.info(f'Entering units value {units}')
        self.wait_for_textbox_and_type(self.COURSE_UNITS_INPUT, units)

    def enter_course_grade(self, grade):
        app.logger.info(f'Entering grade {grade}')
        self.wait_for_textbox_and_type(self.COURSE_GRADE_INPUT, grade)

    def select_course_unit_reqt(self, course):
        button_count = len(self.elements(self.COL_REQT_COURSE_UNITS_REQT_REMOVE_BUTTON))
        for i in range(button_count):
            self.elements(self.COL_REQT_COURSE_UNITS_REQT_REMOVE_BUTTON)[0].click()
            time.sleep(1)
        for u_reqt in course.unit_reqts:
            self.select_col_reqt_unit_reqt(u_reqt)

    def select_color_option(self, color='none'):
        app.logger.info(f'Setting color to {color}')
        if f'border-color-{color}' not in self.element(self.COURSE_COLOR_BUTTON).get_attribute('class'):
            self.wait_for_element_and_click(self.COURSE_COLOR_BUTTON)
            el_id = f'color-code-option-{color}' if color else 'color-code-option-none'
            self.wait_for_element_and_click((By.ID, el_id))

    def enter_course_note(self, note):
        app.logger.info(f'Entering note value {note}')
        self.wait_for_textbox_and_type(self.COURSE_NOTE_INPUT, note)

    def click_create_course(self, reqt):
        self.wait_for_element_and_click(self.create_course_button(reqt))

    def click_cancel_course_create(self):
        self.wait_for_element_and_click(self.CREATE_COURSE_CANCEL_BUTTON)
        time.sleep(utils.get_click_sleep())
        if self.is_present(self.CONFIRM_DELETE_OR_DISCARD):
            self.element(self.CONFIRM_DELETE_OR_DISCARD).click()
        self.when_not_present(self.CREATE_COURSE_CANCEL_BUTTON, 2)

    def click_cancel_course_edit(self):
        if self.is_present(self.COURSE_CANCEL_BUTTON):
            self.wait_for_element_and_click(self.COURSE_CANCEL_BUTTON)
            self.when_not_present(self.COURSE_UNITS_INPUT, 1)

    def click_save_course_edit(self):
        self.wait_for_element_and_click(self.COURSE_UPDATE_BUTTON)
        self.when_not_present(self.COURSE_UPDATE_BUTTON, utils.get_short_timeout())

    def create_manual_course(self, degree_check, course, reqt):
        self.click_create_course(reqt)
        self.enter_course_name(course.name)
        self.enter_course_units(course.units)
        self.enter_course_grade(course.grade)
        self.select_color_option(course.color)
        self.enter_course_note(course.note)
        self.wait_for_element_and_click(self.CREATE_COURSE_SAVE_BUTTON)
        self.when_not_present(self.CREATE_COURSE_SAVE_BUTTON, utils.get_short_timeout())
        self.set_assigned_course_attributes(course, reqt)
        course.degree_check = degree_check
        boa_degree_progress_utils.set_degree_manual_course_id(degree_check, course)

    def enter_and_save_course_attribute_edits(self, course):
        self.enter_course_units(course.units)
        self.enter_course_note(course.note)
        if course.is_manual:
            self.enter_course_name(course.name)
            self.enter_course_grade(course.grade)
            self.select_color_option(course.color)
        self.click_save_course_edit()

    # Edit unassigned

    def click_edit_unassigned_course(self, course):
        loc = By.XPATH, f'{self.unassigned_course_xpath(course)}/td[7]//button[contains(@id, "edit")]'
        self.wait_for_element_and_click(loc)

    def edit_unassigned_course(self, course):
        app.logger.info(f'Editing unassigned course {course.name}')
        self.click_edit_unassigned_course(course)
        self.enter_and_save_course_attribute_edits(course)

    # Edit junk

    def click_edit_junk_course(self, course):
        loc = By.XPATH, f'{self.junk_course_xpath(course)}/td[6]//button[contains(@id, "edit")]'
        self.wait_for_element_and_click(loc)

    def edit_junk_course(self, course):
        app.logger.info(f'Editing junk course {course.name}')
        self.click_edit_junk_course(course)
        self.enter_and_save_course_attribute_edits(course)

    # Edit assigned

    def click_edit_assigned_course(self, course):
        app.logger.info(f'Clicking the edit button for course {course.name}')
        loc = By.XPATH, f'{self.assigned_course_xpath(course)}/td[last()]//button[contains(@id, "edit")]'
        self.wait_for_element_and_click(loc)

    def edit_assigned_course(self, course):
        app.logger.info(f'Editing assigned course {course.name}')
        self.click_edit_assigned_course(course)
        self.select_course_unit_reqt(course)
        self.enter_and_save_course_attribute_edits(course)
        time.sleep(utils.get_click_sleep())

    # Delete unassigned

    def click_delete_unassigned_course(self, course):
        loc = By.XPATH, f'{self.unassigned_course_xpath(course)}/td[7]//button[contains(@id, "delete")]'
        self.wait_for_element_and_click(loc)

    def delete_unassigned_course(self, course):
        app.logger.info(f'Deleting unassigned course {course.name}')
        self.click_delete_unassigned_course(course)
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)
        time.sleep(1)

    # Delete junk

    def click_delete_junk_course(self, course):
        loc = By.XPATH, f'{self.junk_course_xpath(course)}/td[6]//button[contains(@id, "delete")]'
        self.wait_for_element_and_click(loc)

    def delete_junk_course(self, course):
        app.logger.info(f'Deleting junk course {course.name}')
        self.click_delete_junk_course(course)
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)
        time.sleep(1)

    # Delete assigned

    def assigned_course_delete_button(self, course):
        return By.XPATH, f'{self.assigned_course_xpath(course)}/td[6]//button[contains(@id, "delete")]'

    def click_delete_assigned_course(self, course):
        self.wait_for_element_and_click(self.assigned_course_delete_button(course))

    def delete_assigned_course(self, course):
        app.logger.info(f'Deleting assigned course {course.name}')
        self.click_delete_assigned_course(course)
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)
        time.sleep(1)

    # COURSE COPY

    COPY_COURSE_BUTTON = By.ID, 'duplicate-existing-course'
    COPY_COURSE_SELECT = By.ID, 'add-course-select'
    COPY_COURSE_SAVE_BUTTON = By.ID, 'add-course-save-btn'
    COPY_COURSE_CANCEL_BUTTON = By.ID, 'add-course-cancel-btn'

    def click_copy_course_button(self):
        self.wait_for_element_and_click(self.COPY_COURSE_BUTTON)

    def copy_course_options(self):
        time.sleep(utils.get_click_sleep())
        select_el = Select(self.element(self.COPY_COURSE_SELECT))
        opts = [el.text for el in select_el.options]
        opts.remove('Choose...')
        return opts

    def click_cancel_course_copy(self):
        app.logger.info('Clicking course copy cancel button')
        self.wait_for_element_and_click(self.COPY_COURSE_CANCEL_BUTTON)

    def copy_course(self, course, copy, dest_reqt):
        app.logger.info(f'Copying {course.name} to destination {dest_reqt.name}')
        self.click_copy_course_button()
        self.wait_for_select_and_click_option(self.COPY_COURSE_SELECT, course.name)
        self.wait_for_element_and_click(self.COPY_COURSE_SAVE_BUTTON)
        time.sleep(utils.get_click_sleep())
        dummy_reqt = DegreeReqtCourse({
            'is_dummy': True,
            'parent': dest_reqt,
        })
        dest_reqt.course_reqts.append(dummy_reqt)
        copy.course_reqt = dummy_reqt
        copy.unit_reqts = dest_reqt.unit_reqts
        if course.is_manual:
            boa_degree_progress_utils.set_degree_manual_course_id(course.degree_check, copy)
        else:
            boa_degree_progress_utils.set_degree_sis_course_copy_id(course.degree_check, copy)
        course.course_copies.append(copy)
        self.assign_completed_course(copy, dest_reqt)
        time.sleep(1)
        utils.assert_actual_includes_expected(self.assigned_course_name(copy), copy.name)
        dummy_reqt.completed_course = copy

    # COURSE REQT EDITS

    IGNORE_REQT_CBX = By.ID, 'ignored-course-checkbox'
    GRADE_INPUT = By.ID, 'grade-input'
    RECOMMENDED_NOTE_INPUT = By.ID, 'recommendation-note-textarea'

    def click_ignore_reqt(self):
        self.wait_for_element_and_click(self.IGNORE_REQT_CBX)

    def enter_reqt_grade(self, grade):
        self.wait_for_textbox_and_type(self.GRADE_INPUT, grade)

    def edit_course_reqt(self, reqt):
        self.enter_col_reqt_units(reqt.units)

    def enter_recommended_note(self, note):
        self.wait_for_textbox_and_type(self.RECOMMENDED_NOTE_INPUT, note)

    # CAMPUS REQUIREMENTS

    def campus_reqt_cbx(self, reqt_name):
        return By.XPATH, f'{self.campus_reqt_row_xpath(reqt_name)}//input[contains(@id, "satisfy-checkbox")]'

    def click_campus_reqt_cbx(self, reqt_name):
        app.logger.info(f'Clicking satisfied checkbox for {reqt_name}')
        self.wait_for_element_and_click(self.campus_reqt_cbx(reqt_name))
        time.sleep(utils.get_click_sleep())

    def is_campus_reqt_satisfied(self, reqt_name):
        return self.element(self.campus_reqt_cbx(reqt_name)).is_selected()

    def is_campus_reqt_selectable(self, reqt_name):
        return self.element(self.campus_reqt_cbx(reqt_name)).is_enabled()

    def enter_campus_reqt_note(self, reqt_name, note):
        app.logger.info(f'Entering Campus Requirements note {note}')
        loc = By.XPATH, f'{self.campus_reqt_row_xpath(reqt_name)}//button'
        self.wait_for_element_and_click(loc)
        self.enter_recommended_note(note)
        self.click_save_reqt_edit()
