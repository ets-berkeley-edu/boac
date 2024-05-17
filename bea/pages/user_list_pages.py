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

from bea.pages.boa_pages import BoaPages
from flask import current_app as app
from selenium.webdriver.common.by import By


class UserListPages(BoaPages):

    @staticmethod
    def filtered_cohort_xpath(cohort):
        return f'//div[@id="sortable-cohort-{cohort.cohort_id}-details"]'

    @staticmethod
    def curated_group_xpath(group):
        return f'//div[@id="sortable-curated-{group.cohort_id}-details"]'

    def all_row_sids(self, cohort=None):
        xpath = self.filtered_cohort_xpath(cohort) if cohort and cohort.__class__.__name__ == 'FilteredCohort' else ''
        els = self.elements((By.XPATH, f'{xpath}//span[contains(text(), \"S I D\")]/following-sibling::span'))
        return list(map(lambda el: el.text, els))

    def user_row_data(self, sid, cohort=None):
        xpath = self.filtered_cohort_xpath(cohort) if cohort and cohort.__class__.__name__ == 'FilteredCohort' else ''
        row_xpath = f'{xpath}//tr[contains(., "{sid}")]'
        name_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"Student name\")]/following-sibling::a'
        sid_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"S I D\")]/following-sibling::span'
        major_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"Major\")]/following-sibling::div'
        term_units_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"Term units\")]/following-sibling::div'
        cumul_units_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"Units completed\")]/following-sibling::div'
        no_cumul_units_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"Units completed\")]/following-sibling::div/span'
        gpa_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"GPA\")]/following-sibling::div'
        no_gpa_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"GPA\")]/following-sibling::div/span'
        alerts_loc = By.XPATH, f'{row_xpath}//span[contains(text(), \"Issue count\")]/following-sibling::div'
        if self.is_present(cumul_units_loc):
            units = self.element(cumul_units_loc).text
        elif self.is_present(no_cumul_units_loc):
            units = self.element(no_cumul_units_loc).text
        else:
            units = None
        if self.is_present(gpa_loc):
            gpa = self.element(gpa_loc).text
        elif self.is_present(no_gpa_loc):
            gpa = self.element(no_gpa_loc).text
        else:
            gpa = None
        return {
            'name': (self.element(name_loc).text if self.is_present(name_loc) else None),
            'sid': (self.element(sid_loc).text if self.is_present(sid_loc) else None),
            'major': (list(map(lambda el: el.text, self.elements(major_loc)))),
            'term_units': (self.element(term_units_loc).text if self.is_present(term_units_loc) else None),
            'cumulative_units': units,
            'gpa': gpa,
            'alert_count': (self.element(alerts_loc).text if self.is_present(alerts_loc) else None),
        }

    def sort_by_option(self, option, cohort=None):
        app.logger.info(f'Sorting by {option}')
        if cohort and cohort.__class__.__name__ == 'FilteredCohort':
            xpath = self.filtered_cohort_xpath(cohort)
        else:
            xpath = ''
        self.wait_for_element_and_click((By.XPATH, f'{xpath}//th[contains(.,"{option}")]'))

    def sort_by_name(self, cohort=None):
        self.sort_by_option('Name', cohort)

    def sort_by_sid(self, cohort=None):
        self.sort_by_option('SID', cohort)

    def sort_by_major(self, cohort=None):
        self.sort_by_option('Major', cohort)

    def sort_by_expected_grad(self, cohort=None):
        self.sort_by_option('Grad', cohort)

    def sort_by_term_units(self, cohort=None):
        self.sort_by_option('Term units', cohort)

    def sort_by_cumul_units(self, cohort=None):
        self.sort_by_option('Units completed', cohort)

    def sort_by_gpa(self, cohort=None):
        self.sort_by_option('GPA', cohort)

    def sort_by_alert_count(self, cohort=None):
        self.sort_by_option('Alerts', cohort)

    @staticmethod
    def expected_sids_by_alerts(users):
        users.sort(key=lambda u: (u.alert_count, u.last_name.lower(), u.first_name.lower(), u.sid), reverse=False)
        return list(map(lambda u: u.sid, users))

    @staticmethod
    def expected_sids_by_alerts_desc(users):
        users.sort(key=lambda u: (u.last_name.lower(), u.first_name.lower(), u.sid), reverse=False)
        users.sort(key=lambda u: u.alert_count, reverse=True)
        return list(map(lambda u: u.sid, users))

    @staticmethod
    def verify_list_view_sorting(visible_sids, expected_sids):
        # Only compare sort order for SIDs that are both expected and visible
        if not sorted(expected_sids) == sorted(visible_sids):
            expected_sids = [s for s in expected_sids if s in visible_sids]
            visible_sids = [s for s in visible_sids if s in expected_sids]
        sorting_errors = []
        for v in visible_sids:
            e = expected_sids[visible_sids.index(v)]
            if not v == e:
                sorting_errors.append(f'Expected {e}, got {v}')
        app.logger.info(f'Mismatches: {sorting_errors}')
        assert not sorting_errors
