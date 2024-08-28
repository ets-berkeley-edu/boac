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


class Student(Person):

    @property
    def academic_standings(self):
        return self.data['academic_standings']

    @academic_standings.setter
    def academic_standings(self, value):
        self.data['academic_standings'] = value

    @property
    def admit_data(self):
        return self.data['admit_data']

    @admit_data.setter
    def admit_data(self, value):
        self.data['admit_data'] = value

    @property
    def alert_count(self):
        return self.data['alert_count']

    @alert_count.setter
    def alert_count(self, value):
        self.data['alert_count'] = value

    @property
    def enrollment_data(self):
        return self.data['enrollment_terms']

    @enrollment_data.setter
    def enrollment_data(self, value):
        self.data['enrollment_terms'] = value

    @property
    def is_sir(self):
        return self.data['is_sir']

    @is_sir.setter
    def is_sir(self, value):
        self.data['is_sir'] = value

    @property
    def profile_data(self):
        return self.data['profile']

    @profile_data.setter
    def profile_data(self, value):
        self.data['profile'] = value
