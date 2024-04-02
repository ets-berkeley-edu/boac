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


class Cohort(object):

    def __init__(self, data):
        self.data = data

    @property
    def cohort_id(self):
        return self.data['cohort_id']

    @cohort_id.setter
    def cohort_id(self, value):
        self.data['cohort_id'] = value

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, value):
        self.data['name'] = value

    @property
    def ce3(self):
        return self.data['ce3']

    @ce3.setter
    def ce3(self, value):
        self.data['ce3'] = value

    @property
    def owner_uid(self):
        return self.data['owner_uid']

    @owner_uid.setter
    def owner_uid(self, value):
        self.data['owner_uid'] = value

    @property
    def members(self):
        return self.data['members'] or []

    @members.setter
    def members(self, value):
        self.data['members'] = value
