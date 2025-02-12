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


class DegreeReqtCategory(object):

    def __init__(self, data):
        self.data = data

    @property
    def category_id(self):
        return self.data.get('category_id')

    @category_id.setter
    def category_id(self, value):
        self.data['category_id'] = value

    @property
    def column_num(self):
        if self.parent:
            return self.parent.column_num
        else:
            return self.data.get('column_num')

    @column_num.setter
    def column_num(self, value):
        self.data['column_num'] = value

    @property
    def course_reqts(self):
        return self.data.get('course_reqts') or []

    @course_reqts.setter
    def course_reqts(self, value):
        self.data['course_reqts'] = value

    @property
    def desc(self):
        return self.data.get('desc')

    @desc.setter
    def desc(self, value):
        self.data['desc'] = value

    @property
    def name(self):
        return self.data.get('name')

    @name.setter
    def name(self, value):
        self.data['name'] = value

    @property
    def parent(self):
        return self.data.get('parent')

    @parent.setter
    def parent(self, value):
        self.data['parent'] = value

    @property
    def sub_categories(self):
        return self.data.get('sub_categories') or []

    @sub_categories.setter
    def sub_categories(self, value):
        self.data['sub_categories'] = value

    @property
    def unit_reqts(self):
        return self.data.get('unit_reqts') or []

    @unit_reqts.setter
    def unit_reqts(self, value):
        self.data['unit_reqts'] = value
