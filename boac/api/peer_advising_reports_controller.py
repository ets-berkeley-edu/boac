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

from datetime import datetime
import re

from boac.api.auth_utils import is_authorized_peer_advisor_manager
from boac.api.decorators import peer_advisor_manager_required
from boac.api.errors import ResourceNotFoundError
from boac.lib.http import response_with_csv_download, tolerant_jsonify
from boac.merged.peer_advising_notes_reports import get_all_peer_advising_notes, get_notes_created_by_peer_advisors, \
    get_peer_advising_note_author_count, get_peer_advising_note_count_since, get_peer_advising_note_template_usage, \
    get_total_peer_advising_notes
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from flask import current_app as app
from flask_login import current_user


@app.route('/api/peer_advising/<peer_advising_department_id>/notes/csv', methods=['POST'])
@peer_advisor_manager_required
def get_peer_advising_csv_download(peer_advising_department_id):
    if PeerAdvisingDepartmentMember.is_user_in_peer_advising_department(
        peer_advising_department_id=peer_advising_department_id,
        user_id=current_user.get_id(),
    ):
        rows = []
        for row in get_all_peer_advising_notes(peer_advising_department_id=peer_advising_department_id):
            # Line breaks in CSV cause problems
            body = (row['body'] or '').replace('\n', ' ').replace('\r', ' ').strip()
            body = re.sub(r'\s+', ' ', body)
            row['body'] = body
            rows.append(row)
        return response_with_csv_download(
            rows=sorted(rows, key=lambda row: row['created_at'], reverse=True),
            filename_prefix='boa_peer_advising_notes',
            fieldnames=[
                'author_name',
                'author_uid',
                'author_role',
                'author_dept_codes',
                'body',
                'contact_type',
                'peer_advising_department_name',
                'sid',
                'student_first_name',
                'student_last_name',
                'topics',
                'created_at',
                'updated_at',
            ],
        )
    else:
        return app.login_manager.unauthorized()


@app.route('/api/peer_advising/<peer_advising_department_id>/report/notes')
@peer_advisor_manager_required
def peer_advising_notes_report(peer_advising_department_id):
    peer_advising_department = PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)
    if not peer_advising_department:
        raise ResourceNotFoundError('Peer Advising department not found')
    if current_user.is_admin or is_authorized_peer_advisor_manager(
        peer_advising_department_id=peer_advising_department.id,
        peer_advisor_manager_user_id=current_user.get_id(),
    ):
        today = datetime.today()
        timeframe_month = f"{today.year}-{f'0{today.month}' if today.month < 10 else today.month}"
        return tolerant_jsonify({
            'currentMonth': {
                'label': f"{today.strftime('%b')} {today.strftime('%Y')}",
                'month': today.month,
                'noteCount': get_peer_advising_note_count_since(
                    peer_advising_department_id=peer_advising_department.id,
                    timeframe_month=timeframe_month,
                ),
                'peerAdvisingDepartmentId': int(peer_advising_department_id),
                'peerAdvisors': _peer_advisors_with_note_counts(
                    peer_advising_department_id=peer_advising_department.id,
                    timeframe_month=timeframe_month,
                ),
                'year': today.year,
            },
            'distinctPeerAdvisorAuthors': get_peer_advising_note_author_count(peer_advising_department.id),
            'noteTemplates': get_peer_advising_note_template_usage(peer_advising_department.id),
            'peerAdvisingDepartment': peer_advising_department.to_api_json(),
            'totalPeerAdvisingNoteCount': get_total_peer_advising_notes(peer_advising_department.id),
        })
    else:
        return app.login_manager.unauthorized()


@app.route('/api/peer_advising/<peer_advising_department_id>/report/historical')
@peer_advisor_manager_required
def peer_advising_historical_report(peer_advising_department_id):
    peer_advising_department = PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)
    if not peer_advising_department:
        raise ResourceNotFoundError('Peer Advising department not found')
    if current_user.is_admin or is_authorized_peer_advisor_manager(
        peer_advising_department_id=peer_advising_department.id,
        peer_advisor_manager_user_id=current_user.get_id(),
    ):
        return tolerant_jsonify(_historical_peer_advisors_with_note_counts(
            peer_advising_department_id=peer_advising_department.id,
        ))
    else:
        return app.login_manager.unauthorized()


def _historical_peer_advisors_with_note_counts(peer_advising_department_id):
    years_json = []
    today = datetime.today()
    for row in get_notes_created_by_peer_advisors(peer_advising_department_id=peer_advising_department_id):
        created_at = row['created_at']
        is_historical = created_at.year != today.year or created_at.month != today.month
        if is_historical:
            year_json = next((y for y in years_json if y['year'] == created_at.year), None)
            if not year_json:
                year_json = {
                    'year': created_at.year,
                    'label': created_at.year,
                    'months': [],
                }
                years_json.append(year_json)
            month_json = next((m for m in year_json['months'] if m['month'] == created_at.month), None)
            if not month_json:
                month_json = {
                    'label': f"{created_at.strftime('%b')} {created_at.strftime('%Y')}",
                    'month': created_at.month,
                    'noteCount': 0,
                    'peerAdvisors': [],
                    'year': created_at.year,
                }
                year_json['months'].append(month_json)
            uid = row['author_uid']
            peer_advisor = next((p for p in month_json['peerAdvisors'] if p['uid'] == uid), None)
            if not peer_advisor:
                peer_advisor = {
                    'name': row['author_name'],
                    'noteCount': 0,
                    'uid': uid,
                }
                month_json['peerAdvisors'].append(peer_advisor)
            peer_advisor['noteCount'] = peer_advisor['noteCount'] + 1
            month_json['noteCount'] = month_json['noteCount'] + 1
    # Next, sort in reverse chronological.
    years_json = sorted(years_json, key=lambda y: y['year'], reverse=True)
    for year in years_json:
        year['months'] = sorted(year['months'], key=lambda m: m['month'], reverse=True)
    return years_json


def _peer_advisors_with_note_counts(peer_advising_department_id, timeframe_month):
    peer_advisors = []
    for row in get_notes_created_by_peer_advisors(
        peer_advising_department_id=peer_advising_department_id,
        timeframe_month=timeframe_month,
    ):
        uid = row['author_uid']
        peer_advisor = next((p for p in peer_advisors if p['uid'] == uid), None)
        if not peer_advisor:
            peer_advisor = {
                'name': row['author_name'],
                'noteCount': 0,
                'uid': uid,
            }
            peer_advisors.append(peer_advisor)
        peer_advisor['noteCount'] = peer_advisor['noteCount'] + 1
    return peer_advisors
