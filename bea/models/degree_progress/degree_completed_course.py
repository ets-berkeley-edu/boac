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

from bea.models.degree_progress.degree_course import DegreeCourse


class DegreeCompletedCourse(DegreeCourse):

    @property
    def ccn(self):
        return self.data['ccn']

    @ccn.setter
    def ccn(self, value):
        self.data['ccn'] = value

    @property
    def course_copies(self):
        return self.data['course_copies']

    @course_copies.setter
    def course_copies(self, value):
        self.data['course_copies'] = value

    @property
    def course_orig(self):
        return self.data['course_orig']

    @course_orig.setter
    def course_orig(self, value):
        self.data['course_orig'] = value

    @property
    def degree_check(self):
        return self.data['degree_check']

    @degree_check.setter
    def degree_check(self, value):
        self.data['degree_check'] = value

    @property
    def grade(self):
        return self.data['grade']

    @grade.setter
    def grade(self, value):
        self.data['grade'] = value

    @property
    def junk(self):
        return self.data['junk']

    @junk.setter
    def junk(self, value):
        self.data['junk'] = value

    @property
    def manual(self):
        return self.data['manual']

    @manual.setter
    def manual(self, value):
        self.data['manual'] = value

    @property
    def note(self):
        return self.data['note']

    @note.setter
    def note(self, value):
        self.data['note'] = value

    @property
    def req_course(self):
        return self.data['req_course']

    @req_course.setter
    def req_course(self, value):
        self.data['req_course'] = value

    @property
    def term_id(self):
        return self.data['term_id']

    @term_id.setter
    def term_id(self, value):
        self.data['term_id'] = value

    @property
    def units_orig(self):
        return self.data['units_orig']

    @units_orig.setter
    def units_orig(self, value):
        self.data['units_orig'] = value

    @property
    def waitlisted(self):
        return self.data['waitlisted']

    @waitlisted.setter
    def waitlisted(self, value):
        self.data['waitlisted'] = value
