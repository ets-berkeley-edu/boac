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

from bea.models.person import Person


class User(Person):

    @property
    def can_access_advising_data(self):
        return self.data['can_access_advising_data']

    @can_access_advising_data.setter
    def can_access_advising_data(self, value):
        self.data['can_access_advising_data'] = value

    @property
    def can_access_canvas_data(self):
        return self.data['can_access_canvas_data']

    @can_access_canvas_data.setter
    def can_access_canvas_data(self, value):
        self.data['can_access_canvas_data'] = value

    @property
    def degree_progress_perm(self):
        return self.data['degree_progress_perm']

    @degree_progress_perm.setter
    def degree_progress_perm(self, value):
        self.data['degree_progress_perm'] = value

    @property
    def degree_progress_automated(self):
        return self.data['degree_progress_automated']

    @degree_progress_automated.setter
    def degree_progress_automated(self, value):
        self.data['degree_progress_automated'] = value

    @property
    def dept_memberships(self):
        return self.data['dept_memberships']

    @dept_memberships.setter
    def dept_memberships(self, value):
        self.data['dept_memberships'] = value

    @property
    def depts(self):
        return self.data['depts']

    @depts.setter
    def depts(self, value):
        self.data['depts'] = value

    @property
    def is_admin(self):
        return self.data['is_admin']

    @is_admin.setter
    def is_admin(self, value):
        self.data['is_admin'] = value

    @property
    def is_blocked(self):
        return self.data['is_blocked']

    @is_blocked.setter
    def is_blocked(self, value):
        self.data['is_blocked'] = value

    @property
    def role(self):
        return self.data['role']

    @role.setter
    def role(self, value):
        self.data['role'] = value

    @property
    def role_code(self):
        return self.data['role_code']

    @role_code.setter
    def role_code(self, value):
        self.data['role_code'] = value

    @property
    def username(self):
        return self.data['username']

    @username.setter
    def username(self, value):
        self.data['username'] = value
