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

    def test_to_bool_or_none(self):
        """If None is not False in your use case then use this util."""
        assert util.to_bool_or_none(None) is None
        assert util.to_bool_or_none('true') is True
        assert util.to_bool_or_none('false') is False
        assert util.to_bool_or_none('FALSE') is False
        assert util.to_bool_or_none('blargh') is None
