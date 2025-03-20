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

from boac.merged import calnet
from boac.models.authorized_user import AuthorizedUser
from boac.models.json_cache import clear, stow
from boac.models.peer_advising_department_member import PeerAdvisingDepartmentMember
from boac.models.university_dept import UniversityDept
from flask import current_app as app
from flask_login import UserMixin


class UserSession(UserMixin):

    def __init__(self, user_id=None, flush_cached=False):
        try:
            # Type 'int' is required for user_id
            self.user_id = int(user_id) if user_id else None
        except ValueError:
            self.user_id = None
        if self.user_id:
            if flush_cached:
                self.flush_cached()
            self.api_json = self.load_user(self.user_id)
        else:
            self.api_json = self._get_api_json()

    def get_id(self):
        # Flask-login requires this method. Do NOT remove it.
        return self.user_id

    @property
    def can_access_admitted_students(self):
        return self.api_json['canAccessAdmittedStudents']

    @property
    def can_access_advising_data(self):
        return self.api_json['canAccessAdvisingData']

    @property
    def can_access_canvas_data(self):
        return self.api_json['canAccessCanvasData']

    @property
    def can_access_private_notes(self):
        return self.api_json['canAccessPrivateNotes']

    @property
    def can_edit_degree_progress(self):
        return self.api_json['canEditDegreeProgress']

    @property
    def can_read_degree_progress(self):
        return self.api_json['canReadDegreeProgress']

    @property
    def csid(self):
        return self.api_json.get('csid')

    @property
    def departments(self):
        return self.api_json['departments']

    @property
    def uid(self):
        return self.api_json['uid']

    def flush_cached(self):
        self.flush_cached_user_session(self.user_id)

    @property
    def in_demo_mode(self):
        return self.api_json['inDemoMode']

    @property
    def is_active(self):
        return self.api_json['isActive']

    @property
    def is_admin(self):
        return self.api_json['isAdmin']

    @property
    def is_anonymous(self):
        return not self.api_json['isAnonymous']

    @property
    def is_authenticated(self):
        return self.api_json['isAuthenticated']

    @property
    def same_day_advisor_departments(self):
        return self.api_json['sameDayAdvisorStatus']

    def to_api_json(self):
        return self.api_json

    @classmethod
    def flush_cached_user_session(cls, user_id):
        clear(f'boa_user_session_{user_id}')

    @classmethod
    @stow('boa_user_session_{user_id}')
    def load_user(cls, user_id):
        return cls._get_api_json(user=AuthorizedUser.find_by_id(user_id))

    @classmethod
    def _get_api_json(cls, user=None):
        calnet_profile = None
        departments = []
        is_active = False
        is_admin = False
        if user:
            calnet_profile = calnet.get_calnet_user_for_uid(
                app,
                user.uid,
                force_feed=False,
                skip_expired_users=True,
            )
            for m in user.department_memberships:
                departments.append({
                    **m.university_dept.to_api_json(),
                    'memberships': [
                        {
                            'automateMembership': m.automate_membership,
                            'role': m.role,
                        },
                    ],
                })
            for m in PeerAdvisingDepartmentMember.find_peer_advising_memberships_by_user_id(authorized_user_id=user.id):
                peer_advising_dept_membership = {
                    'role': m['role_type'],
                    'peerAdvisingDepartmentId': m['peer_advising_department_id'],
                    'peerAdvisingDepartmentName': m['peer_advising_department_name'],
                }
                university_dept_id = m['university_dept_id']
                university_dept_api_json = next((d for d in departments if d['id'] == university_dept_id), None)
                if university_dept_api_json:
                    # If the university_dept was added in the 'for user.department_memberships' loop above
                    # then we append the peer_advising membership to the existing object.
                    university_dept_api_json['memberships'].append(peer_advising_dept_membership)
                else:
                    departments.append({
                        **UniversityDept.find_by_id(university_dept_id).to_api_json(),
                        'memberships': [peer_advising_dept_membership],
                    })

            if not calnet_profile:
                is_active = False
            elif user.is_admin:
                is_admin = True
                is_active = True
            else:
                for d in departments:
                    is_active = bool(d['memberships'])
                    if is_active:
                        break

        degree_progress_permission = 'read_write' if is_admin else (user and user.degree_progress_permission)
        can_access_ce3_features = user and (user.is_admin or 'ZCEEE' in [d['deptCode'] for d in departments])

        return {
            **(calnet_profile or {}),
            **{
                'id': user and user.id,
                'automateDegreeProgressPermission': user.automate_degree_progress_permission if user else False,
                'canAccessAdmittedStudents': can_access_ce3_features,
                'canAccessAdvisingData': user.can_access_advising_data if user else False,
                'canAccessCanvasData': user.can_access_canvas_data if user else False,
                'canAccessPrivateNotes': can_access_ce3_features,
                'canEditDegreeProgress': degree_progress_permission == 'read_write',
                'canReadDegreeProgress': degree_progress_permission in ['read', 'read_write'],
                'degreeProgressPermission': degree_progress_permission,
                'deletedAt': user and user.deleted_at,
                'departments': departments,
                'inDemoMode': user.in_demo_mode if user else False,
                'isActive': is_active,
                'isAdmin': is_admin,
                'isAnonymous': not is_active,
                'isAuthenticated': is_active,
                'isBlocked': user and user.is_blocked,
                'uid': user and user.uid,
            },
        }
