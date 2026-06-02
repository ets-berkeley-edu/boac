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

from flask import current_app as app

from boac.externals import data_loch
from boac.lib.sis_advising import resolve_sis_created_at, resolve_sis_updated_at
from boac.lib.util import TEXT_SEARCH_PATTERN, get_benchmarker, join_if_present, search_result_text_snippet
from boac.merged.advising_note import note_to_compatible_json
from boac.merged.advising_search import (
    build_comment_search_result,
    get_students_by_sid,
    merge_search_feed,
    parse_search_phrases_for_eforms,
    resolved_comment_total_count,
    student_search_feed,
)
from boac.merged.calnet import get_uid_for_csid
from boac.models.comment import Comment
from boac.models.comment_parent import EFORM_COMMENT_PARENT_TYPES

_EFORM_DATA_SOURCE_TO_PARENT_TYPE = {
    'student_late_drop_eforms': 'late_drop_eform',
    'student_cpp_change_eforms': 'cpp_change_eform',
    'student_course_load_eforms': 'course_load_eform',
}


def search_advising_eforms(
    search_phrase,
    advisor_csid=None,
    advisor_uid=None,
    student_csid=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
    include_body_search=True,
):
    benchmark = get_benchmarker('search_advising_eforms')
    benchmark('begin')

    search_terms = parse_search_phrases_for_eforms(search_phrase)

    advisor_uid = get_uid_for_csid(app, advisor_csid) if (not advisor_uid and advisor_csid) else advisor_uid

    fetch_limit = offset + limit
    body_total = 0
    body_feed = []
    if include_body_search:
        benchmark('begin loch eforms query')
        loch_results = data_loch.search_sis_eforms(
            search_phrases=search_terms or None,
            student_csid=student_csid,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            offset=0,
            limit=fetch_limit,
        )
        benchmark('end loch eforms query')
        body_total = loch_results['total_matching_count']
        body_feed = _get_loch_eforms_search_results(loch_results['rows'], search_terms)

    benchmark('begin eform comments query')
    comment_results = Comment.search_by_parent_types(
        parent_types=EFORM_COMMENT_PARENT_TYPES,
        search_phrases=search_terms or None,
        author_uid=advisor_uid,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=0,
        limit=fetch_limit,
    )
    benchmark('end eform comments query')

    comment_feed = _get_eform_comment_search_results(
        comment_results['rows'],
        search_terms,
        student_csid=student_csid,
    )
    comment_total = resolved_comment_total_count(comment_results, comment_feed, fetch_limit)

    merged = merge_search_feed(body_feed, comment_feed, offset, limit)
    return {
        'eforms': merged,
        'totalEformCount': body_total + comment_total,
    }


def _eform_summary_text(eform_row):
    compatible = note_to_compatible_json(eform_row)
    eform = compatible.get('eForm') or {}
    data_source = eform.get('dataSource') or eform_row.get('data_source')
    action = eform.get('action') or eform_row.get('requested_action') or eform_row.get('eform_action_description')
    status = eform.get('status') or eform_row.get('eform_status')
    if data_source == 'student_cpp_change_eforms':
        return join_if_present(' - ', [f'Career Program Plan eForm: {action}', status])
    if data_source == 'student_course_load_eforms':
        return join_if_present(' - ', [f'Reduced Course Load eForm: {action}', status])
    if data_source == 'student_late_drop_eforms':
        course = eform.get('courseName') or eform_row.get('course_display_name')
        return join_if_present(' - ', [f'Late Change of Schedule Request eForm: {course}', action, status])
    return join_if_present(' - ', [f'eForm: {action}', status])


def _get_loch_eforms_search_results(loch_results, search_terms):
    results = []
    if not loch_results:
        return results
    students_by_sid = get_students_by_sid([row.get('sid') for row in loch_results])
    for eform_row in loch_results:
        sid = eform_row.get('sid')
        student = student_search_feed(sid, students_by_sid)
        if not student:
            continue
        summary = _eform_summary_text(eform_row)
        parent_type = _EFORM_DATA_SOURCE_TO_PARENT_TYPE.get(eform_row.get('data_source'))
        compatible = note_to_compatible_json(eform_row)
        results.append({
            'kind': 'eform',
            'id': eform_row.get('id'),
            'parentType': parent_type,
            'eForm': compatible.get('eForm'),
            'createdAt': resolve_sis_created_at(eform_row),
            'updatedAt': resolve_sis_updated_at(eform_row),
            'snippet': search_result_text_snippet(summary, search_terms, TEXT_SEARCH_PATTERN),
            'studentSid': sid,
            'student': student,
        })
    return results


def _get_eform_comment_search_results(comment_rows, search_terms, student_csid=None):
    if not comment_rows:
        return []

    parent_type_to_ids = {}
    for _comment, parent_type, parent_id in comment_rows:
        parent_type_to_ids.setdefault(parent_type, []).append(parent_id)

    eform_rows = data_loch.get_sis_eforms_by_ids(parent_type_to_ids)
    eforms_by_key = {
        (_EFORM_DATA_SOURCE_TO_PARENT_TYPE.get(row.get('data_source')), str(row.get('id'))): row
        for row in eform_rows
    }

    student_sids = []
    resolved_rows = []
    for comment, parent_type, parent_id in comment_rows:
        eform_row = eforms_by_key.get((parent_type, str(parent_id)))
        if not eform_row:
            continue
        sid = eform_row.get('sid')
        if student_csid and sid != student_csid:
            continue
        student_sids.append(sid)
        resolved_rows.append((comment, parent_type, parent_id, eform_row))

    students_by_sid = get_students_by_sid(student_sids)
    results = []
    for comment, parent_type, parent_id, eform_row in resolved_rows:
        compatible = note_to_compatible_json(eform_row)
        row = build_comment_search_result(
            comment,
            parent_type,
            parent_id,
            search_terms,
            eform_row.get('sid'),
            students_by_sid,
            kind='commentOnEform',
            extra_fields={'eForm': compatible.get('eForm')},
        )
        if row:
            results.append(row)
    return results
