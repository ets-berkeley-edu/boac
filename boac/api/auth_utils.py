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

from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember


def is_authorized_peer_advisor_manager(
        peer_advising_department_id,
        peer_advisor_manager_user_id,
        peer_advisor_user_id=None,
        include_deleted_peer_advisor_memberships=False,
):
    def _is_authorized(membership, role_type):
        has_valid_role = membership['role_type'] == role_type
        return has_valid_role and str(membership['peer_advising_department_id']) == str(peer_advising_department_id)
    peer_advisor_manager_memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
        authorized_user_id=peer_advisor_manager_user_id,
    )
    authorization_checks = [
        next((m for m in peer_advisor_manager_memberships if _is_authorized(m, 'peer_advisor_manager')), None) is not None,
        (peer_advisor_manager_user_id != peer_advisor_user_id),
    ]
    if peer_advisor_user_id:
        peer_advisor_memberships = PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(
            authorized_user_id=peer_advisor_user_id,
            include_deleted=include_deleted_peer_advisor_memberships,
        )
        authorization_checks.append(next((m for m in peer_advisor_memberships if _is_authorized(m, 'peer_advisor')), None) is not None)
    return all(authorization_checks)
