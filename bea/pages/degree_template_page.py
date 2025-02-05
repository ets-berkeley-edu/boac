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
from bea.pages.boa_pages import BoaPages
from bea.test_utils import boa_degree_progress_utils
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class DegreeTemplatePage(BoaPages):

    @staticmethod
    def template_heading(template):
        return By.XPATH, f'//h1[text()="{template.name}"]'

    # UNIT reqtS

    # Create

    UNIT_REQT_ADD_BUTTON = By.ID, 'unit-requirement-create-link'
    UNIT_REQT_NAME_INPUT = By.ID, 'unit-requirement-name-input'
    UNIT_REQT_NUM_INPUT = By.ID, 'unit-requirement-min-units-input'
    UNIT_REQT_CREATE_BUTTON = By.ID, 'create-unit-requirement-btn'
    UNIT_REQT_CANCEL_BUTTON = By.ID, 'cancel-create-unit-requirement-btn'

    def is_unit_reqt_create_enabled(self):
        return self.element(self.UNIT_REQT_CREATE_BUTTON).is_enabled()

    def click_add_unit_reqt(self):
        app.logger.info('Clicking the add unit reqt button')
        self.wait_for_element_and_click(self.UNIT_REQT_ADD_BUTTON)

    def enter_unit_reqt_name(self, name):
        app.logger.info(f'Entering unit reqt {name}')
        self.wait_for_textbox_and_type(self.UNIT_REQT_NAME_INPUT, name)

    def unit_reqt_name_input_value(self):
        return self.el_value(self.UNIT_REQT_NAME_INPUT)

    def enter_unit_reqt_num(self, num):
        app.logger.info(f'Entering unit reqt count {num}')
        self.wait_for_textbox_and_type(self.UNIT_REQT_NUM_INPUT, num)

    def click_create_unit_reqt(self):
        app.logger.info('Clicking the create unit reqt button')
        self.wait_for_element_and_click(self.UNIT_REQT_CREATE_BUTTON)

    def click_cancel_unit_reqt(self):
        app.logger.info('Clicking the cancel unit reqt button')
        self.wait_for_element_and_click(self.UNIT_REQT_CANCEL_BUTTON)

    def create_unit_reqt(self, reqt, template):
        reqt.name = reqt.name[0:255]
        self.click_add_unit_reqt()
        self.enter_unit_reqt_name(reqt.name)
        self.enter_unit_reqt_num(reqt.unit_count)
        self.click_create_unit_reqt()
        self.when_not_present(self.UNIT_REQT_CREATE_BUTTON, utils.get_short_timeout())
        time.sleep(utils.get_click_sleep())
        boa_degree_progress_utils.set_unit_reqt_id(template, reqt)

    # List

    UNIT_REQTS_EMPTY_MSG = By.XPATH, '//div[text()=" No unit requirements created "]'

    @staticmethod
    def unit_reqt_row_xpath(reqt):
        return f'//table[@id="unit-requirements-table"]//tr[contains(., "{reqt.name}")]'

    def unit_reqt_name_loc(self, reqt):
        return By.XPATH, f'{self.unit_reqt_row_xpath(reqt)}/td[1]'

    def visible_unit_reqt_name(self, reqt):
        self.when_present(self.unit_reqt_name_loc(reqt), utils.get_short_timeout())
        return self.el_text_if_exists(self.unit_reqt_name_loc(reqt))

    def visible_unit_reqt_num(self, reqt):
        loc = By.XPATH, f'{self.unit_reqt_row_xpath(reqt)}/td[2]'
        self.when_present(loc, utils.get_short_timeout())
        return self.el_text_if_exists(loc)

    # Edit

    UNIT_REQT_SAVE_BUTTON = By.ID, 'update-unit-requirement-btn'

    def is_unit_reqt_save_enabled(self):
        return self.element(self.UNIT_REQT_SAVE_BUTTON).is_enabled()

    @staticmethod
    def unit_reqt_edit_button(reqt):
        return By.ID, f'unit-requirement-{reqt.reqt_id}-edit-btn'

    def click_edit_unit_reqt(self, reqt):
        app.logger.info(f'Clicking the edit button for unit reqt {reqt.name}')
        self.wait_for_element_and_click(self.unit_reqt_edit_button(reqt))

    def click_save_unit_reqt_edit(self):
        app.logger.info('Clicking the save unit reqt edit button')
        self.wait_for_element_and_click(self.UNIT_REQT_SAVE_BUTTON)

    def edit_unit_reqt(self, reqt):
        reqt.name = reqt.name[0:255]
        self.click_edit_unit_reqt(reqt)
        self.enter_unit_reqt_name(reqt.name)
        self.enter_unit_reqt_num(reqt.unit_count)
        self.click_save_unit_reqt_edit()

    # Delete

    @staticmethod
    def unit_reqt_delete_button(reqt):
        return By.ID, f'unit-requirement-{reqt.reqt_id}-delete-btn'

    def click_delete_unit_reqt(self, reqt):
        app.logger.info(f'Clicking the delete button for unit reqt {reqt.name}')
        self.wait_for_element_and_click(self.unit_reqt_delete_button(reqt))

    def click_confirm_delete(self):
        app.logger.info('Clicking the delete confirm button')
        self.wait_for_element_and_click(self.CONFIRM_DELETE_OR_DISCARD)
        time.sleep(2)

    def click_cancel_delete(self):
        app.logger.info('Clicking delete cancel button')
        self.wait_for_element_and_click(self.CANCEL_DELETE_OR_DISCARD)
        time.sleep(1)

    # COLUMN

    # Create

    COL_REQT_TYPE_SELECT = By.XPATH, '//select[contains(@id, "add-category-select")]'
    COL_REQT_NAME_INPUT = By.XPATH, '//input[contains(@id, "name-input")]'
    COL_REQT_DESC_INPUT = By.XPATH, '//textarea[contains(@id, "description-input")]'
    COL_REQT_PARENT_SELECT = By.XPATH, '//select[contains(@id, "parent-category-select")]'
    COL_REQT_TRANSFER_COURSE_CBX = By.ID, 'is-satisfied-by-transfer-course-checkbox'
    COL_REQT_COURSE_UNITS_INPUT = By.ID, 'units-input'
    COL_REQT_COURSE_UNITS_SHOW_RANGE = By.XPATH, '//span[text()="show range"]'
    COL_REQT_COURSE_UNITS_HIDE_RANGE = By.XPATH, '//span[text()="hide range"]'
    COL_REQT_UNIT_RANGE_TOGGLE = By.ID, 'show-upper-units-input'
    COL_REQT_UNIT_NUM_INPUT_0 = By.ID, 'units-input'
    COL_REQT_UNIT_NUM_INPUT_1 = By.ID, 'upper-units-input'
    COL_REQT_COURSE_UNITS_ERROR_MSG = By.XPATH, '//*[contains(text(), "Invalid")]'
    COL_REQT_COURSE_UNITS_NUM_ERROR_MSG = By.XPATH, '//div[text()="Units must be a number between 0 and 10"]'
    COL_REQT_COURSE_UNITS_REQT_PILL = By.XPATH, '//li[contains(@id, "unit-requirement")]'
    COL_REQT_COURSE_UNITS_REQT_SELECT = By.XPATH, '//select[contains(@id, "unit-requirement-select")]'
    COL_REQT_COURSE_UNITS_REQT_REMOVE_BUTTON = By.XPATH, '//button[contains(@id, "unit-requirement-remove")]'
    COL_REQT_CREATE_BUTTON = By.XPATH, '//button[contains(@id, "create-requirement-btn")]'
    COL_REQT_CANCEL_CREATE_BUTTON = By.XPATH, '//button[contains(@id, "cancel-create-requirement-btn")]'

    def is_col_reqt_create_enabled(self):
        return self.element(self.COL_REQT_CREATE_BUTTON).is_enabled()

    @staticmethod
    def add_col_reqt_button(col_num):
        return By.ID, f'column-{col_num}-create-btn'

    def click_add_col_reqt_button(self, col_num):
        app.logger.info(f'Clicking the add button for column {col_num}')
        self.wait_for_element_and_click(self.add_col_reqt_button(col_num))

    def col_reqt_type_options(self):
        self.when_present(self.COL_REQT_TYPE_SELECT, 1)
        el = Select(self.element(self.COL_REQT_TYPE_SELECT))
        return el.options

    def select_col_reqt_type(self, reqt_type):
        app.logger.info(f'Selecting column requirement type {reqt_type}')
        self.wait_for_select_and_click_option(self.COL_REQT_TYPE_SELECT, reqt_type)

    def enter_col_reqt_name(self, name):
        app.logger.info(f'Entering column requirement name {name}')
        self.wait_for_textbox_and_type(self.COL_REQT_NAME_INPUT, name)

    def col_reqt_name_input_value(self):
        return self.el_value(self.COL_REQT_NAME_INPUT)

    def enter_col_reqt_desc(self, desc):
        app.logger.info(f'Entering column requirement description {desc}')
        self.wait_for_textbox_and_type(self.COL_REQT_DESC_INPUT, desc)

    def col_reqt_desc_input_value(self):
        return self.el_value(self.COL_REQT_DESC_INPUT)

    def col_reqt_parent_options(self):
        self.when_present(self.COL_REQT_PARENT_SELECT, 1)
        el = Select(self.element(self.COL_REQT_PARENT_SELECT))
        return el.options

    def select_col_reqt_parent(self, parent=None):
        if parent:
            app.logger.info(f'Selecting column requirement parent {parent.name}')
            self.wait_for_select_and_click_option(self.COL_REQT_PARENT_SELECT, parent.name)
        else:
            opts = self.col_reqt_parent_options()
            self.wait_for_select_and_click_option(self.COL_REQT_PARENT_SELECT, opts[0].text)

    def click_transfer_course(self):
        self.wait_for_element_and_click(self.COL_REQT_TRANSFER_COURSE_CBX)

    @staticmethod
    def col_reqt_unit_reqt_pill_xpath(unit_reqt):
        return f'//li[contains(@id, "unit-requirement")][contains(., "{unit_reqt.name}")]'

    def col_reqt_unit_reqt_pill(self, unit_reqt):
        return By.XPATH, self.col_reqt_unit_reqt_pill_xpath(unit_reqt)

    def col_reqt_unit_reqt_remove_button(self, unit_reqt):
        return By.XPATH, f'{self.col_reqt_unit_reqt_pill_xpath(unit_reqt)}//button'

    def select_col_reqt_unit_reqt(self, unit_reqt):
        app.logger.info(f'Selecting column requirement unit fulfillment {unit_reqt.name}')
        self.wait_for_select_and_click_option(self.COL_REQT_COURSE_UNITS_REQT_SELECT, unit_reqt.name)

    def remove_col_reqt_unit_reqt(self, unit_reqt):
        app.logger.info(f'Removing unit fulfillment {unit_reqt.name}')
        self.wait_for_element_and_click(self.col_reqt_unit_reqt_remove_button(unit_reqt))
        self.when_not_present(self.col_reqt_unit_reqt_remove_button(unit_reqt), 2)

    def enter_col_reqt_units(self, units):
        app.logger.info(f'Entering column requirement units {units}')
        self.wait_for_element(self.COL_REQT_UNIT_RANGE_TOGGLE, utils.get_short_timeout())
        if '-' in units:
            unit_range = units.split('-')
            if self.is_present(self.COL_REQT_COURSE_UNITS_SHOW_RANGE):
                self.scroll_to_top()
                self.wait_for_element_and_click(self.COL_REQT_UNIT_RANGE_TOGGLE)
            self.wait_for_textbox_and_type(self.COL_REQT_UNIT_NUM_INPUT_0, unit_range[0])
            self.wait_for_textbox_and_type(self.COL_REQT_UNIT_NUM_INPUT_1, unit_range[1])
        else:
            if self.is_present(self.COL_REQT_COURSE_UNITS_HIDE_RANGE):
                self.scroll_to_top()
                self.wait_for_element_and_click(self.COL_REQT_UNIT_RANGE_TOGGLE)
                time.sleep(utils.get_click_sleep())
            if units == '' or units == '0':
                self.remove_chars(self.COL_REQT_UNIT_NUM_INPUT_0)
            else:
                self.wait_for_textbox_and_type(self.COL_REQT_UNIT_NUM_INPUT_0, units)

    def col_reqt_unit_input_0_value(self):
        return self.el_value(self.COL_REQT_UNIT_NUM_INPUT_0)

    def wait_for_units_invalid_error_msg(self):
        self.when_present(self.COL_REQT_COURSE_UNITS_ERROR_MSG, 1)

    def wait_for_units_numeric_error_msg(self):
        self.when_present(self.COL_REQT_COURSE_UNITS_NUM_ERROR_MSG, 1)

    def click_create_col_reqt(self):
        app.logger.info('Clicking the create column requirement button')
        self.wait_for_element_and_click(self.COL_REQT_CREATE_BUTTON)

    def click_cancel_col_reqt(self):
        app.logger.info('Clicking the cancel column requirement button')
        self.wait_for_element_and_click(self.COL_REQT_CANCEL_CREATE_BUTTON)
        self.when_not_present(self.COL_REQT_CANCEL_CREATE_BUTTON, 1)

    def enter_col_reqt_metadata(self, reqt):
        self.enter_col_reqt_name(reqt.name)
        if isinstance(reqt, DegreeReqtCategory):
            self.enter_col_reqt_desc(reqt.desc)
        if reqt.parent:
            self.select_col_reqt_parent(reqt.parent)
        if isinstance(reqt, DegreeReqtCourse):
            if reqt.is_transfer_course:
                self.click_transfer_course()
            if reqt.units:
                self.enter_col_reqt_units(reqt.units)
            else:
                self.enter_col_reqt_units('')
        for u_reqt in reqt.unit_reqts:
            self.select_col_reqt_unit_reqt(u_reqt)

    def save_col_reqt(self):
        self.click_create_col_reqt()
        self.when_not_present(self.COL_REQT_CREATE_BUTTON, utils.get_short_timeout())
        time.sleep(1)

    def create_col_reqt(self, reqt, template):
        if not reqt.column_num:
            reqt.column_num = reqt.parent.column_num or reqt.parent.parent.column_num
        for unit_reqt in reqt.unit_reqts:
            unit_reqt = next(filter(lambda u: unit_reqt.name in u.name, template.unit_reqts))
        self.click_add_col_reqt_button(reqt.column_num)
        if isinstance(reqt, DegreeReqtCategory):
            if reqt.parent:
                self.select_col_reqt_type('Subcategory')
            else:
                self.select_col_reqt_type('Category')
        else:
            self.select_col_reqt_type('Course requirement')
        self.enter_col_reqt_metadata(reqt)
        self.save_col_reqt()
        if isinstance(reqt, DegreeReqtCategory):
            boa_degree_progress_utils.set_category_id(template, reqt)
        else:
            boa_degree_progress_utils.set_course_reqt_id(template, reqt)

    def add_campus_reqts(self, col_num):
        self.click_add_col_reqt_button(col_num)
        self.select_col_reqt_type('Campus requirements')
        self.save_col_reqt()
        self.when_present(self.campus_reqt_row('Entry Level Writing'), utils.get_short_timeout())

    # View

    @staticmethod
    def top_cat_xpath(cat):
        return f'//div[@id="column-{cat.column_num}-category-{cat.category_id}"]'

    @staticmethod
    def sub_cat_xpath(sub_cat):
        return f'//div[@id="column-{sub_cat.parent.column_num}-subcategory-{sub_cat.category_id}"]'

    def cat_xpath(self, cat):
        return self.sub_cat_xpath(cat) if cat.parent else self.top_cat_xpath(cat)

    def cat_drop_zone_loc(self, cat):
        return By.XPATH, f'{self.cat_xpath(cat)}//div[@id="drop-zone-category"]'

    def cat_name_loc(self, cat):
        xpath = f'{self.sub_cat_xpath(cat)}//h4' if cat.parent else f'{self.top_cat_xpath(cat)}//h3'
        return By.XPATH, xpath

    def visible_cat_name(self, cat):
        return self.el_text_if_exists(self.cat_name_loc(cat))

    def visible_cat_desc(self, cat):
        return self.el_text_if_exists((By.XPATH,
                                       f'{self.cat_xpath(cat)}//div[contains(@id, "category-header-description")]'))

    @staticmethod
    def course_reqt_xpath(course):
        col_id = f'column-{course.parent.column_num}-courses-of-category-{course.parent.category_id}'
        return f'//table[@id="{col_id}"]//tr[contains(@id, "course-{course.course_id}-table-row")]'

    def course_reqt_row(self, course):
        return By.XPATH, self.course_reqt_xpath(course)

    def visible_template_course_reqt_name(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.course_reqt_xpath(course)}/td[2]'))

    def visible_template_course_reqt_units(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.course_reqt_xpath(course)}/td[3]'))

    def visible_template_course_reqt_fulfillment(self, course):
        return self.el_text_if_exists((By.XPATH, f'{self.course_reqt_xpath(course)}/td[4]'))

    @staticmethod
    def campus_reqts_xpath(col_num):
        return f'//div[contains(@id, "column-{col_num}-category")][contains(., "Campus Requirements")]'

    def campus_reqts_desc(self, col_num):
        time.sleep(1)
        return self.el_text_if_exists(
            (By.XPATH, f'{self.campus_reqts_xpath(col_num)}//div[contains(@id, "category-header-description")]'))

    @staticmethod
    def campus_reqt_row_xpath(reqt_name):
        return f'//tr[contains(., "{reqt_name}")]'

    def campus_reqt_row(self, reqt_name):
        return By.XPATH, self.campus_reqt_row_xpath(reqt_name)

    # Edit

    CAT_EDIT_BUTTON = By.XPATH, '//button[contains(@id, "-edit-category-")]'
    CAT_DELETE_BUTTON = By.XPATH, '//button[contains(@id, "-delete-category-")]'

    @staticmethod
    def cat_edit_button(cat):
        col = cat.parent.column_num if cat.parent else cat.column_num
        if isinstance(cat, DegreeReqtCourse):
            if cat.is_placeholder:
                cat_id = cat.parent.course_id
            else:
                cat_id = cat.course_id
        else:
            cat_id = cat.category_id
        return By.ID, f'column-{col}-edit-category-{cat_id}-btn'

    def click_edit_cat(self, cat):
        self.wait_for_element_and_click(self.cat_edit_button(cat))

    def edit_campus_reqts_button(self, col_num):
        return By.XPATH, f'{self.campus_reqts_xpath(col_num)}//button[contains(@id, "edit")]'

    def edit_campus_reqts_desc(self, col_num, new_desc):
        app.logger.info(f'Changing Campus requirements description to {new_desc}')
        self.wait_for_element_and_click(self.edit_campus_reqts_button(col_num))
        self.enter_col_reqt_desc(new_desc)
        self.click_create_col_reqt()

    # Delete

    @staticmethod
    def cat_delete_button(cat):
        col = cat.parent.column_num if cat.parent else cat.column_num
        cat_id = cat.course_id if isinstance(cat, DegreeReqtCourse) else cat.category_id
        return By.ID, f'column-{col}-delete-category-{cat_id}-btn'

    def click_delete_cat(self, cat):
        self.wait_for_element_and_click(self.cat_delete_button(cat))

    def campus_reqts_delete_button(self, col_num):
        return By.XPATH, f'{self.campus_reqts_xpath(col_num)}//button[contains(@id, "delete")]'

    def delete_campus_reqts(self, col_num):
        app.logger.info('Deleting Campus requirements')
        self.wait_for_element_and_click(self.campus_reqts_delete_button(col_num))
        self.click_confirm_delete()

    def complete_template(self, template):
        self.when_present(self.template_heading(template), utils.get_short_timeout())
        boa_degree_progress_utils.set_new_template_id(template)
        for u in template.unit_reqts:
            self.create_unit_reqt(u, template)
        for cat in template.categories:
            self.create_col_reqt(cat, template)
            for course in cat.course_reqts:
                self.create_col_reqt(course, template)
            for sub_cat in cat.sub_categories:
                self.create_col_reqt(sub_cat, template)
                for sub_course in sub_cat.course_reqts:
                    self.create_col_reqt(sub_course, template)
        self.add_campus_reqts(3)
