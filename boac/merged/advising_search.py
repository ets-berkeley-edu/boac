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

import re
from operator import itemgetter

from flask import current_app as app
from flask_login import current_user

from boac.externals import data_loch
from boac.lib.sis_advising import (
    resolve_sis_created_at,
    resolve_sis_updated_at,
)
from boac.lib.util import TEXT_SEARCH_PATTERN, camelize, get_benchmarker, join_if_present, search_result_text_snippet, to_iso_format
from boac.merged.advising_note import get_note_author_summary
from boac.merged.calnet import get_calnet_users_for_csids, get_uid_for_csid
from boac.models.note import Note


def parse_search_phrases(search_phrase):
    if not search_phrase or not str(search_phrase).strip():
        return []
    return list({t.group(0) for t in re.finditer(TEXT_SEARCH_PATTERN, search_phrase) if t})


# Display-title prefixes from advising_eform._eform_summary_text and src/lib/note.ts.
# Tokens listed only appear in the label, not in typical SIS field values.
_EFORM_DISPLAY_TITLE_PREFIX_STRIP = (
    ('Career Program Plan eForm', frozenset({'Career', 'eForm'})),
    ('Reduced Course Load eForm', frozenset({'Course', 'Load', 'eForm'})),
    ('Late Change of Schedule Request eForm', frozenset({'Late', 'Change', 'Schedule', 'Request', 'eForm'})),
)


def parse_search_phrases_for_eforms(search_phrase):
    """Drop label-only tokens when the query includes a known eForm display-title prefix."""
    terms = parse_search_phrases(search_phrase)
    if not terms:
        return terms
    phrase = str(search_phrase).replace('\u2013', ' ').replace('\u2014', ' ').lower()
    strip_tokens = set()
    for prefix, tokens in _EFORM_DISPLAY_TITLE_PREFIX_STRIP:
        if prefix.lower() in phrase:
            strip_tokens |= tokens
    if not strip_tokens:
        return terms
    stripped = [term for term in terms if term not in strip_tokens]
    return stripped or terms


def merge_search_feed(body_feed, comment_feed, offset, limit, secondary_sort='id'):
    combined = body_feed + comment_feed
    combined.sort(key=itemgetter('rank', secondary_sort), reverse=True)
    return combined[offset:offset + limit]


def get_students_by_sid(sids):
    student_rows = data_loch.get_basic_student_data([sid for sid in sids if sid])
    return {row.get('sid'): row for row in student_rows}


def student_search_feed(sid, students_by_sid):
    student_row = students_by_sid.get(sid, {})
    if not student_row:
        return None
    return {
        'uid': student_row.get('uid'),
        'firstName': student_row.get('first_name'),
        'lastName': student_row.get('last_name'),
        'sid': sid,
    }


def comment_author_feed(comment):
    return get_note_author_summary({
        'authorUid': comment.author_uid,
        'authorName': comment.author_name,
        'authorRole': comment.author_role,
        'authorDeptCodes': comment.author_dept_codes,
    })


def build_comment_search_result(
        comment,
        parent_type,
        parent_id,
        search_terms,
        student_sid,
        students_by_sid,
        *,
        kind,
        extra_fields=None,
):
    student = student_search_feed(student_sid, students_by_sid)
    if not student:
        return None
    row = {
        'kind': kind,
        'id': comment.id,
        'parentType': parent_type,
        'parentId': parent_id,
        'createdAt': to_iso_format(comment.created_at),
        'updatedAt': to_iso_format(comment.updated_at),
        'snippet': search_result_text_snippet(comment.body, search_terms, TEXT_SEARCH_PATTERN),
        'studentSid': student_sid,
        'student': student,
        'comment': {
            **comment.to_api_json(),
            'author': comment_author_feed(comment),
        },
        'rank': 0,
    }
    if extra_fields:
        row.update(extra_fields)
    return row


def resolved_comment_total_count(comment_results, comment_feed, fetch_limit):
    total = comment_results['total_matching_count']
    if total <= fetch_limit:
        return len(comment_feed)
    return total


