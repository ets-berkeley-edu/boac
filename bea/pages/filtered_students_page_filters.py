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
import datetime
import time

from bea.models.cohorts_and_groups.cohort_filter import CohortFilter
from bea.pages.filtered_students_page_results import FilteredStudentsPageResults
from bea.test_utils import utils
from flask import current_app as app
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class FilteredStudentsPageFilters(FilteredStudentsPageResults):
    # NEW FILTERED COHORTS

    NEW_FILTER_SELECT = By.ID, 'filter-select-primary-new'
    NEW_FILTER_OPTION = By.XPATH, '//option[starts-with(@id, "primary-")]'
    NEW_SUB_FILTER_SELECT = By.XPATH, '//select[contains(@id, "filter-select-secondary-")]'
    NEW_SUB_FILTER_OPTION = By.XPATH, '//option[starts-with(@id, "secondary-")]'
    FILTER_RANGE_MIN_INPUT = By.XPATH, '//input[contains(@id, "filter-range-min")]'
    FILTER_RANGE_MAX_INPUT = By.XPATH, '//input[contains(@id, "filter-range-max")]'
    UNSAVED_FILTER_ADD_BUTON = By.ID, 'unsaved-filter-add'
    UNSAVED_FILTER_CANCEL_BUTON = By.ID, 'unsaved-filter-reset'
    UNSAVED_FILTER_APPLY_BUTTON = By.ID, 'unsaved-filter-apply'
    GPA_FILTER_RANGE_ERROR = By.XPATH, '//span[text()="GPA must be a number in the range 0 to 4."]'
    GPA_FILTER_LOGICAL_ERROR = By.XPATH, '//span[text()="GPA inputs must be in ascending order."]'
    LAST_NAME_FILTER_LOGICAL_ERROR = By.XPATH, '//span[text()="Requires letters in ascending order."]'

    def click_new_filter_select(self):
        try:
            self.wait_for_element_and_click(self.NEW_FILTER_SELECT)
        except StaleElementReferenceException:
            self.wait_for_element_and_click(self.NEW_FILTER_SELECT)

    def filter_options(self):
        Wait(self.driver, utils.get_short_timeout()).until(ec.presence_of_all_elements_located(self.NEW_FILTER_OPTION))
        return list(map(lambda el: el.text.strip(), self.elements(self.NEW_FILTER_OPTION)))

    def select_new_filter_option(self, filter_option):
        app.logger.info(f'Selecting filter {filter_option}')
        self.wait_for_select_and_click_option(self.NEW_FILTER_SELECT, filter_option)

    @staticmethod
    def filter_sub_option_identifier(filter_option, filter_sub_option):
        if filter_option == 'Ethnicity (COE)':
            return CohortFilter.coe_ethnicity_per_code(filter_sub_option)
        elif filter_option == 'Visa Type':
            if filter_sub_option == 'All types':
                return filter_sub_option
            else:
                return CohortFilter.visa_type_per_code(filter_sub_option)
        elif filter_option == 'Level':
            return CohortFilter.level_per_code(filter_sub_option)
        elif filter_option == 'Entering Term':
            return ' '.join(reversed(filter_sub_option.split(' ')))
        else:
            return filter_sub_option

    def enter_filter_range_min(self, minimum):
        self.wait_for_textbox_and_type(self.FILTER_RANGE_MIN_INPUT, minimum)

    def enter_filter_range_max(self, maximum):
        self.wait_for_textbox_and_type(self.FILTER_RANGE_MAX_INPUT, maximum)

    def select_new_filter_sub_option(self, filter_option, filter_sub_option):
        filter_sub_option = self.filter_sub_option_identifier(filter_option, filter_sub_option)
        app.logger.info(f'Selecting sub-option {filter_sub_option}')
        if filter_option in [
            'GPA (Cumulative)', 'GPA (Last Term)', 'Last Name', 'Family Dependents', 'Student Dependents',
            'Incomplete Pending Grades',
        ]:
            if filter_option == 'Incomplete Pending Grades':
                minimum = datetime.datetime.strptime(filter_sub_option['min'], '%Y-%m-%d').strftime('%m/%d/%Y')
                maximum = datetime.datetime.strptime(filter_sub_option['max'], '%Y-%m-%d').strftime('%m/%d/%Y')
            else:
                minimum = filter_sub_option['min']
                maximum = filter_sub_option['max']
            self.enter_filter_range_min(minimum)
            self.enter_filter_range_max(maximum)
        else:
            self.wait_for_element_and_click(self.NEW_SUB_FILTER_SELECT)
            self.matching_option(self.NEW_SUB_FILTER_SELECT, filter_sub_option).click()

    def select_new_filter(self, filter_option, filter_sub_option=None):
        self.select_new_filter_option(filter_option)
        no_options = ['Midpoint Deficient Grade', 'Transfer Student', 'Underrepresented Minority', 'Inactive (ASC)',
                      'Intensive (ASC)', 'Inactive (COE)', 'Underrepresented Minority (COE)', 'Probation (COE)',
                      'Current SIR', 'Hispanic', 'UREM', 'First Generation College', 'Application Fee Waiver',
                      'Foster Care', 'Family Is Single Parent', 'Student Is Single Parent', 'Re-entry Status',
                      'Last School LCFF+', 'Holds']
        if filter_option not in no_options:
            self.select_new_filter_sub_option(filter_option, filter_sub_option)
        self.wait_for_element_and_click(self.UNSAVED_FILTER_ADD_BUTON)

    def perform_student_search(self, cohort):
        # Academic
        for career in cohort.search_criteria.academic_careers:
            self.select_new_filter('Academic Career', career)
        for division in cohort.search_criteria.academic_divisions:
            self.select_new_filter('Academic Division', division)
        for standing in cohort.search_criteria.academic_standings:
            self.select_new_filter('Academic Standing', standing)
        for status in cohort.search_criteria.career_statuses:
            self.select_new_filter('Career Status', status)
        for college in cohort.search_criteria.colleges:
            self.select_new_filter('College', college)
        for degree in cohort.search_criteria.degrees_awarded:
            self.select_new_filter('Degree Awarded', degree)
        for degree_term in cohort.search_criteria.degree_terms:
            self.select_new_filter('Degree Term', str(degree_term))
        for entering_term in cohort.search_criteria.entering_terms:
            self.select_new_filter('Entering Term', str(entering_term))
        for epn_term in cohort.search_criteria.grading_basis_epn:
            self.select_new_filter('EPN/CPN Grading Option', str(epn_term))
        for grad_term in cohort.search_criteria.expected_grad_terms:
            self.select_new_filter('Expected Graduation Term', grad_term)
        for gpa in cohort.search_criteria.gpa_ranges:
            self.select_new_filter('GPA (Cumulative)', gpa)
        for last_gpa in cohort.search_criteria.gpa_ranges_last_term:
            self.select_new_filter('GPA (Last Term)', last_gpa)
        for grad_plan in cohort.search_criteria.graduate_plans:
            self.select_new_filter('Graduate Plan', grad_plan)
        if cohort.search_criteria.holds:
            self.select_new_filter('Holds')
        for incomplete in cohort.search_criteria.incomplete_grades:
            self.select_new_filter('Incomplete Grade', incomplete)
        for incomplete_sched in cohort.search_criteria.incomplete_sched_grades:
            self.select_new_filter('Incomplete Pending Grades', incomplete_sched)
        for intended in cohort.search_criteria.intended_majors:
            self.select_new_filter('Intended Major', intended)
        for level in cohort.search_criteria.levels:
            self.select_new_filter('Level', level)
        for major in cohort.search_criteria.majors:
            self.select_new_filter('Major', major)
        if cohort.search_criteria.mid_point_deficient:
            self.select_new_filter('Midpoint Deficient Grade')
        for minor in cohort.search_criteria.minors:
            self.select_new_filter('Minor', minor)
        if cohort.search_criteria.transfer_student:
            self.select_new_filter('Transfer Student')
        for units in cohort.search_criteria.units_completed:
            self.select_new_filter('Units Completed', units)

        # Demographics
        for ethnicity in cohort.search_criteria.ethnicities:
            self.select_new_filter('Ethnicity', ethnicity)
        for initials in cohort.search_criteria.last_name:
            self.select_new_filter('Last Name', initials)
        if cohort.search_criteria.underrepresented_minority:
            self.select_new_filter('Underrepresented Minority')
        for visa in cohort.search_criteria.visa_types:
            self.select_new_filter('Visa Type', visa)

        # ASC
        if cohort.search_criteria.asc_inactive:
            self.select_new_filter('Inactive (ASC)')
        if cohort.search_criteria.asc_intensive:
            self.select_new_filter('Intensive (ASC)')
        for squad in cohort.search_criteria.asc_teams:
            self.select_new_filter('Team (ASC)', squad.value['name'])

        # CoE
        for advisor in cohort.search_criteria.coe_advisors:
            self.select_new_filter('Advisor (COE)', advisor)
        for ethnicity in cohort.search_criteria.coe_ethnicities:
            self.select_new_filter('Ethnicity (COE)', ethnicity)
        for prep in cohort.search_criteria.coe_preps:
            self.select_new_filter('PREP (COE)', prep)
        if cohort.search_criteria.coe_probation:
            self.select_new_filter('Probation (COE)')
        if cohort.search_criteria.coe_inactive:
            self.select_new_filter('Inactive (COE)')
        if cohort.search_criteria.coe_underrepresented_minority:
            self.select_new_filter('Underrepresented Minority (COE)')

        # Advising
        # TODO - 'My Curated Groups'
        for plan in cohort.search_criteria.my_students:
            self.select_new_filter('My Students', plan)

        self.execute_search()

    # TODO - def perform_admit_search()

    def execute_search(self):
        self.wait_for_element_and_click(self.UNSAVED_FILTER_APPLY_BUTTON)
        self.wait_for_search_results()

    # EXISTING FILTERED COHORTS - Viewing

    TOGGLE_FILTERS_VISIBILITY_BUTTON = By.ID, 'show-hide-details-button'
    SHOW_FILTERS_BUTTON = By.XPATH, '//button[contains(.,"Show Filters")]'
    COHORT_FILTER_ROW = By.CLASS_NAME, 'filter-row'

    def show_filters(self):
        self.when_visible(self.TOGGLE_FILTERS_VISIBILITY_BUTTON, utils.get_short_timeout())
        if self.is_present(self.SHOW_FILTERS_BUTTON):
            self.element(self.SHOW_FILTERS_BUTTON).click()

    @staticmethod
    def existing_filter_xpath(filter_name):
        if filter_name in ['Ethnicity', 'Underrepresented Minority']:
            return f'//div[contains(@class,"filter-row")]/div[contains(.,"{filter_name}") and not(contains(.,"COE"))]'
        elif filter_name == 'Major':
            return f'//div[contains(@class,"filter-row")]/div[contains(.,"{filter_name}") and not(contains(.,"Intended"))]'
        else:
            return f'//div[contains(@class,"filter-row")]/div[contains(.,"{filter_name}")]'

    def existing_filter_loc(self, filter_name, filter_opt=None):
        option_xpath = f'{self.existing_filter_xpath(filter_name)}/following-sibling::div'
        if filter_name in ['Inactive', 'Inactive (ASC)', 'Inactive (COE)', 'Intensive (ASC)', 'Probation (COE)',
                           'Transfer Student', 'Underrepresented Minority', 'Underrepresented Minority (COE)',
                           'Current SIR', 'Hispanic', 'UREM', 'First Generation College', 'Holds', 'Incomplete Grade',
                           'Application Fee Waiver', 'Foster Care', 'Family Is Single Parent',
                           'Student Is Single Parent', 'Re-entry Status', 'Last School LCFF+']:
            return By.XPATH, self.existing_filter_xpath(filter_name)
        elif filter_opt == 'Last Name':
            return By.XPATH, f"{option_xpath}[contains(text(),\"{filter_opt['min']} through {filter_opt['max']}\")]"
        elif filter_name in ['GPA (Cumulative)', 'GPA (Last Term)']:
            return (
                By.XPATH,
                f"{option_xpath}[contains(.,\"{'{:.3f} - {:.3f}'.format(float(filter_opt['min']), float(filter_opt['max']))}\")]")
        elif filter_name in ['Family Dependents', 'Student Dependents']:
            return By.XPATH, f"{option_xpath}[contains(.,'{filter_opt['min']} - {filter_opt['max']}')]"
        elif filter_name == 'Ethnicity':
            return By.XPATH, f'{option_xpath}[contains(.,"{filter_opt}") and not(contains(.,"COE"))]'
        else:
            return By.XPATH, f'{option_xpath}[contains(.,"{filter_opt}")]'

    # EXISTING FILTERED COHORTS - Editing

    COHORT_EDIT_BUTTON = By.XPATH, '//button[contains(@id, "edit-added-filter")]'
    COHORT_UPDATE_BUTTON = By.XPATH, '//button[contains(text(), "Update")]'
    COHORT_UPDATE_CANCEL_BUTTON = By.XPATH, '//button[contains(text(), "Cancel")]'

    def filter_controls_xpath(self, filter_option):
        return f'{self.existing_filter_xpath(filter_option)}/following-sibling::div[2]'

    def filter_edit_button(self, filter_option):
        return By.XPATH, f'{self.filter_controls_xpath(filter_option)}//button[contains(., "Edit")]'

    def filter_edit_cancel_button(self, filter_option):
        return By.XPATH, f'{self.filter_controls_xpath(filter_option)}//button[contains(., "Cancel")]'

    def filter_edit_update_button(self, filter_option):
        return By.XPATH, f'{self.filter_controls_xpath(filter_option)}//button[contains(., "Update")]'

    def filter_remove_button(self, filter_option):
        return By.XPATH, f'{self.filter_controls_xpath(filter_option)}//button[contains(., "Remove")]'

    def cancel_cohort_update(self):
        if self.is_present(self.COHORT_UPDATE_CANCEL_BUTTON):
            self.wait_for_element_and_click(self.COHORT_UPDATE_CANCEL_BUTTON)

    def edit_filter(self, filter_option, filter_sub_option):
        app.logger.info(f'Changing {filter_option} to {filter_sub_option}')
        self.wait_for_element_and_click(self.filter_edit_button(filter_option))
        self.select_new_filter_sub_option(filter_option, filter_sub_option)
        self.wait_for_element_and_click(self.filter_edit_update_button(filter_option))
        self.when_not_present(self.filter_edit_update_button(filter_option), utils.get_short_timeout())

    def remove_filter_of_type(self, filter_option):
        app.logger.info(f'Removing {filter_option}')
        row_count = len(self.elements(self.COHORT_FILTER_ROW))
        self.wait_for_element_and_click(self.filter_remove_button(filter_option))
        tries = utils.get_short_timeout()
        while tries > 0:
            tries -= 1
            try:
                assert len(self.elements(self.COHORT_FILTER_ROW)) == row_count - 1
                break
            except AssertionError:
                if tries == 0:
                    raise
                else:
                    time.sleep(1)

    def verify_student_filters_present(self, cohort):
        filters = cohort.search_criteria
        has_non_empty_filters = any([True for k, v in filters.data.items() if v])
        if filters and has_non_empty_filters:
            self.show_filters()
            Wait(self.driver, utils.get_short_timeout()).until(
                ec.presence_of_all_elements_located(self.COHORT_FILTER_ROW))
            for a in filters.academic_standings:
                assert self.is_present(self.existing_filter_loc('academicStandings', a))
            for c in filters.colleges:
                assert self.is_present(self.existing_filter_loc('College', c))
            for c in filters.career_statuses:
                assert self.is_present(self.existing_filter_loc('Career Status', c))
            for d in filters.degrees_awarded:
                assert self.is_present(self.existing_filter_loc('Degree Awarded', d))
            for d in filters.degree_terms:
                assert self.is_present(self.existing_filter_loc('Degree Term', d))
            for e in filters.entering_terms:
                assert self.is_present(self.existing_filter_loc('Entering Term', e))
            for e in filters.expected_grad_terms:
                assert self.is_present(self.existing_filter_loc('Expected Graduation Term', e))
            for g in filters.gpa_ranges:
                assert self.is_present(self.existing_filter_loc('GPA (Cumulative)', g))
            for g in filters.gpa_ranges_last_term:
                assert self.is_present(self.existing_filter_loc('GPA (Last Term)', g))
            for g in filters.graduate_plans:
                assert self.is_present(self.existing_filter_loc('Graduate Plans', g))
            for g in filters.grading_basis_epn:
                assert self.is_present(self.existing_filter_loc('EPN/CPN Grading Option', g))
            if filters.holds:
                assert self.is_present(self.existing_filter_loc('Holds'))
            for i in filters.incomplete_grades:
                assert self.is_present(self.existing_filter_loc('Incomplete Grade', i))
            for i in filters.incomplete_sched_grades:
                assert self.is_present(self.existing_filter_loc('Incomplete Pending Grades', i))
            for i in filters.intended_majors:
                assert self.is_present(self.existing_filter_loc('Intended Major', i))
            for lev in filters.levels:
                assert self.is_present(self.existing_filter_loc('Level', lev))
            for m in filters.majors:
                assert self.is_present(self.existing_filter_loc('Major', m))
            if filters.mid_point_deficient:
                assert self.is_present(self.existing_filter_loc('Midpoint Deficient Grade'))
            for m in filters.minors:
                assert self.is_present(self.existing_filter_loc('Minor', m))
            if filters.transfer_student:
                assert self.is_present(self.existing_filter_loc('Transfer Student'))
            for u in filters.units_completed:
                assert self.is_present(self.existing_filter_loc('Units Completed', u))

            for e in filters.ethnicities:
                assert self.is_present(self.existing_filter_loc('Ethnicity', e))
            if filters.underrepresented_minority:
                assert self.is_present(self.existing_filter_loc('Underrepresented Minority'))
            for v in filters.visa_types:
                assert self.is_present(self.existing_filter_loc('Visa Type', v))

            if filters.asc_inactive:
                assert self.is_present(self.existing_filter_loc('Inactive (ASC)'))
            if filters.asc_intensive:
                assert self.is_present(self.existing_filter_loc('Intensive (ASC)'))
            for squad in filters.asc_teams:
                assert self.is_present(self.existing_filter_loc('Team (ASC)', squad.value['name']))

            for e in filters.coe_ethnicities:
                assert self.is_present(self.existing_filter_loc('Ethnicity (COE)', e))
            if filters.coe_inactive:
                assert self.is_present(self.existing_filter_loc('Inactive (COE)'))
            for p in filters.coe_preps:
                assert self.is_present(self.existing_filter_loc('PREP (COE)'))
            if filters.coe_probation:
                assert self.is_present(self.existing_filter_loc('Probation (COE)'))
            if filters.coe_underrepresented_minority:
                assert self.is_present(self.existing_filter_loc('Underrepresented Minority (COE)'))

            for n in filters.last_name:
                assert self.is_present(self.existing_filter_loc('Last Name', n))
            for m in filters.my_students:
                assert self.is_present(self.existing_filter_loc('My Students', m))

        else:
            self.when_not_visible(self.UNSAVED_FILTER_APPLY_BUTTON, utils.get_short_timeout())
            assert not self.elements(self.COHORT_FILTER_ROW)
