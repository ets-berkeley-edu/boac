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

from html.parser import HTMLParser
from itertools import groupby
from operator import itemgetter
import re

from boac.externals import data_loch, s3
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.util import camelize, get_benchmarker, join_if_present
from boac.merged.calnet import get_calnet_users_for_csids
from boac.merged.student import get_student_query_scope, narrow_scope_by_criteria
from boac.models.note import Note
from boac.models.note_attachment import NoteAttachment
from boac.models.note_read import NoteRead
from dateutil.tz import tzutc
from flask import current_app as app
from flask_login import current_user
from nltk.stem.snowball import SnowballStemmer

"""Provide advising note data from local and external sources."""

NOTE_SEARCH_PATTERN = r'(\w*[.:/-@]\w+([.:/-]\w+)*)|[^\s?!(),;:.`]+'


def get_advising_notes(sid):
    benchmark = get_benchmarker(f'get_advising_notes {sid}')
    benchmark('begin')
    notes_by_id = {}
    benchmark('begin SIS advising notes query')
    notes_by_id.update(get_sis_advising_notes(sid))
    benchmark('begin ASC advising notes query')
    notes_by_id.update(get_asc_advising_notes(sid))
    benchmark('begin non legacy advising notes query')
    notes_by_id.update(get_non_legacy_advising_notes(sid))
    if not notes_by_id.values():
        return None
    notes_read = NoteRead.get_notes_read_by_user(current_user.id, notes_by_id.keys())
    for note_read in notes_read:
        note_feed = notes_by_id.get(note_read.note_id)
        if note_feed:
            note_feed['read'] = True
        else:
            app.logger.error(f'DB query mismatch for note id {note_read.note_id}')
    benchmark('end')
    return list(notes_by_id.values())


def get_sis_advising_notes(sid):
    notes_by_id = {}
    legacy_notes = data_loch.get_sis_advising_notes(sid)
    legacy_topics = _get_sis_advising_note_topics(sid)
    legacy_attachments = _get_advising_note_attachments(sid)
    for legacy_note in legacy_notes:
        note_id = legacy_note['id']
        note = {camelize(key): legacy_note[key] for key in legacy_note.keys()}
        notes_by_id[note_id] = note_to_compatible_json(
            note=note,
            topics=legacy_topics.get(note_id),
            attachments=legacy_attachments.get(note_id),
        )
        notes_by_id[note_id]['isLegacy'] = True
    return notes_by_id


def get_asc_advising_notes(sid):
    notes_by_id = {}
    legacy_topics = _get_asc_advising_note_topics(sid)
    for legacy_note in data_loch.get_asc_advising_notes(sid):
        note_id = legacy_note['id']
        note = {camelize(key): legacy_note[key] for key in legacy_note.keys()}
        note['deptCode'] = ['UWASC']
        notes_by_id[note_id] = note_to_compatible_json(
            note=note,
            topics=legacy_topics.get(note_id),
        )
        notes_by_id[note_id]['isLegacy'] = True
    return notes_by_id


def get_non_legacy_advising_notes(sid):
    notes_by_id = {}
    for note in [n.to_api_json() for n in Note.get_notes_by_sid(sid)]:
        note_id = note['id']
        notes_by_id[str(note_id)] = note_to_compatible_json(
            note=note,
            attachments=note.get('attachments'),
            topics=note.get('topics'),
        )
    return notes_by_id