def search_advising_notes(
    search_phrase,
    author_csid=None,
    author_uid=None,
    student_csid=None,
    department_codes=None,
    topic=None,
    datetime_from=None,
    datetime_to=None,
    peer_advising_department_id=None,
    peer_advisor_uid=None,
    offset=0,
    limit=20,
):
    benchmark = get_benchmarker('search_advising_notes')
    benchmark('begin')

    author_uid = get_uid_for_csid(app, author_csid) if (not author_uid and author_csid) else author_uid
    search_phrases = parse_search_phrases(search_phrase)

    # Our offset calculations are unforuntately fussy because note parsing might reveal notes associated with students no
    # longer in BOA, which we won't include in the feed; so we don't actually know the length of our result set until parsing
    # is complete. Accordingly, we query local notes in a batch size somewhat larger than the number of notes we'll actually return.
    notes_query_batch_size = (offset + limit) * 2
    notes_query_iteration = 0
    notes_feed = []

    while True:
        if peer_advising_department_id:
            benchmark(f'begin peer advising notes query (iteration {notes_query_iteration})')
            ranked_note_ids = data_loch.search_peer_advising_notes(
                search_phrases,
                peer_advising_department_id,
                peer_advisor_uid=peer_advisor_uid,
                offset=offset,
                limit=limit,
            )
            search_results = Note.ranked_search_results_by_id(ranked_note_ids)
            benchmark(f'end peer advising notes query (iteration {notes_query_iteration})')
        else:
            benchmark(f'begin combined local and external notes query (iteration {notes_query_iteration})')
            search_results = data_loch.search_advising_notes(
                search_phrase,
                author_uid=author_uid,
                author_csid=author_csid,
                student_csid=student_csid,
                department_codes=department_codes,
                topic=topic,
                datetime_from=datetime_from,
                datetime_to=datetime_to,
                offset=offset,
                limit=limit,
            )
            benchmark(f'end combined local and external notes query (iteration {notes_query_iteration})')
        total_matching_count = search_results['total_matching_count']

        if len(search_results['rows']):
            benchmark(f'begin notes parsing (iteration {notes_query_iteration})')
            student_rows = data_loch.get_basic_student_data([row.get('sid') for row in search_results['rows']])
            students_by_sid = {r.get('sid'): r for r in student_rows}
            if peer_advising_department_id:
                cutoff = min(len(search_results), (offset + limit - len(notes_feed)))
                _parse_peer_advising_note_search_results(
                    search_phrases,
                    search_results,
                    cutoff,
                    students_by_sid,
                    notes_feed,
                )
            else:
                advisor_sids = list(set([row.get('advisor_sid') for row in search_results['rows'] if row.get('advisor_sid') is not None]))
                advisors_by_sid = get_calnet_users_for_csids(app, advisor_sids)
                _parse_note_search_results(
                    search_phrases,
                    search_results,
                    students_by_sid,
                    advisors_by_sid,
                    notes_feed,
                )
            benchmark(f'end notes parsing (iteration {notes_query_iteration})')

        # Stop querying notes if 1) we didn't return a full batch, 2) we have all the notes we need.
        if total_matching_count < notes_query_batch_size or len(notes_feed) == offset + limit:
            break
        notes_query_iteration += 1
    return {
        'notes': notes_feed,
        'totalNoteCount': total_matching_count,
    }

def _external_note_to_search_result(note, search_terms, advisor_feed):
    advisor_name = None
    if advisor_feed:
        advisor_name = advisor_feed.get('name') or join_if_present(' ', [advisor_feed.get('first_name'), advisor_feed.get('last_name')])
    note_body = (note.get('note_body') or '').strip() or join_if_present(', ', [note.get('note_category'), note.get('note_subcategory')])
    return {
        'id': note.get('id'),
        'studentSid': note.get('sid'),
        'studentUid': note.get('uid'),
        'studentName': join_if_present(' ', [note.get('first_name'), note.get('last_name')]),
        'advisorSid': note.get('advisor_sid'),
        'advisorName': advisor_name or join_if_present(' ', [note.get('advisor_first_name'), note.get('advisor_last_name')]),
        'noteSnippet': search_result_text_snippet(note_body, search_terms, TEXT_SEARCH_PATTERN),
        'createdAt': resolve_sis_created_at(note),
        'updatedAt': resolve_sis_updated_at(note),
    }

def _local_note_to_search_result(note, sid, search_terms, student_row):
    omit_note_body = note.get('isPrivate') and not current_user.can_access_private_notes
    subject = note.get('subject')
    text = subject if omit_note_body else join_if_present(' - ', [subject, note.get('body')])
    return {
        'id': note.get('id'),
        'parentNoteId': note.get('parentNoteId'),
        'studentSid': sid,
        'studentUid': student_row.get('uid'),
        'studentName': join_if_present(' ', [student_row.get('first_name'), student_row.get('last_name')]),
        'advisorUid': note.get('authorUid') or note.get('advisorUid'),
        'advisorName': note.get('authorName'),
        'attachmentCount': note.get('attachmentCount'),
        'noteSnippet': search_result_text_snippet(text, search_terms, TEXT_SEARCH_PATTERN),
        'createdAt': to_iso_format(note.get('createdAt')),
        'updatedAt': to_iso_format(note.get('updatedAt')),
    }

def _parse_peer_advising_note_search_results(search_phrases, search_results, cutoff, students_by_sid, notes_feed):
    results = []
    student_rows = data_loch.get_basic_student_data([row.get('sid') for row in search_results['rows']])
    students_by_sid = {r.get('sid'): r for r in student_rows}
    for row in search_results['rows']:
        note = {camelize(key): row[key] for key in row}
        sid = note.get('sid')
        student_row = students_by_sid.get(sid, {})
        if student_row:
            results.append(_local_note_to_search_result(note, sid, search_phrases, student_row))
        if len(results) == cutoff:
            break
    notes_feed += results

def _parse_note_search_results(search_phrases, search_results, students_by_sid, advisors_by_sid, notes_feed):
    for note in search_results['rows']:
        if note['id'].startswith('boa-'):
            local_note = {
                **{camelize(key): note[key] for key in note},
                ' ': note['id'],
                'id': int((note['id']).split('-')[-1]),
                'body': note['note_body'],
            }
            sid = local_note.get('sid')
            student_row = students_by_sid.get(sid, {})
            if student_row:
                notes_feed.append(_local_note_to_search_result(local_note, sid, search_phrases, student_row))
        else:
            advisor_feed = advisors_by_sid.get(note.get('advisor_sid'))
            notes_feed.append(_external_note_to_search_result(note, search_phrases, advisor_feed))

