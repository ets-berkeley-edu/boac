"""Generic utilities"""


def get(_dict, key, default_value=None):
    value = _dict and key in _dict and _dict[key]
    return value or default_value
