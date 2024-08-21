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

from bea.config.bea_test_config import BEATestConfig
from bea.models.cohorts_and_groups.filtered_cohort import FilteredCohort
from bea.test_utils import boa_utils
from bea.test_utils import nessie_filter_admits_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
from flask import current_app as app
import pytest

test = BEATestConfig()
test.filtered_admits()
test.searches.sort(key=lambda c: len(c.members))

pre_existing_cohorts = boa_utils.get_user_filtered_cohorts(test.advisor, admits=True)
latest_update_date = nessie_utils.get_admit_data_update_date()


@pytest.mark.usefixtures('page_objects')
class TestFilteredAdmits:

    all_admits_cohort = FilteredCohort({
        'cohort_id': '0',
        'members': test.admits,
        'name': 'CE3 Admissions',
        'search_criteria': {},
    })

    def test_no_existing_cohorts(self):
        self.homepage.dev_auth(test.advisor)
        for c in pre_existing_cohorts:
            self.filtered_admits_page.load_cohort(c)
            self.filtered_admits_page.delete_cohort(c)

    def test_default_cohort(self):
        self.filtered_admits_page.cancel_cohort_if_modal()
        self.homepage.load_page()
        self.homepage.click_sidebar_all_admits()

    def test_stale_data_msg(self):
        is_stale = self.filtered_admits_page.is_present(self.filtered_admits_page.data_update_date_heading(latest_update_date))
        if datetime.datetime.strptime(latest_update_date, '%b %d, %Y').date() == datetime.date.today():
            assert not is_stale
        else:
            assert is_stale

    def test_ferpa_msg(self):
        self.filtered_admits_page.click_export_list()
        title = 'FERPA (Privacy Disclosure) - Office of the Registrar'
        assert self.filtered_admits_page.is_external_link_valid(self.filtered_admits_page.FERPA_WARNING_LINK, title)

    def test_export_all_admits(self):
        self.filtered_admits_page.click_export_ferpa_cancel()
        all_admits_csv = self.filtered_admits_page.export_admit_list(self.all_admits_cohort)
        self.filtered_admits_page.verify_admits_present_in_export(self.all_admits_cohort, all_admits_csv)

    def test_no_emails_in_export(self):
        all_admits_csv = self.filtered_admits_page.export_admit_list(self.all_admits_cohort)
        self.filtered_admits_page.verify_no_email_in_export(all_admits_csv)

    def test_required_fields_in_export(self):
        all_admits_csv = self.filtered_admits_page.export_admit_list(self.all_admits_cohort)
        self.filtered_admits_page.verify_mandatory_data_in_export(all_admits_csv)

    def test_optional_fields_in_export(self):
        all_admits_csv = self.filtered_admits_page.export_admit_list(self.all_admits_cohort)
        self.filtered_admits_page.verify_optional_data_in_export(all_admits_csv)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('cohort', test.searches, scope='class',
                         ids=[f'{vars(cohort.search_criteria)}' for cohort in test.searches])
class TestFilteredAdmitResults:

    def test_cohort_search_results_default_by_last_name(self, cohort):
        idx = test.searches.index(cohort)
        app.logger.info(f'Testing cohort {idx} with criteria {vars(cohort.search_criteria)}')
        self.filtered_admits_page.cancel_cohort_if_modal()
        self.homepage.load_page()

        # Follow both paths to create admit cohorts
        if idx % 2 == 0:
            self.filtered_admits_page.click_sidebar_create_ce3_filtered()
        else:
            self.homepage.click_sidebar_all_admits()
            self.filtered_admits_page.click_create_cohort()

        self.filtered_admits_page.perform_admit_search(cohort)
        expected = nessie_filter_admits_utils.cohort_by_last_name(test, cohort.search_criteria)
        if cohort.members:
            visible = self.filtered_admits_page.list_view_admit_sids(cohort)
            utils.assert_equivalence(visible, expected)
            self.filtered_admits_page.verify_list_view_sorting(expected, visible)
        else:
            utils.assert_equivalence(self.filtered_admits_page.results_count(), 0)

    def test_cohort_search_results_visible_admit_data(self, cohort):
        failures = []
        visible_sids = self.filtered_admits_page.admit_cohort_row_sids()
        members_to_check = [member for member in cohort.members if member.sid in visible_sids]
        for admit in members_to_check:
            self.filtered_admits_page.verify_admit_row_data(admit, failures)
        if failures:
            app.logger.info(f'Failures: {failures}')
        assert not failures

    def test_cohort_search_export_button(self, cohort):
        assert self.filtered_admits_page.is_present(self.filtered_admits_page.EXPORT_LIST_BUTTON)

    def test_cohort_search_create_new_cohort(self, cohort):
        self.filtered_admits_page.create_new_cohort(cohort)

    def test_cohort_show_filters(self, cohort):
        self.filtered_admits_page.verify_admit_filters_present(cohort)

    def test_cohort_sidebar_member_count(self, cohort):
        self.filtered_admits_page.wait_for_sidebar_member_count(cohort)

    def test_cohort_no_history(self, cohort):
        assert not self.filtered_admits_page.is_present(self.filtered_admits_page.HISTORY_BUTTON)


@pytest.mark.usefixtures('page_objects')
class FilteredAdmitSorting:

    def test_cohort_sort_first_name(self):
        cohort = test.searches[-1]
        self.filtered_admits_page.load_cohort(cohort)
        self.filtered_admits_page.sort_by_first_name()
        expected = nessie_filter_admits_utils.cohort_by_first_name(test, cohort.search_criteria)
        visible = self.filtered_admits_page.list_view_admit_sids(cohort)
        utils.assert_equivalence(visible, expected)

    def test_cohort_sort_cs_id(self):
        cohort = test.searches[-1]
        self.filtered_admits_page.sort_by('cs_empl_id')
        expected = nessie_filter_admits_utils.cohort_by_cs_empl_id(test, cohort.search_criteria)
        visible = self.filtered_admits_page.list_view_admit_sids(cohort)
        utils.assert_equivalence(visible, expected)

    def test_link_to_admit_page(self):
        sid = self.filtered_admits_page.admit_cohort_row_sids[0]
        self.filtered_admits_page.click_admit_link(sid)
        self.admit_page.when_present(self.admit_page.SID, utils.get_short_timeout())
        assert self.admit_page.element(self.admit_page.SID).text == sid
