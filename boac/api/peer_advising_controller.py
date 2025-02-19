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

from boac.api.errors import ResourceNotFoundError
from boac.api.util import authorized_users_api_feed, peer_advisor_manager_required
from boac.lib.http import tolerant_jsonify
from boac.models.authorized_user import AuthorizedUser
from boac.models.peer_advising_department import PeerAdvisingDepartment
from dateutil.tz import tzutc
from flask import current_app as app, request


@app.route('/api/peer/department/<peer_advising_department_id>')
@peer_advisor_manager_required
def get_peer_advising_department(peer_advising_department_id):
    include_deleted = request.args.get('includeDeleted', False)
    peer_advising_department = PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)
    if peer_advising_department:
        users = AuthorizedUser.get_peer_advising_users(peer_advising_department_id=peer_advising_department_id)
        if include_deleted:
            users = users + AuthorizedUser.get_peer_advising_users(
                peer_advising_department_id=peer_advising_department_id,
                status='deleted',
            )
        users = sorted([user for user in authorized_users_api_feed(users)], key=lambda u: u['lastName'])
        api_json = {
            **peer_advising_department.to_api_json(),
            **{'peerAdvisingDepartmentMembers': users},
        }
        return tolerant_jsonify(api_json)
    else:
        raise ResourceNotFoundError('Peer Advising Department not found.')


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
