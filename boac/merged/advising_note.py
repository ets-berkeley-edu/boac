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


from datetime import timezone
from itertools import groupby
import operator
import re

from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.util import camelize
from boac.merged.calnet import get_calnet_users_for_csids
from boac.merged.student import get_student_query_scope, narrow_scope_by_criteria
from boac.models.note import Note
from boac.models.note_read import NoteRead
from flask import current_app as app
from flask_login import current_user
from nltk.stem.snowball import SnowballStemmer


"""Provide advising note data from local and external sources."""


def get_advising_notes(sid):
    legacy_notes = data_loch.get_advising_notes(sid)
    legacy_topics = _get_advising_note_topics(sid)
    legacy_attachments = _get_advising_note_attachments(sid)
    notes_by_id = {}
    for legacy_note in legacy_notes:
        note_id = legacy_note['id']
        note = {camelize(key): legacy_note[key] for key in legacy_note.keys()}
        notes_by_id[note_id] = note_to_compatible_json(note, legacy_topics.get(note_id), legacy_attachments.get(note_id))
        notes_by_id[note_id]['isLegacy'] = True
    for note in [n.to_api_json() for n in Note.get_notes_by_sid(sid)]:
        note_id = note['id']
        notes_by_id[str(note_id)] = note_to_compatible_json(note)
    if not notes_by_id.values():
        return None
    notes_read = NoteRead.get_notes_read_by_user(current_user.id, notes_by_id.keys())
    for note_read in notes_read:
        note_feed = notes_by_id.get(note_read.note_id)
        if note_feed:
            note_feed['read'] = True
        else:
            app.logger.error(f'DB query mismatch for note id {note_read.note_id}')
    return list(notes_by_id.values())


def search_advising_notes(
    search_phrase=None,
    limit=None,
):
    scope = narrow_scope_by_criteria(get_student_query_scope())
    # In the interest of keeping our search implementation flexible, we mimic a join by first querying RDS
    # for all student rows matching user scope, then incorporating SIDs into the notes query as a very large
    # array filter. If it looks like notes search is going to live in RDS for the long haul, this could be
    # rewritten with a proper join.
    query_tables, query_filter, query_bindings = data_loch.get_students_query(scope=scope)
    if not query_tables:
        return []
    sids_result = data_loch.safe_execute_rds(
        f'SELECT sas.sid, sas.uid, sas.first_name, sas.last_name {query_tables} {query_filter}',
        **query_bindings,
    )
    if not sids_result:
        return []
    rows_by_sid = {row['sid']: row for row in sids_result}
    sid_filter = '{' + ','.join(rows_by_sid.keys()) + '}'

    search_terms = [t for t in re.split(r'\W+', search_phrase) if t]

    notes_results = data_loch.search_advising_notes(
        search_phrase=' & '.join(search_terms),
        sid_filter=sid_filter,
        limit=limit,
    )
    calnet_advisor_feeds = get_calnet_users_for_csids(app, [row.get('advisor_sid') for row in notes_results])

    def _notes_result_to_json(row):
        rds_row = rows_by_sid[row.get('sid')]
        advisor_feed = calnet_advisor_feeds.get(row.get('advisor_sid'))
        return {
            'studentSid': row.get('sid'),
            'studentUid': rds_row.get('uid'),
            'studentName': ' '.join([rds_row.get('first_name'), rds_row.get('last_name')]),
            'advisorSid': row.get('advisor_sid'),
            'advisorName': ' '.join([advisor_feed.get('firstName'), advisor_feed.get('lastName')]) if advisor_feed else None,
            'noteId': row.get('id'),
            'noteSnippet': notes_text_snippet(row.get('note_body'), search_terms),
            'createdAt': _stringify_note_timestamp(row.get('created_at')),
            'updatedAt': _stringify_note_timestamp(row.get('updated_at')),
        }
    return [_notes_result_to_json(row) for row in notes_results]


def note_to_compatible_json(note, topics=None, attachments=None):
    # We have legacy notes and notes created via BOA. The following sets a standard for the front-end.
    dept_codes = note.get('deptCode') if 'deptCode' in note else note.get('authorDeptCodes') or []
    return {
        'id': note.get('id'),
        'sid': note.get('sid'),
        'author': {
            'id': note.get('authorId'),
            'uid': note.get('authorUid'),
            'sid': note.get('advisorSid'),
            'name': note.get('authorName'),
            'role': note.get('authorRole'),
            'depts': [BERKELEY_DEPT_CODE_TO_NAME.get(code) for code in dept_codes],
        },
        'subject': note.get('subject'),
        'body': note.get('body') or note.get('noteBody'),
        'category': note.get('noteCategory'),
        'subcategory': note.get('noteSubcategory'),
        'appointmentId': note.get('appointmentId'),
        'createdBy': note.get('createdBy'),
        'createdAt': _stringify_note_timestamp(note.get('createdAt')),
        'updatedBy': note.get('updated_by'),
        'updatedAt': _stringify_note_timestamp(note.get('updatedAt')),
        'read': False,
        'topics': topics,
        'attachments': attachments,
    }


def _stringify_note_timestamp(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _get_advising_note_topics(sid):
    topics = data_loch.get_advising_note_topics(sid)
    topics_by_id = {}
    for advising_note_id, topics in groupby(topics, key=operator.itemgetter('advising_note_id')):
        topics_by_id[advising_note_id] = [topic['note_topic'] for topic in topics]
    return topics_by_id


def _get_advising_note_attachments(sid):
    attachments = data_loch.get_advising_note_attachments(sid)
    attachments_by_id = {}
    for advising_note_id, attachments in groupby(attachments, key=operator.itemgetter('advising_note_id')):
        attachments_by_id[advising_note_id] = [attachments['sis_file_name'] for attachments in attachments]
    return attachments_by_id


def notes_text_snippet(note_body, search_terms):
    stemmer = SnowballStemmer('english')
    stemmed_search_terms = [stemmer.stem(term) for term in search_terms]
    tag_stripped_body = re.sub(r'<[^>]+>', '', note_body)
    snippet_padding = app.config['NOTES_SEARCH_RESULT_SNIPPET_PADDING']
    note_words = list(re.finditer(r'\w+', tag_stripped_body))

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
        if match_index:
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
