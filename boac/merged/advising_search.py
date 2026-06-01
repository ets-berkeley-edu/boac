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

from boac.externals import data_loch
from boac.lib.util import TEXT_SEARCH_PATTERN, search_result_text_snippet, to_iso_format
from boac.merged.advising_note import get_note_author_summary


def parse_search_phrases(search_phrase):
    if not search_phrase or not str(search_phrase).strip():
        return []
    return list({t.group(0) for t in re.finditer(TEXT_SEARCH_PATTERN, search_phrase) if t})


def merge_search_feed(body_feed, comment_feed, offset, limit):
    combined = body_feed + comment_feed
    combined.sort(key=lambda row: row.get('createdAt') or '', reverse=True)
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
    }
    if extra_fields:
        row.update(extra_fields)
    return row


def resolved_comment_total_count(comment_results, comment_feed, fetch_limit):
    total = comment_results['total_matching_count']
    if total <= fetch_limit:
        return len(comment_feed)
    return total
