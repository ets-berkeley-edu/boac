from boac.lib import berkeley


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
