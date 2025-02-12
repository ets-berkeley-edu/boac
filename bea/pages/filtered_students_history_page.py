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
from datetime import datetime

from bea.pages.filtered_students_page import FilteredStudentsPage
from bea.test_utils import utils
from flask import current_app as app
from selenium.webdriver.common.by import By


class FilteredStudentsHistoryPage(FilteredStudentsPage):

    NO_HISTORY_MSG = By.ID, 'cohort-history-no-events'
    HISTORY_ROW = By.XPATH, '//table[@id="cohort-history-table"]/tbody/tr'

    def wait_for_history(self):
        self.when_present(self.HISTORY_ROW, utils.get_medium_timeout())

    def visible_row_data(self):
        rows = self.elements(self.HISTORY_ROW)
        rows_data = []
        for row in rows:
            idx = rows.index(row)
            rows_data.append({
                'status': self.el_text_if_exists((By.ID, f'event-{idx}-status')),
                'date': self.el_text_if_exists((By.ID, f'event-{idx}-date')),
                'name': self.el_text_if_exists((By.ID, f'event-{idx}-student-name')),
                'sid': self.el_text_if_exists((By.ID, f'event-{idx}-sid')),
            })
        return rows_data

    def visible_history_entries(self):
        entries = []
        self.wait_for_history()
        page_count = self.list_view_page_count()
        page = 1
        if page_count == 1:
            app.logger.info('There is 1 page')
            entries.extend(self.visible_row_data())
        else:
            app.logger.info(f'There are {page_count} pages')
            entries.extend(self.visible_row_data())
            for i in range(page_count - 1):
                page += 1
                self.wait_for_element_and_click(self.go_to_page_link(page))
                self.wait_for_history()
                entries.extend(self.visible_row_data())
        entries.sort(key=lambda h: [h['sid'], h['status']])
        return entries

    @staticmethod
    def expected_history_entries(students, status, date=None):
        entries = []
        date = date or datetime.today()
        expected_date = datetime.strftime(date, '%b %-d, %Y')
        for stu in students:
            entries.append({
                'status': status,
                'date': expected_date,
                'name': f'{stu.last_name}, {stu.first_name}',
                'sid': str(stu.sid),
            })
        entries.sort(key=lambda e: e['sid'])
        return entries

    def click_back_to_cohort(self):
        app.logger.info('Clicking back-to-cohort button')
        self.wait_for_element_and_click(self.BACK_TO_COHORT_LINK)
