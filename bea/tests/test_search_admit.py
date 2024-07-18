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
from bea.models.department import Department
from bea.test_utils import boa_utils
from bea.test_utils import nessie_utils
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.search_admits()
for ad in test.test_admits:
    nessie_utils.get_admit_data(ad)
auth_users = boa_utils.get_authorized_users()
auth_users = [user for user in auth_users if user.active and not user.is_blocked]
last_update_date = nessie_utils.get_admit_data_update_date()


@pytest.mark.usefixtures('page_objects')
class TestSearchAdmitPerms:

    def test_non_ce3_advisor_cannot_search_admits(self):
        non_ce3_advisor = next(filter(lambda u: Department.ZCEEE not in u.depts and not u.is_admin, auth_users))
        self.homepage.load_page()
        self.homepage.dev_auth(non_ce3_advisor)
        self.homepage.open_adv_search()
        assert not self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)

    def test_admin_can_search_admits(self):
        admin = next(filter(lambda u: Department.ZCEEE not in u.depts and u.is_admin, auth_users))
        self.homepage.click_adv_search_cxl_button()
        self.homepage.log_out()
        self.homepage.dev_auth(admin)
        self.homepage.open_adv_search()
        assert self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)

    def test_ce3_advisor_can_search_admits(self):
        self.homepage.click_adv_search_cxl_button()
        self.homepage.log_out()
        self.homepage.dev_auth(test.advisor)
        self.homepage.open_adv_search()
        assert self.homepage.is_present(self.homepage.INCLUDE_ADMITS_CBX)

    def test_exclude_admits_from_search(self):
        self.homepage.exclude_admits()
        self.homepage.enter_adv_search_and_hit_enter(test.test_admits[0].sid)
        self.homepage.wait_for_spinner()
        assert not self.search_results_page.is_present(self.search_results_page.ADMIT_RESULTS_BUTTON)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize('admit', test.test_admits, ids=[admit.sid for admit in test.test_admits], scope='class')
class TestSearchAdmitSearches:

    def test_search_admit_complete_first_name(self, admit):
        self.homepage.load_page()
        self.homepage.open_adv_search()
        self.homepage.include_admits()
        self.homepage.enter_adv_search_and_hit_enter(admit.first_name)
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_partial_first_name(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(admit.first_name[0:2])
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_complete_last_name(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(admit.last_name)
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_partial_last_name(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(admit.last_name[0:2])
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_complete_first_and_last_names(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(f'{admit.first_name} {admit.last_name}')
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_complete_last_and_first_names(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(f'{admit.last_name} {admit.first_name}')
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_partial_first_and_last_names(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(f'{admit.first_name[0:2]} {admit.last_name[0:2]}')
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_partial_last_and_first_names(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(f'{admit.last_name[0:2]} {admit.first_name[0:2]}')
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_partial_sid(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(admit.sid[0:4])
        assert self.search_results_page.is_admit_in_search_result(admit)

    def test_search_admit_complete_sid(self, admit):
        self.search_results_page.open_adv_search()
        self.search_results_page.enter_adv_search_and_hit_enter(admit.sid)
        assert self.search_results_page.is_admit_in_search_result(admit)

    # VISIBLE ADMIT DATA

    def test_visible_admit_last_name(self, admit):
        assert admit.last_name in self.search_results_page.visible_admit_name(admit)

    def test_visible_admit_sid(self, admit):
        assert self.search_results_page.visible_admit_sid(admit) == admit.sid

    def test_visible_admit_cep(self, admit):
        cep = admit.admit_data['special_program_cep'] or '—'
        assert self.search_results_page.visible_admit_cep(admit) == cep

    def test_visible_admit_re_entry_status(self, admit):
        assert self.search_results_page.visible_admit_re_entry(admit) == admit.admit_data['reentry_status']

    def test_visible_admit_1st_gen_college(self, admit):
        assert self.search_results_page.visible_admit_1st_gen_college(admit) == admit.admit_data['first_generation_college']

    def test_visible_admit_urem(self, admit):
        assert self.search_results_page.visible_admit_urem(admit) == admit.admit_data['urem']

    def test_visible_fee_waiver(self, admit):
        # The element locator has to strip 'Waiver' out of the text. Sad!
        data = admit.admit_data['application_fee_waiver_flag']
        expected = 'Fee' if data == 'FeeWaiver' else data
        assert self.search_results_page.visible_admit_fee_waiver(admit) == expected

    def test_visible_freshman_or_transfer(self, admit):
        assert self.search_results_page.visible_admit_residency(admit) == admit.admit_data['residency_category']

    def test_visible_residency(self, admit):
        assert self.search_results_page.visible_admit_fresh_trans(admit) == admit.admit_data['freshman_or_transfer']

    def test_latest_update_date(self, admit):
        if admit.admit_data['updated_at'].date() == datetime.date.today():
            assert not self.search_results_page.is_present(self.search_results_page.last_updated_msg_loc())
        else:
            assert self.search_results_page.is_present(self.search_results_page.last_updated_msg_loc())

    def test_admit_page_link(self, admit):
        self.search_results_page.click_admit_result(admit)
        self.admit_page.when_present(self.admit_page.NAME, utils.get_short_timeout())

    # TODO def test_admit_page_back_to_results_button(self, admit):
