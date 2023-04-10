"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from html.parser import HTMLParser
import inspect
import re
import string
import time

from autolink import linkify
from boac.externals import s3
from flask import current_app as app
from nltk.stem.snowball import SnowballStemmer
import pytz
from titlecase import titlecase


"""Generic utilities."""

TEXT_SEARCH_PATTERN = r'(\w*[.:/-@]\w+([.:/-]\w+)*)|[^\s?!(),;:.`]+'


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


def localized_timestamp_to_utc(_str, date_format='%Y-%m-%dT%H:%M:%S'):
    naive_datetime = datetime.strptime(_str, date_format)
    localized_datetime = pytz.timezone(app.config['TIMEZONE']).localize(naive_datetime)
    return localized_datetime.astimezone(pytz.utc)


def process_input_from_rich_text_editor(rich_text):
    parsed = rich_text and rich_text.strip()
    if parsed:
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
    else:
        return None


def remove_none_values(_dict):
    return {k: v for k, v in _dict.items() if v is not None}


def safe_strftime(date, date_format):
    return datetime.strftime(date, date_format) if date else None


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


def is_float(s):
    try:
        float(s)
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


def to_float_or_none(s):
    try:
        return None if s is None else float(s)
    except ValueError:
        return None


def to_int_or_none(s):
    if s is None:
        return None
    try:
        return int(s)
    except ValueError:
        return None


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


def put_attachment_to_s3(name, byte_stream):
    bucket = app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET']
    base_path = app.config['DATA_LOCH_S3_BOA_NOTE_ATTACHMENTS_PATH']
    key_suffix = _localize_datetime(datetime.now()).strftime(f'%Y/%m/%d/%Y%m%d_%H%M%S_{name}')
    key = f'{base_path}/{key_suffix}'
    s3.put_binary_data_to_s3(
        bucket=bucket,
        key=key,
        binary_data=byte_stream,
    )
    return key


def get_attachment_filename(attachment_id, path_to_attachment):
    raw_filename = path_to_attachment.rsplit('/', 1)[-1]
    match = re.match(r'\A\d{8}_\d{6}_(.+)\Z', raw_filename)
    if match:
        return match[1]
    else:
        app.logger.warn(
            f'Note attachment S3 filename did not match expected format: ID = {attachment_id}, filename = {raw_filename}')
        return raw_filename


def note_attachment_to_api_json(attachment):
    filename = get_attachment_filename(attachment.id, attachment.path_to_attachment)
    api_json = {
        'id': attachment.id,
        'displayName': filename,
        'filename': filename,
        'uploadedBy': attachment.uploaded_by_uid,
    }
    if hasattr(attachment, 'note_id'):
        api_json['noteId'] = attachment.note_id
    if hasattr(attachment, 'note_draft_id'):
        api_json['noteDraftId'] = attachment.note_draft_id
    elif hasattr(attachment, 'note_template_id'):
        api_json['noteTemplateId'] = attachment.note_template_id
    return api_json


class HTMLTagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    def reset(self):
        super().reset()
        self.fed = []


tag_stripper = HTMLTagStripper()
stemmer = SnowballStemmer('english')


def search_result_text_snippet(text, search_terms, search_pattern):
    tag_stripper.feed(text)
    tag_stripped_body = tag_stripper.get_data()
    tag_stripper.reset()

    snippet_padding = app.config['NOTES_SEARCH_RESULT_SNIPPET_PADDING']
    words = list(re.finditer(search_pattern, tag_stripped_body))
    stemmed_search_terms = [stemmer.stem(term) for term in search_terms]

    snippet = None
    match_index = None
    start_position = 0

    for index, word_match in enumerate(words):
        stem = stemmer.stem(word_match.group(0))
        if match_index is None and stem in stemmed_search_terms:
            match_index = index
            if index > snippet_padding:
                start_position = words[index - snippet_padding].start(0)
            snippet = '...' if start_position > 0 else ''
        if match_index is not None:
            snippet += tag_stripped_body[start_position:word_match.start(0)]
            if stem in stemmed_search_terms:
                snippet += '<strong>'
            snippet += word_match.group(0)
            if stem in stemmed_search_terms:
                snippet += '</strong>'
            if index == len(words) - 1:
                snippet += tag_stripped_body[word_match.end(0):len(tag_stripped_body)]
                break
            elif index == match_index + snippet_padding:
                end_position = words[index].end(0)
                snippet += tag_stripped_body[word_match.end(0):end_position]
                snippet += '...'
                break
            else:
                start_position = word_match.end(0)

    if snippet:
        return snippet
    else:
        if len(words) > snippet_padding:
            end_position = words[snippet_padding].end(0)
            return tag_stripped_body[0:end_position] + '...'
        else:
            return tag_stripped_body


def _localize_datetime(dt):
    return dt.astimezone(pytz.timezone(app.config['TIMEZONE']))
