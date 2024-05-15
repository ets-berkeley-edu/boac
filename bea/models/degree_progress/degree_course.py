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


class DegreeCourse(object):

    def __init__(self, data):
        self.data = data

    @property
    def course_id(self):
        return self.data['course_id']

    @course_id.setter
    def course_id(self, value):
        self.data['course_id'] = value

    @property
    def color(self):
        return self.data['color']

    @color.setter
    def color(self, value):
        self.data['color'] = value

    @property
    def column_num(self):
        return self.data['column_num']

    @column_num.setter
    def column_num(self, value):
        self.data['column_num'] = value

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, value):
        self.data['name'] = value

    @property
    def transfer_course(self):
        return self.data['transfer_course']

    @transfer_course.setter
    def transfer_course(self, value):
        self.data['transfer_course'] = value

    @property
    def units(self):
        return self.data['units']

    @units.setter
    def units(self, value):
        self.data['units'] = value

    @property
    def units_reqts(self):
        return self.data['units_reqts']

    @units_reqts.setter
    def units_reqts(self, value):
        self.data['units_reqts'] = value
