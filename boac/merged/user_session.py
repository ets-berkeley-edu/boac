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

from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME, get_dept_codes, get_dept_role
from boac.merged import calnet
from flask import current_app as app
from flask_login import UserMixin


class UserSession(UserMixin):

    def __init__(self, authorized_user=None):
        self.user = authorized_user
        self.calnet_profile = None
        if self.user:
            self.calnet_profile = calnet.get_calnet_user_for_uid(
                app,
                self.user.uid,
                force_feed=False,
                skip_expired_users=True,
            )

    def get_id(self):
        return self.user and self.user.id

    def get_uid(self):
        return self.user and self.user.uid

    @property
    def is_active(self):
        active = False
        if self.user:
            if not self.calnet_profile:
                active = False
            elif self.user.is_admin:
                active = True
            elif len(self.user.department_memberships):
                for m in self.user.department_memberships:
                    active = m.is_advisor or m.is_director
                    if active:
                        break
        return active

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return not self.is_active

    @property
    def department_memberships(self):
        return self.user and self.user.department_memberships

    @property
    def is_admin(self):
        return self.user and self.user.is_admin

    @property
    def in_demo_mode(self):
        return self.user and self.user.in_demo_mode

    def to_api_json(self):
        departments = []
        if self.user:
            for m in self.user.department_memberships:
                dept_code = m.university_dept.dept_code
                departments.append(
                    {
                        'code': dept_code,
                        'name': BERKELEY_DEPT_CODE_TO_NAME[dept_code] or dept_code,
                        'role': get_dept_role(m),
                        'isAdvisor': m.is_advisor,
                        'isDirector': m.is_director,
                    })
        dept_codes = get_dept_codes(self.user) if self.user else []
        is_asc = 'UWASC' in dept_codes
        is_coe = 'COENG' in dept_codes
        return {
            **(self.calnet_profile or {}),
            **{
                'id': self.get_id(),
                'canViewAsc': is_asc or self.is_admin,
                'canViewCoe': is_coe or self.is_admin,
                'departments': departments,
                'isActive': self.is_active,
                'isAdmin': self.is_admin,
                'isAnonymous': self.is_anonymous,
                'isAsc': is_asc,
                'isAuthenticated': self.is_authenticated,
                'isCoe': is_coe,
                'inDemoMode': self.in_demo_mode,
                'uid': self.get_uid(),
            },
        }
