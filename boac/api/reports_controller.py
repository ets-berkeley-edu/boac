"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from datetime import timedelta
import re

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import admin_or_director_required, admin_required, authorized_users_api_feed
from boac.externals.data_loch import get_asc_advising_note_count, get_e_and_i_advising_note_count, get_sis_advising_note_count
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, term_name_for_sis_id
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.lib.util import localized_timestamp_to_utc, utc_now
from boac.merged.reports import get_boa_note_count_by_month, get_note_author_count, get_note_count, get_note_count_per_user,\
    get_note_with_attachments_count, get_note_with_topics_count, get_summary_of_boa_notes, low_assignment_scores
from boac.merged.sis_terms import current_term_id
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from boac.models.university_dept_member import UniversityDeptMember
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/reports/download_alerts_csv', methods=['POST'])
@admin_required
def alerts_log_export():
    def _param_to_utc_date(key):
        value = (params.get(key) or '').strip()
        return localized_timestamp_to_utc(value, date_format='%m/%d/%Y') if value else None

    params = request.get_json()
    from_date_utc = _param_to_utc_date('fromDate')
    to_date_utc = _param_to_utc_date('toDate') + timedelta(days=1)
    if from_date_utc and to_date_utc:
        def _to_api_json(alert):
            term_id_match = re.search(r'^2[012]\d[0258]', alert.key[0:4])
            active_until = alert.deleted_at or utc_now()
            return {
                'sid': alert.sid,
                'term': term_name_for_sis_id(term_id_match.string) if term_id_match else None,
                'key': alert.key,
                'type': alert.alert_type,
                'is_active': not alert.deleted_at,
                'active_duration_hours': round((active_until - alert.created_at).total_seconds() / 3600),
                'created_at': alert.created_at,
                'deleted_at': alert.deleted_at,
            }
        alerts = Alert.get_alerts_per_date_range(from_date_utc, to_date_utc)
        return response_with_csv_download(
            rows=[_to_api_json(a) for a in alerts],
            filename_prefix='alerts_log',
            fieldnames=['sid', 'term', 'key', 'type', 'is_active', 'active_duration_hours', 'created_at', 'deleted_at'],
        )
    else:
        raise BadRequestError('Invalid arguments')


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
            'author_uid',
            'author_name',
            'author_role',
            'author_dept_codes',
            'sid',
            'subject',
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
            return tolerant_jsonify({
                'asc': get_asc_advising_note_count(),
                'ei': get_e_and_i_advising_note_count(),
                'sis': get_sis_advising_note_count(),
                'boa': {
                    'total': total_note_count,
                    'authors': get_note_author_count(),
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