def search_advising_notes(
    search_phrase,
    author_csid=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
):

    benchmark = get_benchmarker('search_advising_notes')
    benchmark('begin')

    scope = narrow_scope_by_criteria(get_student_query_scope())

    # In the interest of keeping our search implementation flexible, we mimic a join by first querying RDS
    # for all student rows matching user scope, then incorporating SIDs into the notes query as a very large
    # array filter. If it looks like notes search is going to live in RDS for the long haul, this could be
    # rewritten with a proper join; but this will require student profile data (which lives in Nessie RDS) to
    # somehow join up with advising note data (which lives in BOA RDS).

    student_query_tables, student_query_filter, student_query_bindings = data_loch.get_students_query(scope=scope)
    if not student_query_tables:
        return []

    benchmark('begin sids query')
    sids_result = data_loch.safe_execute_rds(
        f'SELECT sas.sid, sas.uid, sas.first_name, sas.last_name {student_query_tables} {student_query_filter}',
        **student_query_bindings,
    )
    benchmark('end sids query')
    if not sids_result:
        return []
    student_rows_by_sid = {row['sid']: row for row in sids_result}
    sid_filter = '{' + ','.join(student_rows_by_sid.keys()) + '}'

    search_terms = [t.group(0) for t in list(re.finditer(NOTE_SEARCH_PATTERN, search_phrase)) if t]
    search_phrase = ' & '.join(search_terms)

    # TODO We're currently retrieving all results for the sake of subsequent offset calculations. As the number of notes in
    # BOA grows (and possibly requires us to use some kind of staging table for search indexing), we'll need to revisit.
    benchmark('begin local notes query')
    local_results = Note.search(
        search_phrase=search_phrase,
        sid_filter=sid_filter,
        author_csid=author_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
    )
    benchmark('end local notes query')
    local_notes_count = len(local_results)
    cutoff = min(local_notes_count, offset + limit)

    benchmark('begin local notes parsing')
    notes_feed = _get_local_notes_search_results(local_results[offset:cutoff], student_rows_by_sid, search_terms)
    benchmark('end local notes parsing')

    if len(notes_feed) == limit:
        return notes_feed

    # When querying the loch for notes, we use an actual join rather than the cumbersome SID list since everything lives in
    # Nessie RDS.

    benchmark('begin loch notes query')
    loch_results = data_loch.search_advising_notes(
        search_phrase=search_phrase,
        student_query_tables=student_query_tables,
        student_query_filter=student_query_filter,
        student_query_bindings=student_query_bindings,
        author_csid=author_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=max(0, offset - local_notes_count),
        limit=(limit - len(notes_feed)),
    )
    benchmark('end loch notes query')

    benchmark('begin loch notes parsing')
    notes_feed += _get_loch_notes_search_results(loch_results, search_terms)
    benchmark('end loch notes parsing')

    return notes_feed


def _get_local_notes_search_results(local_results, student_rows_by_sid, search_terms):
    results = []
    for row in local_results:
        note = {camelize(key): row[key] for key in row.keys()}
        student_row = student_rows_by_sid[note.get('sid')]
        results.append({
            'id': note.get('id'),
            'studentSid': note.get('sid'),
            'studentUid': student_row.get('uid'),
            'studentName': join_if_present(' ', [student_row.get('first_name'), student_row.get('last_name')]),
            'advisorUid': note.get('authorUid'),
            'advisorName': note.get('authorName'),
            'noteSnippet': _notes_text_snippet(join_if_present(' - ', [note.get('subject'), note.get('body')]), search_terms),
            'createdAt': _isoformat(note, 'createdAt'),
            'updatedAt': _isoformat(note, 'updatedAt'),
        })
    return results


def _get_loch_notes_search_results(loch_results, search_terms):
    results = []
    calnet_advisor_feeds = get_calnet_users_for_csids(
        app,
        list(set([row.get('advisor_sid') for row in loch_results if row.get('advisor_sid') is not None])),
    )
    for row in loch_results:
        note = {camelize(key): row[key] for key in row.keys()}
        advisor_feed = calnet_advisor_feeds.get(note.get('advisorSid'))
        advisor_name = join_if_present(' ', [advisor_feed.get('firstName'), advisor_feed.get('lastName')]) if advisor_feed else None
        results.append({
            'id': note.get('id'),
            'studentSid': note.get('sid'),
            'studentUid': note.get('uid'),
            'studentName': join_if_present(' ', [note.get('firstName'), note.get('lastName')]),
            'advisorSid': note.get('advisorSid'),
            'advisorName': advisor_name or join_if_present(' ', [note.get('advisorFirstName'), note.get('advisorLastName')]),
            'noteSnippet': _notes_text_snippet(note.get('noteBody') or '', search_terms),
            'createdAt': _resolve_created_at(note),
            'updatedAt': _resolve_updated_at(note),
        })
    return results


