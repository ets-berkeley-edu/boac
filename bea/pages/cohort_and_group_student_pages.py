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

from bea.pages.cohort_pages import CohortPages
from bea.pages.list_view_student_pages import ListViewStudentPages
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class CohortAndGroupStudentPages(CohortPages, ListViewStudentPages):
    CONFIRM_EXPORT_LIST_BUTTON = By.ID, 'export-list-confirm'
    NO_ACCESS_MSG = By.XPATH, '//span[text()="You are unauthorized to access student data managed by other departments"]'
    TITLE_REQUIRED_MSG = By.XPATH, '//span[text()="Required"]'

    def confirm_export(self, cohort):
        is_filtered = cohort.__class__.__name__ == 'FilteredCohort'
        is_filtered_admits = cohort.search_criteria.__class__.__name__ == 'CohortAdmitFilter'
        is_group = cohort.__class__.__name__ == 'CuratedGroup'
        if (is_filtered and not is_filtered_admits) or is_group:
            self.wait_for_element_and_click(self.CONFIRM_EXPORT_LIST_BUTTON)

    def export_default_student_list(self, cohort):
        app.logger.info('Exporting student list with default columns')
        utils.prepare_download_dir()
        self.click_export_list()
        self.confirm_export(cohort)
        return utils.wait_for_export_csv()

    def export_custom_student_list(self, cohort):
        app.logger.info('Exporting student list with default columns')
        utils.prepare_download_dir()
        self.click_export_list()
        for i in range(19):
            loc = (By.ID, f'csv-column-options_BV_option_{i}')
            self.wait_for_element(loc, utils.get_short_timeout())
            self.click_element_js(loc)
        self.confirm_export(cohort)
        return utils.wait_for_export_csv()

    @staticmethod
    def verify_default_export_student_list(cohort, csv_reader):
        sids = []
        first_names = []
        last_names = []
        emails = []
        phones = []
        for r in csv_reader:
            sids.append(r['sid'])
            first_names.append(r['first_name'])
            last_names.append(r['last_name'])
            emails.append(r['email'])
            phones.append(r['phone'])
        sids.sort()
        cohort_sids = list(map(lambda m: m.sid, cohort.members))
        cohort_sids.sort()
        assert sids == cohort_sids
        assert list(filter(lambda fi: fi, first_names))
        assert list(filter(lambda la: la, last_names))
        assert list(filter(lambda em: em, emails))
        assert list(filter(lambda ph: ph, phones))

    @staticmethod
    def verify_custom_export_student_list(cohort, csv_reader):
        prev_term_sis_id = utils.get_prev_term_sis_id()
        prev_prev_term_sis_id = utils.get_prev_term_sis_id(prev_term_sis_id)
        majors = []
        minors = []
        subplans = []
        levels_by_units = []
        terms_in_attend = []
        expected_grad_terms = []
        units_complete = []
        gpas_last_term = []
        gpas_last_last_term = []
        cumul_gpas = []
        program_statuses = []
        transfers = []
        intended_majors = []
        units_in_progress = []
        for r in csv_reader:
            majors.append(r['majors'])
            minors.append(r['minors'])
            subplans.append(r['subplans'])
            levels_by_units.append(r['level_by_units'])
            terms_in_attend.append(r['terms_in_attendance'])
            expected_grad_terms.append(r['expected_graduation_term'])
            units_complete.append(r['units_completed'])
            gpas_last_term.append(r[f'term_gpa_{prev_term_sis_id}'])
            gpas_last_last_term.append(r[f'term_gpa_{prev_prev_term_sis_id}'])
            cumul_gpas.append(r['cumulative_gpa'])
            program_statuses.append(r['program_status'])
            transfers.append(r['transfer'])
            intended_majors.append(r['intended_major'])
            units_in_progress.append(r['units_in_progress'])
        assert list(filter(lambda ma: ma, majors))
        assert list(filter(lambda mi: mi, minors))
        assert list(filter(lambda su: su, subplans))
        assert list(filter(lambda le: le, levels_by_units))
        assert list(filter(lambda te: te, terms_in_attend))
        assert list(filter(lambda ex: ex, expected_grad_terms))
        assert list(filter(lambda uc: uc, units_complete))
        assert list(filter(lambda gpl: gpl, gpas_last_term))
        assert list(filter(lambda gpll: gpll, gpas_last_last_term))
        assert list(filter(lambda cu: cu, cumul_gpas))
        assert list(filter(lambda pr: pr, program_statuses))
        assert list(filter(lambda tr: tr, transfers))
        assert list(filter(lambda ima: ima, intended_majors))
        assert list(filter(lambda up: up, units_in_progress))

    # LIST VIEW - shared by filtered cohorts and curated groups

    TERM_SELECT_BUTTON = By.ID, 'students-term-select__BV_toggle_'
    SITE_ACTIVITY_HEADER = By.XPATH, '//th[contains(., "bCourses Activity")]'

    @staticmethod
    def term_select_option(term):
        return By.ID, f'term-select-option-{term.sis_id}'

    def select_term(self, term):
        app.logger.info(f'Selecting term ID {term.sis_id}')
        self.wait_for_element_and_click(self.TERM_SELECT_BUTTON)
        self.wait_for_element_and_click(self.term_select_option(term))

    def scroll_to_student(self, student):
        self.scroll_to_element(self.element((By.XPATH, self.student_row_xpath(student))))

    def visible_sis_data(self, student):
        self.wait_for_players()
        student_xpath = self.student_row_xpath(student)
        level_loc = By.XPATH, f'{student_xpath}//div[contains(@id, "student-level")]'
        level = self.element(level_loc).text.strip() if self.is_present(level_loc) else None
        majors_loc = By.XPATH, f'{student_xpath}//span[contains(@id, "student-major")]'
        majors = list(map(lambda ma: ma.text, self.elements(majors_loc)))
        entered_term_loc = By.XPATH, f'{student_xpath}//div[contains(@id, "student-matriculation")]'
        entered_term = self.element(entered_term_loc).text.replace('Entered', '').strip() if self.is_present(
            entered_term_loc) else None
        grad_term_loc = By.XPATH, f'{student_xpath}//div[contains(@id, "student-grad-term")]'
        grad_term = self.element(grad_term_loc).text().split(':')[1].strip() if self.is_present(grad_term_loc) else None
        graduation_loc = By.XPATH, f'{student_xpath}//div[starts-with(text(), " Graduated")]'
        graduation = self.element(graduation_loc).text.replace('Graduated', '').strip() if self.is_present(
            graduation_loc) else None
        sports_loc = By.XPATH, f'{student_xpath}//span[contains(@id, "student-team")]'
        sports = list(map(lambda sp: sp.text, self.elements(sports_loc)))
        gpa_loc = By.XPATH, f'{student_xpath}//span[contains(@id, "student-cumulative-gpa")]'
        gpa = self.element(gpa_loc).text.gsub('No data', '').strip() if self.is_present(gpa_loc) else None
        classes_loc = By.XPATH, f'{student_xpath}//span[contains(@id, "student-enrollment-name")]'
        classes = list(map(lambda cl: cl.text, self.elements(classes_loc)))
        waitlists_loc = By.XPATH, f'{student_xpath}//span[contains(@id, "-waitlisted-")]/preceding-sibling::span'
        waitlists = list(map(lambda wa: wa.text, self.elements(waitlists_loc)))
        inactive_loc = By.XPATH, f'{student_xpath}//div[contains(@class, "student-sid")]/div[contains(@id, "-inactive")]'
        inactive = self.is_present(inactive_loc) and self.element(inactive_loc).text.strip() == 'INACTIVE'
        # TODO academic_standing
        cxl_loc = By.XPATH, f'{student_xpath}//div[contains(@id, "withdrawal-cancel")]/span'
        cxl_msg = self.element(cxl_loc).text.strip() if self.is_present(cxl_loc) else None
        return {
            'level': level,
            'majors': majors,
            'entered_term': entered_term,
            'grad_term': grad_term,
            'graduation': graduation,
            'sports': sports,
            'gpa': gpa,
            'classes': classes,
            'waitlists': waitlists,
            'inactive': inactive,
            # TODO academic standing
            'cxl_msg': cxl_msg,
        }

    def visible_term_units(self, student):
        xpath = self.student_row_xpath(student)
        units_loc = By.XPATH, f'{xpath}//div[contains(@id, "student-enrolled-units")]'
        cumul_units_loc = By.XPATH, f'{xpath}//div[contains(@id, "cumulative-units")]'
        max_loc = By.XPATH, f'{xpath}//span[contains(@id, "student-max-units")]'
        min_loc = By.XPATH, f'{xpath}//div[contains(@id, "student-min-units")]'
        return {
            'term_units': (self.element(units_loc).text if self.is_present(units_loc) else None),
            'cumul_units': (self.element(cumul_units_loc).text.replce('No data', '').strip() if self.is_present(
                cumul_units_loc) else None),
            'term_units_max': (self.element(max_loc).text if self.is_present(max_loc) else None),
            'term_units_min': (self.element(min_loc).text if self.is_present(min_loc) else None),
        }

    def visible_courses_data(self, student):
        self.wait_for_players()
        row_xpath = f'{self.student_row_xpath(student)}//tbody/tr'
        row_els = self.elements((By.XPATH, row_xpath))
        rows_data = []
        for el in row_els:
            node_xpath = f'{row_xpath}[{row_els.index(el) + 1}]'
            mid_flag_loc = By.XPATH, f'{node_xpath}/td[4]/*[@data-icon="triangle-exclamation"]'
            final_flag_loc = By.XPATH, f'{node_xpath}/td[5]/*[@data-icon="triangle-exclamation"]'
            rows_data.append({
                'course_code': self.element((By.XPATH, f'{node_xpath}/td[1]')).text,
                'units': self.element((By.XPATH, f'{node_xpath}/td[2]')).text,
                'activity': self.element((By.XPATH, f'{node_xpath}/td[3]')).text,
                'mid_grade': self.element((By.XPATH, f'{node_xpath}/td[4]')).text,
                'mid_flag': self.is_present(mid_flag_loc),
                'final_grade': self.element((By.XPATH, f'{node_xpath}/td[5]')).text,
                'final_flag': self.is_present(final_flag_loc),
            })

    # SORTING

    def sort_by_team(self):
        self.sort_by('group_name')

    def sort_by_gpa_cumulative(self):
        self.sort_by('gpa')

    def sort_by_gpa_cumulative_desc(self):
        self.sort_by('gpa desc')

    def sort_by_last_term_gpa(self, term=None):
        term = term or utils.get_previous_term()
        self.sort_by(f'term_gpa_{term.sis_id}')

    def sort_by_last_term_gpa_desc(self, term=None):
        term = term or utils.get_previous_term()
        self.sort_by(f'term_gpa_{term.sis_id} desc')

    def sort_by_level(self):
        self.sort_by('level')

    def sort_by_student_major(self):
        self.sort_by('major')

    def sort_by_entering_term(self):
        self.sort_by('entering_term')

    def sort_by_expected_graduation(self):
        self.sort_by('expected_grad_term')

    def sort_by_terms_in_attend(self):
        self.sort_by('terms_in_attendance')

    def sort_by_terms_in_attend_desc(self):
        self.sort_by('terms_in_attendance desc')

    def sort_by_units_in_progress(self):
        self.sort_by('enrolled_units')

    def sort_by_units_in_progress_desc(self):
        self.sort_by('enrolled_units desc')

    def sort_by_units_completed(self):
        self.sort_by('units')

    def sort_by_units_completed_desc(self):
        self.sort_by('units desc')
