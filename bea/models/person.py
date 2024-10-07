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


class Person(object):

    def __init__(self, data):
        self.data = data

    @property
    def uid(self):
        return self.data.get('uid')

    @uid.setter
    def uid(self, value):
        self.data['uid'] = value

    @property
    def active(self):
        return self.data.get('active')

    @active.setter
    def active(self, value):
        self.data['active'] = value

    @property
    def email(self):
        return self.data.get('email')

    @email.setter
    def email(self, value):
        self.data['email'] = value

    @property
    def first_name(self):
        return self.data.get('first_name')

    @first_name.setter
    def first_name(self, value):
        self.data['first_name'] = value

    @property
    def full_name(self):
        return self.data.get('full_name')

    @full_name.setter
    def full_name(self, value):
        self.data['full_name'] = value

    @property
    def last_name(self):
        return self.data.get('last_name')

    @last_name.setter
    def last_name(self, value):
        self.data['last_name'] = value

    @property
    def middle_name(self):
        return self.data.get('middle_name')

    @middle_name.setter
    def middle_name(self, value):
        self.data['middle_name'] = value

    @property
    def sid(self):
        return self.data.get('sid')

    @sid.setter
    def sid(self, value):
        self.data['sid'] = value

    @property
    def status(self):
        return self.data.get('status')

    @status.setter
    def status(self, value):
        self.data['status'] = value
