"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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

import html
import inspect
import re
import string
import time
import unicodedata
from datetime import UTC, datetime
from html.parser import HTMLParser

import pytz
from autolink import linkify
from dateutil.tz import tzutc
from flask import current_app as app
from nltk.stem.snowball import SnowballStemmer
from titlecase import titlecase

from boac.externals import s3

"""Generic utilities."""

DASHES = re.compile('[\u2013\u2014\-—]')
TEXT_SEARCH_PATTERN = r'[0-9A-Za-z/\-]+'


def camelize(text):
    def lower_then_capitalize():
        yield str.lower
        while True:
            yield str.capitalize
    string_transform = lower_then_capitalize()
    return ''.join(next(string_transform)(segment) for segment in text.split('_'))


def capitalize_all_words(text):
    return ' '.join([word.capitalize() for word in text.split()])


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
    return delimiter.join([t for t in terms if t and len(t)])


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


def remove_none_values(_dict):
    return {k: v for k, v in _dict.items() if v is not None}


def safe_strftime(date, date_format):
    return datetime.strftime(date, date_format) if date else None


def split_per_camel_case(camel_cased_string, separator='_'):
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub(separator, camel_cased_string).lower()


def titleize(_str):
    def handle_abbreviations(word, **kwargs):
        if app.config['ABBREVIATED_WORDS'] and word.upper().strip(string.punctuation) in app.config['ABBREVIATED_WORDS']:
            return word.upper()
    if not isinstance(_str, str):
        return _str
    return titlecase(_str.upper(), callback=handle_abbreviations)


def to_iso_format(value):
    return value and value.astimezone(tzutc()).isoformat()


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
    return datetime.now(UTC).replace(tzinfo=pytz.utc)


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
        app.logger.warning(
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
    elif hasattr(attachment, 'note_template_id'):
        api_json['noteTemplateId'] = attachment.note_template_id
    return api_json


class HTMLTagStripper(HTMLParser):
    # Tags whose content should be dropped, not just the tags themselves
    SKIP_CONTENT_TAGS = {'script', 'style', 'iframe', 'object', 'embed', 'noscript', 'template'}

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True

    def handle_starttag(self, tag, attrs):  # noqa: ARG002
        if tag in self.SKIP_CONTENT_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_CONTENT_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, d):
        if len(d) and not self._skip_depth:
            self.fed.append(d)

    def get_data(self):
        return ' '.join(self.fed)

    def reset(self):
        super().reset()
        self.fed = []
        self._skip_depth = 0



# A hyphen at the start of a word, which websearch_to_tsquery reads as "exclude this word".
_LEADING_HYPHENS = re.compile(r'(?:^|(?<=\s))-+')
# The word "or" in any case, which websearch_to_tsquery reads as the OR operator.
_OR_OPERATOR = re.compile(r'\bor\b', re.IGNORECASE)


def clean_websearch_phrase(phrase, max_length=500, literal=False):
    """Normalize a user's search phrase for websearch_to_tsquery, returning '' when nothing searchable remains.

    Leading hyphens are always removed, because BOA search doesn't offer word exclusion and a stray '-word' would
    silently hide results. Hyphens inside a word, as in '1-14', are left alone. With literal=True, quoted phrases
    and OR are disabled too, so that every word is simply required.
    """
    # NFKC folds look-alike characters, such as full-width letters, into their plain forms.
    phrase = unicodedata.normalize('NFKC', str(phrase or ''))
    # The length cap keeps a pasted document from becoming an enormous query.
    phrase = ' '.join(phrase.split())[:max_length]
    phrase = _LEADING_HYPHENS.sub('', phrase)
    if literal:
        phrase = phrase.replace('"', ' ')
        phrase = _OR_OPERATOR.sub(' ', phrase)
    return ' '.join(phrase.split())


def escape_like(text):
    """Escape LIKE and ILIKE wildcards, so that user text such as '100%' matches only itself."""
    # Backslash is Postgres's default LIKE escape character, so it has to be escaped first.
    return str(text).replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def parse_search_phrases(search_phrase):
    if not search_phrase or not str(search_phrase).strip():
        return []
    return list({t.group(0) for t in re.finditer(TEXT_SEARCH_PATTERN, search_phrase) if t})


stemmer = SnowballStemmer('english')


# Postgres's English stop words, which full-text search ignores. They count as matches only inside a phrase match,
# so that a query like "I tested for it" doesn't anchor the snippet on the first "I" in the note.
_SNIPPET_STOP_WORDS = frozenset({
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been',
    'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'did', 'do', 'does', 'doing', 'don', 'down', 'during', 'each', 'few',
    'for', 'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i',
    'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 's', 'same', 'she', 'should', 'so', 'some',
    'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
    'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
    'why', 'will', 'with', 'you', 'your', 'yours', 'yourself', 'yourselves',
})


