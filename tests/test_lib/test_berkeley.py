"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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


from boac.lib import berkeley
from boac.models.authorized_user import AuthorizedUser
from boac.models.cohort_filter import CohortFilter
import pytest


class TestBerkeleySisTermIdForName:
    """Term name to SIS id translation."""

    def test_sis_term_id_for_name(self):
        """Handles well-formed term names."""
        assert berkeley.sis_term_id_for_name('Spring 2015') == '2152'
        assert berkeley.sis_term_id_for_name('Summer 2016') == '2165'
        assert berkeley.sis_term_id_for_name('Fall 2017') == '2178'

    def test_unparseable_term_name(self):
        """Returns None for unparseable term names."""
        assert berkeley.sis_term_id_for_name('Winter 2061') is None
        assert berkeley.sis_term_id_for_name('Default Term') is None

    def test_missing_term_name(self):
        """Returns None for missing term names."""
        assert berkeley.sis_term_id_for_name(None) is None

    def test_all_term_ids(self, app):
        assert berkeley.all_term_ids() == ['2178', '2175', '2172', '2168']


class TestBerkeleyDegreeProgramUrl:

    def test_major_with_known_link(self):
        assert berkeley.degree_program_url_for_major('English BA') == \
            'http://guide.berkeley.edu/undergraduate/degree-programs/english/'
        assert berkeley.degree_program_url_for_major('Peace & Conflict Studies BA') == \
            'http://guide.berkeley.edu/undergraduate/degree-programs/peace-conflict-studies/'
        assert berkeley.degree_program_url_for_major('History BA') == \
            'http://guide.berkeley.edu/undergraduate/degree-programs/history/'
        assert berkeley.degree_program_url_for_major('History of Art BA') == \
            'http://guide.berkeley.edu/undergraduate/degree-programs/art-history/'

    def test_major_without_a_link(self):
        assert berkeley.degree_program_url_for_major('English for Billiards Players MS') is None
        assert berkeley.degree_program_url_for_major('Altaic Language BA') is None
        assert berkeley.degree_program_url_for_major('Entomology BS') is None


class TestBerkeleyAuthorization:

    @pytest.fixture()
    def admin_user(self):
        return AuthorizedUser.find_by_uid('2040')

    @pytest.fixture()
    def asc_advisor(self):
        return AuthorizedUser.find_by_uid('1081940')

    @pytest.fixture()
    def coe_advisor(self):
        return AuthorizedUser.find_by_uid('1133399')

    @pytest.fixture()
    def unauthorized_user(self):
        return AuthorizedUser.find_by_uid('1015674')

    def test_not_authorized_to_use_boac(self, unauthorized_user):
        assert not berkeley.is_authorized_to_use_boac(unauthorized_user)

    def test_admin_authorized_to_use_boac(self, admin_user):
        assert berkeley.is_authorized_to_use_boac(admin_user)

    def test_is_authorized_to_use_boac(self, asc_advisor):
        assert berkeley.is_authorized_to_use_boac(asc_advisor)

    def test_zero_dept_codes(self, admin_user, unauthorized_user):
        assert berkeley.get_dept_codes(None) is None
        assert berkeley.get_dept_codes(admin_user) == []
        assert not berkeley.get_dept_codes(unauthorized_user)

    def test_asc_dept_codes(self, asc_advisor, coe_advisor):
        assert berkeley.get_dept_codes(asc_advisor) == ['UWASC']
        assert berkeley.get_dept_codes(coe_advisor) == ['COENG']

    def test_can_view_cohort(self, admin_user, asc_advisor, coe_advisor):
        coe_cohorts = CohortFilter.all_owned_by('1133399')
        assert len(coe_cohorts)
        assert berkeley.can_view_cohort(admin_user, coe_cohorts[0])
        assert not berkeley.can_view_cohort(asc_advisor, coe_cohorts[0])
        assert berkeley.can_view_cohort(coe_advisor, coe_cohorts[0])


class TestAlertRules:
    """Rules related to alert creation."""

    def test_section_is_eligible_for_alerts(self):
        assert berkeley.section_is_eligible_for_alerts({'displayName': 'SOCIOL 198'}, {'component': 'LEC'})
        dis_section = {'component': 'DIS'}
        for catalog_id in ('98', '199', '98A', '98BC', '199BC'):
            assert not berkeley.section_is_eligible_for_alerts({'displayName': f'SOCIOL {catalog_id}'}, dis_section)
        for display_name in ('PSYCH 19A', 'MATH 9A', 'SOCIOL 198, Special Edition', 'Pop Music in 1988'):
            eligible_for_alert = {'displayName': display_name}
            assert berkeley.section_is_eligible_for_alerts(eligible_for_alert, dis_section), f'Failed on {display_name}'
