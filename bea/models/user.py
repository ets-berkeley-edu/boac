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


class User(object):

    def __init__(self, data):
        self.data = data

    @property
    def uid(self):
        return self.data['uid']

    @uid.setter
    def uid(self, value):
        self.data['uid'] = value

    @property
    def active(self):
        return self.data['active']

    @active.setter
    def active(self, value):
        self.data['active'] = value

    @property
    def alert_count(self):
        return self.data['alert_count']

    @alert_count.setter
    def alert_count(self, value):
        self.data['alert_count'] = value

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
    def email(self):
        return self.data['email']

    @email.setter
    def email(self, value):
        self.data['email'] = value

    @property
    def first_name(self):
        return self.data['first_name']

    @first_name.setter
    def first_name(self, value):
        self.data['first_name'] = value

    @property
    def full_name(self):
        return self.data['full_name']

    @full_name.setter
    def full_name(self, value):
        self.data['full_name'] = value

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
    def is_sir(self):
        return self.data['is_sir']

    @is_sir.setter
    def is_sir(self, value):
        self.data['is_sir'] = value

    @property
    def last_name(self):
        return self.data['last_name']

    @last_name.setter
    def last_name(self, value):
        self.data['last_name'] = value

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
    def sid(self):
        return self.data['sid']

    @sid.setter
    def sid(self, value):
        self.data['sid'] = value

    @property
    def status(self):
        return self.data['status']

    @status.setter
    def status(self, value):
        self.data['status'] = value

    @property
    def username(self):
        return self.data['username']

    @username.setter
    def username(self, value):
        self.data['username'] = value
