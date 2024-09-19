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
import re

from bea.config.bea_test_config import BEATestConfig
from bea.test_utils import nessie_utils
from bea.test_utils import utils
import pytest

test = BEATestConfig()
test.sis_admit_data()

latest_update_date = nessie_utils.get_admit_data_update_date()
all_student_sids = nessie_utils.get_all_student_sids()


@pytest.mark.usefixtures('page_objects')
class TestAdmitLogIn:

    def test_log_in(self):
        self.homepage.load_page()
        self.homepage.dev_auth(test.advisor)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=test.test_cases,
                         ids=[tc.test_case_id for tc in test.test_cases],
                         scope='class')
class TestAdmitPage:

    def test_load_admit_page(self, tc):
        self.admit_page.load_page(tc.student.sid)

    def test_update_date(self, tc):
        is_stale = self.admit_page.is_present(self.admit_page.data_update_date_heading(latest_update_date))
        if datetime.datetime.strptime(latest_update_date, '%b %d, %Y').date() == datetime.date.today():
            assert not is_stale
        else:
            assert is_stale

    def test_name(self, tc):
        utils.assert_equivalence(self.admit_page.name(), self.admit_page.concatenated_name(tc.student))

    def test_applicant_id(self, tc):
        utils.assert_equivalence(self.admit_page.uc_cpid(), tc.student.admit_data['applyuc_cpid'])

    def test_cs_empl_id(self, tc):
        utils.assert_equivalence(self.admit_page.sid(), tc.student.sid)

    def test_birth_date(self, tc):
        data_date = datetime.datetime.strptime(tc.student.admit_data['birthdate'], '%Y-%m-%d')
        utils.assert_equivalence(self.admit_page.birth_date(), data_date.strftime('%b %-d, %Y'))

    def test_freshman_or_transfer(self, tc):
        utils.assert_equivalence(self.admit_page.fresh_trans(), tc.student.admit_data['freshman_or_transfer'])

    def test_status(self, tc):
        utils.assert_equivalence(self.admit_page.status(), tc.student.admit_data['admit_status'])

    def test_sir(self, tc):
        utils.assert_equivalence(self.admit_page.sir(), tc.student.admit_data['current_sir'])

    def test_college(self, tc):
        utils.assert_equivalence(self.admit_page.college(), tc.student.admit_data['college'])

    def test_admission_term(self, tc):
        utils.assert_equivalence(self.admit_page.admit_term(), tc.student.admit_data['admit_term'])

    def test_email(self, tc):
        utils.assert_equivalence(self.admit_page.email(), tc.student.admit_data['email'])

    def test_campus_email(self, tc):
        email = tc.student.admit_data['campus_email_1'] or '—'
        utils.assert_equivalence(self.admit_page.campus_email(), email)

    def test_daytime_phone(self, tc):
        phone = tc.student.admit_data['daytime_phone'] or '—'
        utils.assert_equivalence(self.admit_page.daytime_phone(), phone)

    def test_mobile_phone(self, tc):
        phone = tc.student.admit_data['mobile'] or '—'
        utils.assert_equivalence(self.admit_page.mobile_phone(), phone)

    def test_address_1(self, tc):
        utils.assert_equivalence(self.admit_page.address_street_1(),
                                 re.sub('\s+', ' ', tc.student.admit_data['permanent_street_1']))

    def test_address_2(self, tc):
        utils.assert_equivalence(self.admit_page.address_street_2(),
                                 re.sub('\s+', ' ', tc.student.admit_data['permanent_street_2']))

    def test_address_city_region_postal(self, tc):
        city = tc.student.admit_data['permanent_city']
        region = f" {tc.student.admit_data['permanent_region']}" if tc.student.admit_data['permanent_region'] else ''
        post_code = tc.student.admit_data['permanent_postal']
        expected = re.sub('\s+', ' ', f'{city},{region} {post_code}')
        utils.assert_equivalence(self.admit_page.address_city_region_postal(), expected)

    def test_address_county(self, tc):
        utils.assert_equivalence(self.admit_page.address_country(), tc.student.admit_data['permanent_country'])

    def test_x_ethnic(self, tc):
        utils.assert_equivalence(self.admit_page.x_ethnic(), tc.student.admit_data['xethnic'])

    def test_hispanic(self, tc):
        hispanic = tc.student.admit_data['hispanic'] or '—'
        utils.assert_equivalence(self.admit_page.hispanic(), hispanic)

    def test_urem(self, tc):
        utils.assert_equivalence(self.admit_page.urem(), tc.student.admit_data['urem'])

    def test_residency(self, tc):
        utils.assert_equivalence(self.admit_page.residency_category(), tc.student.admit_data['residency_category'])

    def test_citizen(self, tc):
        utils.assert_equivalence(self.admit_page.citizen_status(), tc.student.admit_data['us_citizenship_status'])

    def test_non_citizen(self, tc):
        status = tc.student.admit_data['us_non_citizen_status'] or '—'
        utils.assert_equivalence(self.admit_page.non_citizen_status(), status)

    def test_citizenship(self, tc):
        utils.assert_equivalence(self.admit_page.citizenship(), tc.student.admit_data['citizenship_country'])

    def test_residence_country(self, tc):
        country = tc.student.admit_data['permanent_residence_country'] or '—'
        utils.assert_equivalence(self.admit_page.residence_country(), country)

    def test_visa_status(self, tc):
        status = tc.student.admit_data['non_immigrant_visa_current'] or '—'
        utils.assert_equivalence(self.admit_page.visa_status(), status)

    def test_visa_planned(self, tc):
        planned = tc.student.admit_data['non_immigrant_visa_planned'] or '—'
        utils.assert_equivalence(self.admit_page.visa_planned(), planned)

    def test_first_gen_college(self, tc):
        utils.assert_equivalence(self.admit_page.first_gen_college(), tc.student.admit_data['first_generation_college'])

    def test_parent_1_educ(self, tc):
        utils.assert_equivalence(self.admit_page.parent_1_educ(), tc.student.admit_data['parent_1_education_level'])

    def test_parent_2_educ(self, tc):
        utils.assert_equivalence(self.admit_page.parent_2_educ(), tc.student.admit_data['parent_2_education_level'])

    def test_parent_highest_educ(self, tc):
        utils.assert_equivalence(self.admit_page.parent_highest_educ(), tc.student.admit_data['highest_parent_education_level'])

    def test_gpa_hs_unweighted(self, tc):
        gpa = tc.student.admit_data['hs_unweighted_gpa'] or '—'
        utils.assert_equivalence(self.admit_page.gpa_hs_unweighted(), gpa)

    def test_gpa_hs_weighted(self, tc):
        gpa = tc.student.admit_data['hs_weighted_gpa'] or '—'
        utils.assert_equivalence(self.admit_page.gpa_hs_weighted(), gpa)

    def test_gpa_transfer(self, tc):
        gpa = tc.student.admit_data['transfer_gpa'] or '—'
        utils.assert_equivalence(self.admit_page.gpa_transfer(), gpa)

    def test_fee_waiver(self, tc):
        flag = tc.student.admit_data['application_fee_waiver_flag'] or '—'
        utils.assert_equivalence(self.admit_page.fee_waiver(), flag)

    def test_foster_care(self, tc):
        foster_care = tc.student.admit_data['foster_care_flag'] or '—'
        utils.assert_equivalence(self.admit_page.foster_care(), foster_care)

    def test_family_single_parent(self, tc):
        single_parent = tc.student.admit_data['family_is_single_parent'] or '—'
        utils.assert_equivalence(self.admit_page.family_single_parent(), single_parent)

    def test_student_single_parent(self, tc):
        single_parent = tc.student.admit_data['student_is_single_parent'] or '—'
        utils.assert_equivalence(self.admit_page.student_single_parent(), single_parent)

    def test_family_dependents(self, tc):
        deps = tc.student.admit_data['family_dependents_num'] or '—'
        utils.assert_equivalence(self.admit_page.family_dependents(), deps)

    def test_student_dependents(self, tc):
        deps = tc.student.admit_data['student_dependents_num'] or '—'
        utils.assert_equivalence(self.admit_page.student_dependents(), deps)

    def test_family_income(self, tc):
        income = int(tc.student.admit_data['family_income']) if tc.student.admit_data['family_income'] else '—'
        utils.assert_equivalence(self.admit_page.family_income(), income)

    def test_student_income(self, tc):
        income = int(tc.student.admit_data['student_income']) if tc.student.admit_data['student_income'] else '—'
        utils.assert_equivalence(self.admit_page.student_income(), income)

    def test_military_dependent(self, tc):
        deps = tc.student.admit_data['is_military_dependent'] or '—'
        utils.assert_equivalence(self.admit_page.military_dependent(), deps)

    def test_military_status(self, tc):
        status = tc.student.admit_data['military_status'] or '—'
        utils.assert_equivalence(self.admit_page.military_status(), status)

    def test_re_entry_status(self, tc):
        status = tc.student.admit_data['reentry_status'] or '—'
        utils.assert_equivalence(self.admit_page.re_entry_status(), status)

    def test_athlete_status(self, tc):
        status = tc.student.admit_data['athlete_status'] or '—'
        utils.assert_equivalence(self.admit_page.athlete_status(), status)

    def test_summer_bridge_status(self, tc):
        status = tc.student.admit_data['summer_bridge_status'] or '—'
        utils.assert_equivalence(self.admit_page.summer_bridge_status(), status)

    def test_last_school_lcff_plus(self, tc):
        lcff = tc.student.admit_data['last_school_lcff_plus_flag'] or '—'
        utils.assert_equivalence(self.admit_page.last_school_lcff_plus(), lcff)

    def test_special_program_cep(self, tc):
        cep = tc.student.admit_data['special_program_cep'] or '—'
        utils.assert_equivalence(self.admit_page.special_program_cep(), cep)

    def test_student_page_link(self, tc):
        link_present = self.admit_page.is_present(self.admit_page.student_page_link_loc())
        if tc.student.sid in all_student_sids:
            assert link_present
            self.admit_page.click_student_page_link(tc.student)
            self.student_page.expand_personal_details()
        else:
            assert not link_present
