"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import db, std_commit


class DegreeProgressCourseUnitRequirement(db.Model):
    __tablename__ = 'degree_progress_course_unit_requirements'

    course_id = db.Column(db.Integer, db.ForeignKey('degree_progress_courses.id'), primary_key=True)
    unit_requirement_id = db.Column(db.Integer, db.ForeignKey('degree_progress_unit_requirements.id'), primary_key=True)
    course = db.relationship('DegreeProgressCourse', back_populates='unit_requirements')
    unit_requirement = db.relationship('DegreeProgressUnitRequirement', back_populates='courses')

    def __init__(
            self,
            course_id,
            unit_requirement_id,
    ):
        self.course_id = course_id
        self.unit_requirement_id = unit_requirement_id

    @classmethod
    def create(cls, course_id, unit_requirement_id):
        db.session.add(cls(course_id=course_id, unit_requirement_id=unit_requirement_id))
        std_commit()

    @classmethod
    def delete(cls, course_id):
        for row in cls.find_by_course_id(course_id):
            db.session.delete(row)
        std_commit()

    @classmethod
    def find_by_course_id(cls, course_id):
        return cls.query.filter_by(course_id=course_id).all()
