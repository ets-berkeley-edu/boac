"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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
import re
import string
import time

from autolink import linkify
from flask import current_app as app
import pytz
from titlecase import titlecase


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


def get_benchmarker(label):
    benchmark_start = time.time()

    def _log_benchmark(msg):
        app.logger.debug(f'BENCHMARK {label}: {msg} ({round((time.time() - benchmark_start) * 1000)} ms elapsed)')
    return _log_benchmark


def join_if_present(delimiter, terms):
    return delimiter.join([t for t in terms if t])


def localize_datetime(dt):
    return dt.astimezone(pytz.timezone(app.config['TIMEZONE']))


def localized_timestamp_to_utc(_str):
    naive_datetime = datetime.strptime(_str, '%Y-%m-%dT%H:%M:%S')
    localized_datetime = pytz.timezone(app.config['TIMEZONE']).localize(naive_datetime)
    return localized_datetime.astimezone(pytz.utc)


def process_input_from_rich_text_editor(rich_text):
    parsed = rich_text.strip()
    exclude_from_parse = {}
    now = time.time()
    for index, match in enumerate(re.findall('<a [^>]*>.*?</a>', parsed)):
        placeholder = f'placeholder-{now}-{index}'
        exclude_from_parse[placeholder] = match
        parsed = parsed.replace(match, placeholder, 1)
    parsed = linkify(parsed, {'target': '_blank'})
    for placeholder, match in exclude_from_parse.items():
        parsed = parsed.replace(placeholder, match, 1)
    return parsed


def remove_none_values(_dict):
    return {k: v for k, v in _dict.items() if v is not None}


def titleize(_str):
    def handle_abbreviations(word, **kwargs):
        if app.config['ABBREVIATED_WORDS'] and word.upper().strip(string.punctuation) in app.config['ABBREVIATED_WORDS']:
            return word.upper()
    if not isinstance(_str, str):
        return _str
    return titlecase(_str.upper(), callback=handle_abbreviations)


def tolerant_remove(_list, item):
    """Remove item from list. Return True if item was present, otherwise False."""
    try:
        _list.remove(item)
        return True
    except ValueError:
        return False


def is_int(s):
    try:
        int(s)
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


def unix_timestamp_to_localtime(epoch):
    utc_from_timestamp = datetime.utcfromtimestamp(epoch).replace(tzinfo=pytz.utc)
    return localize_datetime(utc_from_timestamp)


def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def utc_timestamp_to_localtime(_str):
    utc_datetime = pytz.utc.localize(datetime.strptime(_str, '%Y-%m-%dT%H:%M:%SZ'))
    return localize_datetime(utc_datetime)


def vacuum_whitespace(_str):
    """Collapse multiple-whitespace sequences into a single space; remove leading and trailing whitespace."""
    if not _str:
        return None
    return ' '.join(_str.split())
