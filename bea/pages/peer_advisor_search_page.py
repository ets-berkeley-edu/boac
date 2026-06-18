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
import time

from flask import current_app as app
from selenium.webdriver.common.by import By

from bea.pages.peer_advising_note_table import PeerAdvisingNoteTable
from bea.test_utils import utils


class PeerAdvisorSearchPage(PeerAdvisingNoteTable):

    PEER_SEARCH_PAGE_HEADING = By.XPATH, '//h1[text()="Peer Advising Search"]'

    NOTE_RESULTS_BUTTON = By.ID, 'peer-tab-note'
    NOTE_RESULTS_COUNT = By.ID, 'peer-tab-count-note'
    PEER_NOTE_RESULTS_SUMMARY = By.ID, 'peer-tab-note-summary'

    def note_results_count(self):
        return self.element(self.NOTE_RESULTS_COUNT).text

    def note_results_summary(self):
        return self.element(self.PEER_NOTE_RESULTS_SUMMARY).text

    def wait_for_note_search_result_count(self):
        self.wait_for_spinner(timeout=utils.get_medium_timeout())
        count = self.note_results_count()
        app.logger.info(f'Note search results count is {count}')
        return count

    def assert_note_results_present(self):
        count = self.wait_for_note_search_result_count()
        assert str(count) != '0'
        self.wait_for_element_and_click(self.NOTE_RESULTS_BUTTON)
        time.sleep(1)
        if '+' in count:
            assert self.note_results_summary().startswith(f"Showing {count.replace('+', '')} of")
        else:
            noun = 'result' if count == '1' else 'results'
            assert self.note_results_summary().startswith(f'Showing {count} {noun} matching')

    def assert_note_results_not_present(self):
        count = self.wait_for_note_search_result_count()
        assert count == '0'
        self.wait_for_element_and_click(self.NOTE_RESULTS_BUTTON)
        time.sleep(1)
        assert self.note_results_summary().startswith('No results found matching')
