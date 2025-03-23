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
from boac.api.decorators import peer_advisor_manager_required, peer_advisor_required
from boac.api.errors import ResourceNotFoundError
from boac.api.util import authorized_users_api_feed
from boac.externals import data_loch
from boac.lib.http import tolerant_jsonify
from boac.lib.util import to_bool_or_none
from boac.models.authorized_user import AuthorizedUser
from boac.models.note import Note
from boac.models.peer_advising_department import PeerAdvisingDepartment
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from flask import current_app as app, request
from flask_login import current_user


@app.route('/api/peer_advising/create_peer_advisor', methods=['POST'])
@peer_advisor_manager_required
def create_peer_advisor():
    params = request.get_json()
    peer_advising_department_id = params.get('peerAdvisingDeptId')
    uid = params.get('uid')
    if is_authorized_peer_advisor_manager(
            peer_advising_department_id=peer_advising_department_id,
            peer_advisor_manager_user_id=current_user.get_id(),
    ):
        peer_advisor = AuthorizedUser.create_or_restore(
            uid,
            automate_degree_progress_permission=False,
            can_access_advising_data=False,
            can_access_canvas_data=False,
            created_by=current_user.uid,
            degree_progress_permission=None,
        )
        PeerAdvisingDepartmentMember.create_or_update_membership(
            authorized_user_id=peer_advisor.id,
            peer_advising_department_id=peer_advising_department_id,
            role_type='peer_advisor',
        )
        api_json = authorized_users_api_feed([peer_advisor])[0]
        return tolerant_jsonify(api_json)
    else:
        return app.login_manager.unauthorized()


@app.route('/api/peer_advising/department/<peer_advising_department_id>/<role_type>')
@peer_advisor_manager_required
def get_peer_advising_department(peer_advising_department_id, role_type):
    include_deleted = request.args.get('includeDeleted', False)
    include_note_counts = to_bool_or_none(request.args.get('includeNoteCounts')) or False
    peer_advising_department = PeerAdvisingDepartment.get_department_by_id(peer_advising_department_id)
    if peer_advising_department:
        university_dept = UniversityDept.find_by_id(peer_advising_department.university_dept_id)
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
        if include_note_counts:
            note_counts_per_uid = Note.get_note_counts_per_uid([u['uid'] for u in users])
            for user in users:
                user['noteCount'] = note_counts_per_uid.get(user['uid'], 0)
        users = sorted([{**user, **{'role': role_type}} for user in users], key=lambda u: u['lastName'])
        api_json = {
            **peer_advising_department.to_api_json(),
            **{
                'peerAdvisingDepartmentMembers': users,
                'universityDeptCode': university_dept.dept_code,
                'universityDeptName': university_dept.dept_name,
            },
        }
        return tolerant_jsonify(api_json)
    else:
        raise ResourceNotFoundError('Peer Advising Department not found.')


@app.route('/api/peer_advising/student/<sid>')
@peer_advisor_required
def get_basic_student(sid):
    students = data_loch.get_basic_student_data([sid])
    if len(students) == 1:
        student = students[0]
        return tolerant_jsonify({
            'firstName': student['first_name'],
            'lastName': student['last_name'],
            'sid': student['sid'],
            'uid': student['uid'],
        })
    else:
        raise ResourceNotFoundError('Student not found.')


@app.route('/api/peer_advising/delete_peer_advisor/<peer_advising_department_id>/<peer_advisor_user_id>', methods=['DELETE'])
@peer_advisor_manager_required
def delete_peer_advisor(peer_advising_department_id, peer_advisor_user_id):
    if current_user.is_admin or is_authorized_peer_advisor_manager(
            peer_advising_department_id=peer_advising_department_id,
            peer_advisor_manager_user_id=current_user.get_id(),
            peer_advisor_user_id=int(peer_advisor_user_id),
    ):
        PeerAdvisingDepartmentMember.delete_membership(
            authorized_user_id=int(peer_advisor_user_id),
            peer_advising_department_id=peer_advising_department_id,
        )
        uid = AuthorizedUser.get_uid_per_id(peer_advisor_user_id)
        AuthorizedUser.delete(uid)
        return tolerant_jsonify({'message': f'Peer Advisor UID {uid} deleted'}), 200
    else:
        return app.login_manager.unauthorized()


@app.route('/api/peer_advising/restore_peer_advisor/<peer_advising_department_id>/<peer_advisor_user_id>')
@peer_advisor_manager_required
def restore_peer_advisor(peer_advising_department_id, peer_advisor_user_id):
    peer_advisor_user_id = int(peer_advisor_user_id)
    if current_user.is_admin or is_authorized_peer_advisor_manager(
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
        AuthorizedUser.create_or_restore(
            created_by=current_user.get_id(),
            is_blocked=False,
            uid=uid,
        )
        return tolerant_jsonify({})
    else:
        return app.login_manager.unauthorized()
