"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, BERKELEY_DEPT_NAME_TO_CODE


class TestBerkeleySisTermIdForName:
    """Term name to SIS id translation."""

    def test_sis_term_id_for_name(self):
        """Handles well-formed term names."""
        assert berkeley.sis_term_id_for_name('Spring 2015') == '2152'
        assert berkeley.sis_term_id_for_name('Summer 2016') == '2165'
        assert berkeley.sis_term_id_for_name('Fall 2017') == '2178'
        assert berkeley.sis_term_id_for_name('Fall 1997') == '1978'

    def test_term_name_for_sis_id(self):
        assert berkeley.term_name_for_sis_id('2178') == 'Fall 2017'
        assert berkeley.term_name_for_sis_id('1978') == 'Fall 1997'

    def test_unparseable_term_name(self):
        """Returns None for unparseable term names."""
        assert berkeley.sis_term_id_for_name('Winter 2061') is None
        assert berkeley.sis_term_id_for_name('Default Term') is None

    def test_missing_term_name(self):
        """Returns None for missing term names."""
        assert berkeley.sis_term_id_for_name(None) is None

    def test_term_ids_range(self, app):
        assert berkeley.term_ids_range('2158', '2208') == [
            '2158', '2162', '2165', '2168', '2172', '2175', '2178', '2182', '2185', '2188', '2192', '2195', '2198', '2202', '2205', '2208',
        ]


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


class TestBerkeleyDepartmentCodes:
    """Department codes map to department names."""

    def test_unique_department_names(self):
        """We must have unique dept codes and unique names."""
        assert len(BERKELEY_DEPT_CODE_TO_NAME) == len(BERKELEY_DEPT_NAME_TO_CODE)


class TestAcademicYearForTermName:
    """Matches a term name to its academic year."""

    def test_academic_year_for_term_name(self):
        assert berkeley.academic_year_for_term_name('Fall 1990') == '1991'
        assert berkeley.academic_year_for_term_name('Winter 1971') is None
        assert berkeley.academic_year_for_term_name('Spring 2025') == '2025'
        assert berkeley.academic_year_for_term_name('Summer 2007') == '2007'
        assert berkeley.academic_year_for_term_name('') is None
        assert berkeley.academic_year_for_term_name('Septober 2007') is None
        assert berkeley.academic_year_for_term_name('Fall2007') is None
