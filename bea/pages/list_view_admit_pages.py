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

from bea.pages.admit_pages import AdmitPages
from bea.pages.pagination import Pagination
from selenium.webdriver.common.by import By


class ListViewAdmitPages(Pagination, AdmitPages):

    @staticmethod
    def admit_row_xpath(admit):
        return f'//a[contains(@href, "/admit/student/{admit.sid}")]/ancestor::tr'

    def visible_admit_row_text(self, admit, node, label_text=None):
        loc = By.XPATH, f'{self.admit_row_xpath(admit)}/td[{node}]'
        return self.element(loc).text.replace(label_text, '').strip() if self.is_present(loc) else None

    def visible_admit_name(self, admit):
        loc = By.ID, f'link-to-admit-{admit.sid}'
        return self.element(loc).text if self.is_present(loc) else None

    def visible_admit_sid(self, admit):
        return self.visible_admit_row_text(admit, 3, 'C S I D')

    def visible_admit_sir(self, admit):
        return self.visible_admit_row_text(admit, 4, 'S I R')

    def visible_admit_cep(self, admit):
        return self.visible_admit_row_text(admit, 5, 'C E P')

    def visible_admit_re_entry(self, admit):
        return self.visible_admit_row_text(admit, 6, 'Re-entry')

    def visible_admit_1st_gen_college(self, admit):
        return self.visible_admit_row_text(admit, 7, 'First generation')

    def visible_admit_urem(self, admit):
        return self.visible_admit_row_text(admit, 8, 'U R E M')

    def visible_admit_fee_waiver(self, admit):
        return self.visible_admit_row_text(admit, 9, 'Waiver')

    def visible_admit_residency(self, admit):
        return self.visible_admit_row_text(admit, 10, 'Residency')

    def visible_admit_fresh_trans(self, admit):
        return self.visible_admit_row_text(admit, 11, 'Freshman or Transfer')

    @staticmethod
    def last_updated_msg_loc():
        return By.XPATH, '//div[contains(text(), "Admit data was last updated on")]'
