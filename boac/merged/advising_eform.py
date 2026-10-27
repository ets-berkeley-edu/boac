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
from boac.lib.util import (
    TEXT_SEARCH_PATTERN,
    get_benchmarker,
    join_if_present,
    search_result_text_snippet,
    to_iso_format,
)
from boac.merged.advising_search import (
    get_note_author_summary,
    parse_search_phrases,
)
from boac.merged.calnet import get_uid_for_csid

_EFORM_DATA_SOURCE_TO_PARENT_TYPE = {
    'student_late_drop_eforms': 'late_drop_eform',
    'student_cpp_change_eforms': 'cpp_change_eform',
    'student_course_load_eforms': 'course_load_eform',
}

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


def search_advising_eforms(
    search_phrase,
    advisor_csid=None,
    advisor_uid=None,
    student_csid=None,
    datetime_from=None,
    datetime_to=None,
    offset=0,
    limit=20,
):
    benchmark = get_benchmarker('search_advising_eforms')
    benchmark('begin')

    search_terms = parse_search_phrases_for_eforms(search_phrase)
    advisor_uid = get_uid_for_csid(app, advisor_csid) if (not advisor_uid and advisor_csid) else advisor_uid
    fetch_limit = offset + limit

    benchmark('begin loch eforms query')
    loch_results = data_loch.search_eforms(
        search_phrases=search_terms,
        student_csid=student_csid,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=0,
        limit=fetch_limit,
    )
    benchmark('end loch eforms query')

    eforms_feed = _get_loch_eforms_search_results(loch_results['rows'], search_terms)

    return {
        'eforms': eforms_feed,
        'totalEformCount': loch_results['total_matching_count'],
    }


def _eform_summary_text(eform_row):
    eform = eform_row.get('eform') or eform_row
    data_source = eform_row.get('data_source')
    action = eform.get('action') or eform.get('requested_action') or eform.get('eform_action_description')
    status = eform.get('status') or eform.get('eform_status')
    if data_source == 'student_cpp_change_eforms':
        return join_if_present(' - ', [f'Career Program Plan eForm: {action}', status])
    if data_source == 'student_course_load_eforms':
        return join_if_present(' - ', [f'Reduced Course Load eForm: {action}', status])
    if data_source == 'student_late_drop_eforms':
        course = eform.get('courseName') or eform.get('course_display_name')
        return join_if_present(' - ', [f'Late Change of Schedule Request eForm: {course}', action, status])
    return join_if_present(' - ', [f'eForm: {action}', status])


def _get_loch_eforms_search_results(loch_rows, search_terms):
    results = []
    if not loch_rows:
        return results
    for eform_row in loch_rows:
        is_comment = eform_row.get('boa_id')
        summary = eform_row['body'] if is_comment else _eform_summary_text(eform_row)
        eform_type = _EFORM_DATA_SOURCE_TO_PARENT_TYPE.get(eform_row.get('data_source'))
        result = {
            'kind': 'commentOnEform' if is_comment else 'eform',
            'id': eform_row.get('parent_eform_id'),
            'type': eform_type,
            'createdAt': resolve_sis_created_at(eform_row),
            'snippet': search_result_text_snippet(summary, search_terms, TEXT_SEARCH_PATTERN),
            'student': {
                'sid': eform_row['student_sid'],
                'uid': eform_row['student_uid'],
                'firstName': eform_row['first_name'],
                'lastName': eform_row['last_name'],
            },
            'rank': eform_row.get('rank'),
            'updatedAt': to_iso_format(eform_row['updated_at']) if is_comment else resolve_sis_updated_at(eform_row),
        }
        if is_comment:
            result['comment'] = {
              'advisor': get_note_author_summary(eform_row),
              'id': eform_row['boa_id'],
            }
        results.append(result)
    return results
