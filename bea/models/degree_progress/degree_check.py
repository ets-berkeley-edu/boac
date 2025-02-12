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
import copy

from bea.models.degree_progress.degree_check_template import DegreeCheckTemplate


class DegreeCheck(DegreeCheckTemplate):

    def __init__(self, data, template, student):
        super().__init__(data)
        self.template = template
        self.categories = copy.deepcopy(self.template.categories)
        self.completed_courses = []
        self.name = copy.deepcopy(self.template.name)
        self.student = student
        self.unit_reqts = copy.deepcopy(self.template.unit_reqts)

        for req in self.unit_reqts:
            req.units_completed = 0

    @property
    def check_id(self):
        return self.data.get('check_id')

    @check_id.setter
    def check_id(self, value):
        self.data['check_id'] = value

    @property
    def note(self):
        return self.data.get('note')

    @note.setter
    def note(self, value):
        self.data['note'] = value

    @property
    def student(self):
        return self.data.get('student')

    @student.setter
    def student(self, value):
        self.data['student'] = value

    def get_transfer_courses(self):
        transfers = []
        for cat in self.categories:
            for course in cat.course_reqts:
                if course.is_transfer_course:
                    transfers.append(course)
            for sub_cat in cat.sub_categories:
                for sub_course in sub_cat.course_reqts:
                    if sub_course.is_transfer_course:
                        transfers.append(sub_course)
        return transfers
