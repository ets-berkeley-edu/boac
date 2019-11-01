"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, get_dept_role
from boac.merged import calnet
from boac.models.authorized_user import AuthorizedUser
from boac.models.json_cache import clear, stow
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

    def flush_cached(self):
        clear(f'boa_user_session_{self.user_id}')

    def get_id(self):
        return self.user_id

    def get_uid(self):
        return self.api_json['uid']

    def get_csid(self):
        return self.api_json.get('csid')

    @property
    def is_active(self):
        return self.api_json['isActive']

    @property
    def is_authenticated(self):
        return self.api_json['isAuthenticated']

    @property
    def is_anonymous(self):
        return not self.api_json['isAnonymous']

    @property
    def is_drop_in_advisor(self):
        if self.api_json['dropInAdvisorStatus']:
            return True
        else:
            return False

    @property
    def departments(self):
        return self.api_json['departments']

    @property
    def drop_in_advisor_departments(self):
        return self.api_json['dropInAdvisorStatus']

    @property
    def is_admin(self):
        return self.api_json['isAdmin']

    @property
    def in_demo_mode(self):
        return self.api_json['inDemoMode']

    @property
    def can_access_canvas_data(self):
        return self.api_json['canAccessCanvasData']

    def to_api_json(self):
        return self.api_json

    @classmethod
    @stow('boa_user_session_{user_id}')
    def load_user(cls, user_id):
        return cls._get_api_json(user=AuthorizedUser.find_by_id(user_id))

    @classmethod
    def _get_api_json(cls, user=None):
        calnet_profile = None
        departments = []
        if user:
            calnet_profile = calnet.get_calnet_user_for_uid(
                app,
                user.uid,
                force_feed=False,
                skip_expired_users=True,
            )
            for m in user.department_memberships:
                dept_code = m.university_dept.dept_code
                departments.append(
                    {
                        'code': dept_code,
                        'name': BERKELEY_DEPT_CODE_TO_NAME.get(dept_code, dept_code),
                        'role': get_dept_role(m),
                        'isAdvisor': m.is_advisor,
                        'isDirector': m.is_director,
                        'isScheduler': m.is_scheduler,
                    })
        is_active = False
        if user:
            if not calnet_profile:
                is_active = False
            elif user.is_admin:
                is_active = True
            elif len(user.department_memberships):
                for m in user.department_memberships:
                    is_active = m.is_advisor or m.is_director or m.is_scheduler
                    if is_active:
                        break
        is_admin = user and user.is_admin
        drop_in_advisor_status = []
        if user and len(user.drop_in_departments):
            drop_in_advisor_status = [d.to_api_json() for d in user.drop_in_departments]
        return {
            **(calnet_profile or {}),
            **{
                'id': user and user.id,
                'departments': departments,
                'isActive': is_active,
                'isAdmin': is_admin,
                'isAnonymous': not is_active,
                'isAuthenticated': is_active,
                'inDemoMode': user and user.in_demo_mode,
                'canAccessCanvasData': user and user.can_access_canvas_data,
                'uid': user and user.uid,
                'dropInAdvisorStatus': drop_in_advisor_status,
            },
        }
