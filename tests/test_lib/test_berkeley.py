import boac.lib.berkeley as berkeley


class TestBerkeleySisTermIdForName:
    """Term name to SIS id translation"""

    def test_sis_term_id_for_name(self):
        """handles well-formed term names"""
        assert berkeley.sis_term_id_for_name('Spring 2015') == '2152'
        assert berkeley.sis_term_id_for_name('Summer 2016') == '2165'
        assert berkeley.sis_term_id_for_name('Fall 2017') == '2178'

    def test_unparseable_term_name(self):
        """returns None for unparseable term names"""
        assert berkeley.sis_term_id_for_name('Winter 2061') is None
        assert berkeley.sis_term_id_for_name('Default Term') is None

    def test_missing_term_name(self):
        """returns None for missing term names"""
        assert berkeley.sis_term_id_for_name(None) is None
