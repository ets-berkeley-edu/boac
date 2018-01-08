import boac.lib.util as util


class TestUtil:
    """Generic utilities"""

    def test_vacuum_whitespace(self):
        """cleans up leading, trailing, and repeated whitespace"""
        assert util.vacuum_whitespace('  Firstname    Lastname   ') == 'Firstname Lastname'
