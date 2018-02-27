"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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


from datetime import datetime
import inspect

from flask import current_app as app
import pytz


"""Generic utilities."""


def camelize(string):
    def lower_then_capitalize():
        yield str.lower
        while True:
            yield str.capitalize
    string_transform = lower_then_capitalize()
    return ''.join(next(string_transform)(segment) for segment in string.split('_'))


def fill_pattern_from_args(pattern, func, *args, **kw):
    return pattern.format(**get_args_dict(func, *args, **kw))


def get_args_dict(func, *args, **kw):
    arg_names = inspect.getfullargspec(func)[0]
    resp = dict(zip(arg_names, args))
    resp.update(kw)
    return resp


def get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def localize_datetime(dt):
    return dt.astimezone(pytz.timezone(app.config['TIMEZONE']))


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


def utc_timestamp_to_localtime(str):
    utc_datetime = pytz.utc.localize(datetime.strptime(str, '%Y-%m-%dT%H:%M:%SZ'))
    return localize_datetime(utc_datetime)


def vacuum_whitespace(str):
    """Collapse multiple-whitespace sequences into a single space; remove leading and trailing whitespace."""
    if not str:
        return None
    return ' '.join(str.split())


def app_in_demo_mode():
    """Return config value, if found. The default is False."""
    return 'DEMO_MODE' in app.config and app.config['DEMO_MODE']