def search_result_text_snippet(text, search_phrase):
    """Return an HTML snippet of the text around the passage that best matches the search phrase.

    The window goes to the longest run of words that matches the query in order, if that run holds at least two
    meaningful (non-stop) words. Otherwise it goes where the most distinct meaningful query terms sit close together,
    with ties going to the earliest match. Matching is by stem, and every piece of text is HTML-escaped because the
    frontend renders snippets with v-html.
    """
    tag_stripped_body = strip_html(text)
    snippet_padding = app.config['NOTES_SEARCH_RESULT_SNIPPET_PADDING']
    words = list(re.finditer(TEXT_SEARCH_PATTERN, tag_stripped_body))
    if not words:
        return html.escape(tag_stripped_body)
    word_stems = [stemmer.stem(w.group(0)) for w in words]

    # Query words stay in their typed order, since phrase matching depends on it.
    query_words = [t.group(0).lower() for t in re.finditer(TEXT_SEARCH_PATTERN, search_phrase or '')]
    query_stems = [stemmer.stem(w) for w in query_words]
    content_stems = {stemmer.stem(w) for w in query_words if w not in _SNIPPET_STOP_WORDS}
    if not content_stems:
        # A query made only of stop words still deserves highlighting.
        content_stems = set(query_stems)

    phrase_start, phrase_end, highlighted = _find_snippet_phrase(word_stems, query_stems, content_stems)
    for index, stem in enumerate(word_stems):
        if stem in content_stems:
            highlighted.add(index)

    if phrase_start is not None:
        anchor_start, anchor_end = phrase_start, phrase_end
    else:
        anchor_start = _find_densest_snippet_anchor(word_stems, content_stems, snippet_padding)
        anchor_end = anchor_start
    if anchor_start is None:
        # Nothing matched, so show the start of the text.
        return _render_snippet(tag_stripped_body, words, 0, min(len(words) - 1, snippet_padding), highlighted)

    first = max(0, anchor_start - snippet_padding)
    # Stretch the window to the end of a long phrase. A phrase is never longer than the query, so this stays bounded.
    last = min(len(words) - 1, max(anchor_start + snippet_padding, anchor_end))
    return _render_snippet(tag_stripped_body, words, first, last, highlighted)


def _find_snippet_phrase(word_stems, query_stems, content_stems):
    """Find the longest run of text words matching consecutive query words, scored by its count of meaningful words.

    Returns the best run's first and last word indexes (or None, None) and the set of word indexes inside every run
    that counts as a phrase, so those words, stop words included, get highlighted.
    """
    query_positions = {}
    for position, stem in enumerate(query_stems):
        query_positions.setdefault(stem, []).append(position)

    # Dynamic programming from right to left: runs[j] holds (length, meaningful words) of the match that starts at the
    # current text word and query word j. Only positions where the stems agree are stored, so long notes stay cheap.
    best = None
    phrase_words = set()
    next_runs = {}
    for index in range(len(word_stems) - 1, -1, -1):
        runs = {}
        for position in query_positions.get(word_stems[index], []):
            length, meaningful = next_runs.get(position + 1, (0, 0))
            runs[position] = (length + 1, meaningful + (query_stems[position] in content_stems))
        if runs:
            length, meaningful = max(runs.values(), key=lambda run: (run[1], run[0]))
            if length > 1 and meaningful > 1:
                phrase_words.update(range(index, index + length))
                # The scan runs backward, so ">=" lets an earlier run win a tie.
                if best is None or (meaningful, length) >= (best[1], best[2]):
                    best = (index, meaningful, length)
        next_runs = runs
    if best is None:
        return None, None, phrase_words
    return best[0], best[0] + best[2] - 1, phrase_words


def _find_densest_snippet_anchor(word_stems, content_stems, snippet_padding):
    """Return the index of the matching word whose centered window holds the most distinct query terms, or None."""
    matches = [index for index, stem in enumerate(word_stems) if stem in content_stems]
    best_index = None
    best_count = 0
    counts = {}
    left = right = 0
    # Two pointers keep a running count of the matches within the padding on either side of each candidate.
    for index in matches:
        while right < len(matches) and matches[right] <= index + snippet_padding:
            stem = word_stems[matches[right]]
            counts[stem] = counts.get(stem, 0) + 1
            right += 1
        while matches[left] < index - snippet_padding:
            stem = word_stems[matches[left]]
            counts[stem] -= 1
            if not counts[stem]:
                del counts[stem]
            left += 1
        if len(counts) > best_count:
            best_index, best_count = index, len(counts)
    return best_index


def _render_snippet(body, words, first, last, highlighted):
    """Render words first through last as escaped HTML, bolding highlighted words and marking cut-off ends."""
    # A window that starts at the first word keeps any leading punctuation, such as an opening quote.
    snippet = '...' if first > 0 else ''
    position = words[first].start(0) if first > 0 else 0
    for index in range(first, last + 1):
        word_match = words[index]
        snippet += html.escape(body[position:word_match.start(0)])
        word = html.escape(word_match.group(0))
        snippet += f'<strong>{word}</strong>' if index in highlighted else word
        position = word_match.end(0)
    if last == len(words) - 1:
        snippet += html.escape(body[position:])
    else:
        snippet += '...'
    return snippet


def strip_html(text, max_passes=3):
    """Strip tags, including tags that were entity-encoded (e.g. &lt;script&gt; &amp;lt;script&amp;gt;)."""
    for _ in range(max_passes):
        tag_stripper = HTMLTagStripper()
        tag_stripper.feed(text)
        tag_stripper.close()
        stripped_text = tag_stripper.get_data()
        if stripped_text == text:
            # nothing left to decode or strip
            break
        text = stripped_text
    return re.sub(r'\s+', ' ', text)


def _localize_datetime(dt):
    return dt.astimezone(pytz.timezone(app.config['TIMEZONE']))
