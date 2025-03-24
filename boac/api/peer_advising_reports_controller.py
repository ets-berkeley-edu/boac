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

from boac.api.auth_utils import is_authorized_peer_advisor_manager
from boac.api.decorators import peer_advisor_manager_required
from boac.api.errors import ResourceNotFoundError
from boac.lib.http import tolerant_jsonify
from boac.models.peer_advising_department import PeerAdvisingDepartment
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
        return tolerant_jsonify({
            'currentMonth': {
                'month': 'May',
                'peerAdvisingNoteCount': 17,
                'peerAdvisors': [
                    {'userId': 1, 'name': 'Patsy Simmons', 'noteCount': 2},
                    {'userId': 2, 'name': 'Max Townsend', 'noteCount': 1},
                    {'userId': 3, 'name': 'Lance Wright', 'noteCount': 5},
                    {'userId': 4, 'name': 'Kirk Holloway', 'noteCount': 9},
                ],
                'year': 2024,
            },
            'distinctPeerAdvisorAuthors': 26,
            'noteTemplates': [
                {'name': 'Change of Major', 'usageCount': 11},
                {'name': 'Declaring a Major', 'usageCount': 7},
                {'name': 'Units Exception', 'usageCount': 3},
                {'name': 'Graduation Planning', 'usageCount': 0},
            ],
            'peerAdvisingDepartment': peer_advising_department.to_api_json(),
            'totalPeerAdvisingNoteCount': 436,
        })
    else:
        return app.login_manager.unauthorized()
