"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.api.errors import ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import admin_or_director_required, admin_required, authorized_users_api_feed
from boac.externals.data_loch import get_asc_advising_note_count, get_e_and_i_advising_note_count, \
    get_sis_advising_note_count
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.merged.reports import get_boa_note_count_by_month, get_note_author_count, get_note_count, \
    get_note_count_per_batch, get_note_count_per_user, get_note_with_attachments_count, \
    get_note_with_topics_count, get_private_note_count, get_summary_of_boa_notes, low_assignment_scores
from boac.merged.sis_terms import current_term_id
from boac.models.authorized_user import AuthorizedUser
from boac.models.university_dept_member import UniversityDeptMember
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/reports/boa_notes/monthly_count')
@admin_or_director_required
def boa_note_count_by_month():
    return tolerant_jsonify(get_boa_note_count_by_month())


@app.route('/api/reports/boa_notes/metadata')
@admin_required
def get_boa_notes_metadata():
    return response_with_csv_download(
        rows=get_summary_of_boa_notes(),
        filename_prefix='boa_advising_notes_metadata',
        fieldnames=[
            'author_dept_codes',
            'author_name',
            'author_role',
            'author_uid',
            'cohort_names',
            'contact_type',
            'curated_group_names',
            'degree_awarded_dates',
            'degree_awarded_names',
            'is_private',
            'set_date',
            'sid',
            'student_first_name',
            'student_last_name',
            'subject',
            'topics',
            'created_at',
            'updated_at',
        ],
    )


@app.route('/api/reports/notes/<dept_code>')
@admin_or_director_required
def get_notes_report_by_dept(dept_code):
    dept_code = dept_code.upper()
    dept_name = BERKELEY_DEPT_CODE_TO_NAME.get(dept_code)
    if dept_name:
        if current_user.is_admin or _current_user_is_director_of(dept_code):
            total_note_count = get_note_count()
            note_count_per_batch = get_note_count_per_batch()
            return tolerant_jsonify({
                'asc': get_asc_advising_note_count(),
                'ei': get_e_and_i_advising_note_count(),
                'sis': get_sis_advising_note_count(),
                'boa': {
                    'authors': get_note_author_count(),
                    'privateNoteCount': get_private_note_count(),
                    'total': total_note_count,
                    'batchNotes': {
                        'totalBatchCount': len(note_count_per_batch),
                        'totalNoteCount': sum(note_count_per_batch),
                    },
                    'withAttachments': get_note_with_attachments_count(),
                    'withTopics': get_note_with_topics_count(),
                },
            })
        else:
            raise ForbiddenRequestError(f'You are unauthorized to view {dept_name} reports')
    else:
        raise ResourceNotFoundError(f'Unrecognized department code {dept_code}')


@app.route('/api/reports/users/<dept_code>')
@admin_or_director_required
def get_users_report(dept_code):
    dept_code = dept_code.upper()
    dept_name = BERKELEY_DEPT_CODE_TO_NAME.get(dept_code)
    if dept_name:
        if current_user.is_admin or _current_user_is_director_of(dept_code):
            users, total_user_count = AuthorizedUser.get_users(deleted=False, dept_code=dept_code)
            users = authorized_users_api_feed(users, sort_by='lastName')
            note_count_per_user = get_note_count_per_user(dept_code)
            for user in users:
                user['notesCreated'] = note_count_per_user.get(user['uid'], 0)
            return tolerant_jsonify({
                'users': users,
                'totalUserCount': total_user_count,
            })
        else:
            raise ForbiddenRequestError(f'You are unauthorized to view {dept_name} reports')
    else:
        raise ResourceNotFoundError(f'Unrecognized department code {dept_code}')


@app.route('/api/reports/available_departments')
@admin_or_director_required
def available_dept_codes():
    if current_user.is_admin:
        dept_codes = UniversityDeptMember.get_distinct_departments()
    else:
        dept_codes = UniversityDeptMember.get_distinct_departments(
            authorized_user_id=current_user.get_id(),
            role='director',
        )

    def _to_json(row):
        dept_code = row.upper()
        return {
            'code': dept_code,
            'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code),
        }
    return tolerant_jsonify([_to_json(d) for d in dept_codes])


@app.route('/api/reports/low_assignment_scores')
@admin_required
def report_low_assignment_scores():
    return tolerant_jsonify(low_assignment_scores(_term()))


def _current_user_is_director_of(dept_code):
    return next((d for d in current_user.departments if d['code'] == dept_code and d['role'] == 'director'), False)


def _term():
    term_id = request.args.get('term') or current_term_id()
    return term_id
