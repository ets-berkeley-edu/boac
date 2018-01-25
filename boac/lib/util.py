"""Generic utilities."""


def camelize(string):
    def lower_then_capitalize():
        yield str.lower
        while True:
            yield str.capitalize
    string_transform = lower_then_capitalize()
    return ''.join(next(string_transform)(segment) for segment in string.split('_'))


def get(_dict, key, default_value=None):
    value = _dict and key in _dict and _dict[key]
    return value or default_value


def get_distinct_with_order(sequence):
    """Remove duplicates from list whilst preserving order (see https://www.peterbe.com/plog/uniqifiers-benchmark)."""
    seen = set()
    seen_add = seen.add
    return [x for x in sequence if not (x in seen or seen_add(x))]


def vacuum_whitespace(str):
    """Collapse multiple-whitespace sequences into a single space; remove leading and trailing whitespace."""
    if not str:
        return None
    return ' '.join(str.split())
