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
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from dateutil.tz import tzutc
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/peer/department/<peer_advising_department_id>/<role_type>')
@peer_advisor_manager_required
def get_peer_advising_department(peer_advising_department_id, role_type):
    include_deleted = request.args.get('includeDeleted', False)
    peer_advising_department = PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)
    if peer_advising_department:
        users = AuthorizedUser.get_peer_advising_users(
            peer_advising_department_id=peer_advising_department_id,
            role_type=role_type,
        )
        if include_deleted:
            users = users + AuthorizedUser.get_peer_advising_users(
                peer_advising_department_id=peer_advising_department_id,
                role_type=role_type,
                status='deleted',
            )
        users = authorized_users_api_feed(users)
        users = sorted([{**user, **{'role': role_type}} for user in users], key=lambda u: u['lastName'])
        api_json = {
            **peer_advising_department.to_api_json(),
            **{'peerAdvisingDepartmentMembers': users},
        }
        return tolerant_jsonify(api_json)
    else:
        raise ResourceNotFoundError('Peer Advising Department not found.')


@app.route('/api/peer/delete_peer_advisor/<peer_advising_department_id>/<peer_advisor_user_id>', methods=['DELETE'])
@peer_advisor_manager_required
def delete_peer_advisor(peer_advising_department_id, peer_advisor_user_id):
    if _is_authorized_peer_advisor_manager(
            peer_advising_department_id=peer_advising_department_id,
            peer_advisor_manager_user_id=current_user.get_id(),
            peer_advisor_user_id=peer_advisor_user_id,
    ):
        PeerAdvisingDepartmentMember.delete_membership(
            authorized_user_id=peer_advisor_user_id,
            peer_advising_department_id=peer_advising_department_id,
        )
        uid = AuthorizedUser.get_uid_per_id(peer_advisor_user_id)
        AuthorizedUser.delete(uid)
        return tolerant_jsonify({'message': f'Peer Advisor UID {uid} deleted'}), 200
    else:
        return app.login_manager.unauthorized()


@app.route('/api/peer/restore_peer_advisor/<peer_advising_department_id>/<peer_advisor_user_id>')
@peer_advisor_manager_required
def restore_peer_advisor(peer_advising_department_id, peer_advisor_user_id):
    if _is_authorized_peer_advisor_manager(
        include_deleted_peer_advisor_memberships=True,
        peer_advising_department_id=peer_advising_department_id,
        peer_advisor_manager_user_id=current_user.get_id(),
        peer_advisor_user_id=peer_advisor_user_id,
    ):
        PeerAdvisingDepartmentMember.restore_membership(
            authorized_user_id=peer_advisor_user_id,
            peer_advising_department_id=peer_advising_department_id,
        )
        uid = AuthorizedUser.get_uid_per_id(peer_advisor_user_id, include_deleted=True)
        AuthorizedUser.create_or_restore(uid, created_by=current_user.get_id())
        return tolerant_jsonify({})
    else:
        return app.login_manager.unauthorized()


def _is_authorized_peer_advisor_manager(
        peer_advising_department_id,
        peer_advisor_manager_user_id,
        peer_advisor_user_id,
        include_deleted_peer_advisor_memberships=False,
):
    def _is_authorized(membership, role_type):
        has_valid_role = membership['role_type'] == role_type
        return has_valid_role and membership['peer_advising_department_id'] == int(peer_advising_department_id)
    peer_advisor_manager_memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
        authorized_user_id=peer_advisor_manager_user_id,
    )
    peer_advisor_memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
        authorized_user_id=peer_advisor_user_id,
        include_deleted=include_deleted_peer_advisor_memberships,
    )
    authorization_checks = [
        next((m for m in peer_advisor_manager_memberships if _is_authorized(m, 'peer_advisor_manager')), None) is not None,
        next((m for m in peer_advisor_memberships if _is_authorized(m, 'peer_advisor')), None) is not None,
        (peer_advisor_manager_user_id != peer_advisor_user_id),
    ]
    return all(authorization_checks)


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
