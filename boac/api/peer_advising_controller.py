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

from datetime import datetime
from random import randrange

from boac.api.util import peer_advising_manager_required
from boac.lib.http import tolerant_jsonify
from dateutil.tz import tzutc
from flask import current_app as app


@app.route('/api/peer/department/<peer_advising_department_id>')
@peer_advising_manager_required
def get_peer_advising_department(peer_advising_department_id):
    mock_names = [
        'Amelia Cortez',
        'Cecil Copeland',
        'Kirk Holloway',
        'Lance Wright',
        'Lila Caldwell',
        'Max Townsend',
        'Patricia Dunn',
        'Patsy Simmons',
    ]
    members = []
    for index, mock_name in enumerate(mock_names):
        # TODO: Use approach similar to the '/api/users' API which leverages 'authorized_users_api_feed(...)'.
        members.append({
            'authorizedUserId': index,
            'createdAt': _isoformat(datetime.now()),
            'name': mock_name,
            'notesCreatedCount': randrange(10),
            'roleType': 'peer_advisor',
            'updatedAt': _isoformat(datetime.now()),
        })
    return tolerant_jsonify({
        'id': peer_advising_department_id,
        'createdAt': _isoformat(datetime.now()),
        'name': 'Your Peer Advising Department',
        'members': members,
        'universityDeptId': 1,
        'updatedAt': _isoformat(datetime.now()),
    })


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
