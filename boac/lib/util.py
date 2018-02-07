"""Generic utilities."""


def camelize(string):
    def lower_then_capitalize():
        yield str.lower
        while True:
            yield str.capitalize
    string_transform = lower_then_capitalize()
    return ''.join(next(string_transform)(segment) for segment in string.split('_'))


def get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def vacuum_whitespace(str):
    """Collapse multiple-whitespace sequences into a single space; remove leading and trailing whitespace."""
    if not str:
        return None
    return ' '.join(str.split())


def tolerant_remove(_list, item):
    """Remove item from list. Return True if item was present, otherwise False."""
    try:
        _list.remove(item)
        return True
    except ValueError:
        return False


def to_bool_or_none(arg):
    """
    With the idea of "no decision is a decision" in mind, this util has three possible outcomes: True, False and None.

    If arg is type string then intuitively handle 'true'/'false' values, else return None.
    If arg is NOT type string and NOT None then rely on Python's bool().
    """
    s = arg
    if isinstance(arg, str):
        s = arg.strip().lower()
        s = True if s == 'true' else s
        s = False if s == 'false' else s
        s = None if s not in [True, False] else s
    return None if s is None else bool(s)
