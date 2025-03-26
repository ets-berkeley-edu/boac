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

from datetime import datetime, timedelta

from boac.api.auth_utils import is_authorized_peer_advisor_manager
from boac.api.decorators import peer_advisor_manager_required
from boac.api.errors import ResourceNotFoundError
from boac.lib.http import tolerant_jsonify
from boac.merged.peer_advising_notes_reports import get_notes_created_by_peer_advisors, \
    get_peer_advising_note_author_count, get_peer_advising_note_count_since, get_peer_advising_note_template_usage, \
    get_total_peer_advising_notes
from boac.models.peer_advising_department import PeerAdvisingDepartment
from dateutil.tz import tzutc
from flask import current_app as app
from flask_login import current_user


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
        start_of_month = datetime(today.year, today.month, 1, 0, 0, tzinfo=tzutc())
        return tolerant_jsonify({
            'currentMonth': {
                'label': f"{start_of_month.strftime('%b')} {start_of_month.strftime('%Y')}",
                'peerAdvisingDepartmentId': int(peer_advising_department_id),
                'peerAdvisingNoteCount': get_peer_advising_note_count_since(
                    peer_advising_department_id=peer_advising_department.id,
                    since_datetime=start_of_month,
                ),
                'peerAdvisors': _peer_advisors_with_note_counts(
                    peer_advising_department_id=peer_advising_department.id,
                    from_created_at=start_of_month,
                ),
            },
            'historical': {
                'years': _historical_peer_advisors_with_note_counts(
                    peer_advising_department_id=peer_advising_department.id,
                    to_created_at=start_of_month - timedelta(milliseconds=1),
                ),
            },
            'distinctPeerAdvisorAuthors': get_peer_advising_note_author_count(peer_advising_department.id),
            'noteTemplates': get_peer_advising_note_template_usage(peer_advising_department.id),
            'peerAdvisingDepartment': peer_advising_department.to_api_json(),
            'totalPeerAdvisingNoteCount': get_total_peer_advising_notes(peer_advising_department.id),
        })
    else:
        return app.login_manager.unauthorized()


def _historical_peer_advisors_with_note_counts(peer_advising_department_id, to_created_at):
    years_json = []
    for row in get_notes_created_by_peer_advisors(
        peer_advising_department_id=peer_advising_department_id,
        to_created_at=to_created_at,
    ):
        created_at = datetime.fromisoformat(row['note_created_at'].replace('Z', '+00:00'))
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
                'month': created_at.month,
                'label': created_at.month,
                'peerAdvisors': [],
            }
        user_id = row['id']
        peer_advisor = next((p for p in month_json['peerAdvisors'] if p['id'] == user_id), None)
        if not peer_advisor:
            peer_advisor = {
                'id': row['user_id'],
                'name': row['note_author_name'],
                'uid': row['uid'],
                'noteCount': 0,
            }
            month_json['peerAdvisors'].append(peer_advisor)
        peer_advisor['noteCount'] = peer_advisor['noteCount'] + 1
    return years_json


def _peer_advisors_with_note_counts(peer_advising_department_id, from_created_at):
    peer_advisors = []
    for row in get_notes_created_by_peer_advisors(
        peer_advising_department_id=peer_advising_department_id,
        from_created_at=from_created_at,
    ):
        user_id = row['user_id']
        peer_advisor = next((p for p in peer_advisors if p['id'] == user_id), None)
        if not peer_advisor:
            peer_advisor = {
                'id': user_id,
                'name': row['note_author_name'],
                'uid': row['uid'],
                'noteCount': 0,
            }
            peer_advisors.append(peer_advisor)
        peer_advisor['noteCount'] = peer_advisor['noteCount'] + 1
    return peer_advisors
