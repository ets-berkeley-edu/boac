from boac.lib import util


class TestUtil:
    """Generic utilities."""

    def test_vacuum_whitespace(self):
        """Cleans up leading, trailing, and repeated whitespace."""
        assert util.vacuum_whitespace('  Firstname    Lastname   ') == 'Firstname Lastname'

    def test_tolerant_remove(self):
        """Ignores error if item not found in list."""
        assert not util.tolerant_remove([], 'foo')
        a = ['foo', 'bar', 'baz']
        assert util.tolerant_remove(a, 'bar') is True
        assert a == ['foo', 'baz']