def get_boa_attachment_stream(attachment_id):
    attachment = NoteAttachment.find_by_id(attachment_id)
    if attachment:
        path = attachment.path_to_attachment
        return {
            'filename': attachment.get_user_filename(),
            'stream': s3.stream_object(app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET'], path),
        }
    else:
        return None


def get_legacy_attachment_stream(filename):
    # Filenames come prefixed with SID by convention.
    for i, c in enumerate(filename):
        if not c.isdigit():
            break
    sid = filename[:i]
    if not sid:
        return None
    # Ensure that the file exists and the user has permission to see it.
    attachment_result = data_loch.get_sis_advising_note_attachment(sid, filename, scope=get_student_query_scope())
    if not attachment_result or not attachment_result[0]:
        return None
    if attachment_result[0].get('created_by') == 'UCBCONVERSION':
        display_filename = filename
    else:
        display_filename = attachment_result[0].get('user_file_name')
    s3_key = '/'.join([app.config['DATA_LOCH_S3_ADVISING_NOTE_ATTACHMENT_PATH'], sid, filename])
    return {
        'filename': display_filename,
        'stream': s3.stream_object(app.config['DATA_LOCH_S3_ADVISING_NOTE_BUCKET'], s3_key),
    }


def note_to_compatible_json(note, topics=(), attachments=None, note_read=False):
    # We have legacy notes and notes created via BOAC. The following sets a standard for the front-end.
    departments = []
    dept_codes = note.get('deptCode') if 'deptCode' in note else note.get('authorDeptCodes') or []
    for dept_code in dept_codes:
        departments.append({
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code) or dept_code,
        })
    return {
        'id': note.get('id'),
        'sid': note.get('sid'),
        'author': {
            'id': note.get('authorId'),
            'uid': note.get('authorUid'),
            'sid': note.get('advisorSid'),
            'name': note.get('authorName'),
            'role': note.get('authorRole'),
            'departments': departments,
        },
        'subject': note.get('subject'),
        'body': note.get('body') or note.get('noteBody'),
        'category': note.get('noteCategory'),
        'subcategory': note.get('noteSubcategory'),
        'appointmentId': note.get('appointmentId'),
        'createdBy': note.get('createdBy'),
        'createdAt': _resolve_created_at(note),
        'updatedBy': note.get('updated_by'),
        'updatedAt': _resolve_updated_at(note),
        'read': True if note_read else False,
        'topics': topics,
        'attachments': attachments,
    }


def _resolve_created_at(note):
    return note.get('createdAt').date().isoformat() if note.get('createdBy') == 'UCBCONVERSION' else _isoformat(note, 'createdAt')


def _resolve_updated_at(note):
    # Notes converted from pre-CS legacy systems have an updated_at value indicating (probably)
    # time of conversion rather than an update by a human.
    return None if note.get('createdBy') == 'UCBCONVERSION' else _isoformat(note, 'updatedAt')


def _get_sis_advising_note_topics(sid):
    topics = data_loch.get_sis_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=itemgetter('advising_note_id')):
        topics_by_id[advising_note_id] = [topic['note_topic'] for topic in topics]
    return topics_by_id


def _get_advising_note_attachments(sid):
    attachments = data_loch.get_sis_advising_note_attachments(sid)
    attachments_by_id = {}

    def _attachment_to_json(attachment):
        sis_file_name = attachment.get('sis_file_name')
        return {
            'id': sis_file_name,
            'sisFilename': sis_file_name,
            'displayName': sis_file_name if attachment.get('created_by') == 'UCBCONVERSION' else attachment.get('user_file_name'),
        }
    for advising_note_id, attachments in groupby(attachments, key=itemgetter('advising_note_id')):
        attachments_by_id[advising_note_id] = [_attachment_to_json(a) for a in attachments]
    return attachments_by_id


def _get_asc_advising_note_topics(sid):
    topics = data_loch.get_asc_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=itemgetter('id')):
        topics_by_id[advising_note_id] = [topic['topic'] for topic in topics]
    return topics_by_id


def _isoformat(obj, key):
    value = obj.get(key)
    return value and value.astimezone(tzutc()).isoformat()


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


def _notes_text_snippet(note_body, search_terms):
    tag_stripper.feed(note_body)
    tag_stripped_body = tag_stripper.get_data()
    tag_stripper.reset()

    snippet_padding = app.config['NOTES_SEARCH_RESULT_SNIPPET_PADDING']
    note_words = list(re.finditer(NOTE_SEARCH_PATTERN, tag_stripped_body))
    stemmed_search_terms = [stemmer.stem(term) for term in search_terms]

    snippet = None
    match_index = None
    start_position = 0

    for index, word_match in enumerate(note_words):
        stem = stemmer.stem(word_match.group(0))
        if match_index is None and stem in stemmed_search_terms:
            match_index = index
            if index > snippet_padding:
                start_position = note_words[index - snippet_padding].start(0)
            snippet = '...' if start_position > 0 else ''
        if match_index is not None:
            snippet += tag_stripped_body[start_position:word_match.start(0)]
            if stem in stemmed_search_terms:
                snippet += '<strong>'
            snippet += word_match.group(0)
            if stem in stemmed_search_terms:
                snippet += '</strong>'
            if index == len(note_words) - 1:
                snippet += tag_stripped_body[word_match.end(0):len(tag_stripped_body)]
                break
            elif index == match_index + snippet_padding:
                end_position = note_words[index].end(0)
                snippet += tag_stripped_body[word_match.end(0):end_position]
                snippet += '...'
                break
            else:
                start_position = word_match.end(0)

    if snippet:
        return snippet
    else:
        if len(note_words) > snippet_padding:
            end_position = note_words[snippet_padding].end(0)
            return tag_stripped_body[0:end_position] + '...'
        else:
            return tag_stripped_body
