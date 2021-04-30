"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.lib.berkeley import term_name_for_sis_id
from boac.lib.util import is_int
from boac.models.base import Base
from dateutil.tz import tzutc


class DegreeProgressCourse(Base):
    __tablename__ = 'degree_progress_courses'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    category_id = db.Column(db.Integer, db.ForeignKey('degree_progress_categories.id'), nullable=True)
    degree_check_id = db.Column(db.Integer, db.ForeignKey('degree_progress_templates.id'), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text)
    section_id = db.Column(db.Integer, nullable=False)
    sid = db.Column(db.String(80), nullable=False)
    term_id = db.Column(db.Integer, nullable=False)
    units = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint(
        'category_id',
        'degree_check_id',
        'section_id',
        'sid',
        'term_id',
        name='degree_progress_courses_category_id_course_unique_constraint',
    ),)

    def __init__(
            self,
            degree_check_id,
            display_name,
            grade,
            section_id,
            sid,
            term_id,
            units,
            category_id=None,
            note=None,
    ):
        self.category_id = category_id
        self.degree_check_id = degree_check_id
        self.display_name = display_name
        self.grade = grade
        self.note = note
        self.section_id = section_id
        self.sid = sid
        self.term_id = term_id
        self.units = units

    def __repr__(self):
        return f"""<DegreeProgressCourse id={self.id},
            category_id={self.category_id},
            degree_check_id={self.degree_check_id},
            display_name={self.display_name},
            grade={self.grade},
            note={self.note},
            section_id={self.section_id},
            sid={self.sid},
            term_id={self.term_id},
            units={self.units},>"""

    @classmethod
    def assign_category(cls, category_id, course_id):
        course = cls.query.filter_by(id=course_id).first()
        course.category_id = category_id
        std_commit()
        return course

    @classmethod
    def create(
            cls,
            degree_check_id,
            display_name,
            grade,
            section_id,
            sid,
            term_id,
            units,
            category_id=None,
            note=None,
    ):
        course = cls(
            category_id=category_id,
            degree_check_id=degree_check_id,
            display_name=display_name,
            grade=grade,
            note=note,
            section_id=section_id,
            sid=sid,
            term_id=term_id,
            units=units if is_int(units) else 0,  # TODO: Is units='E' valid? Can units value be non-numeric?
        )
        db.session.add(course)
        std_commit()
        return course

    @classmethod
    def find_by_id(cls, course_id):
        return cls.query.filter_by(id=course_id).first()

    @classmethod
    def find_by_category_id(cls, category_id):
        return cls.query.filter_by(category_id=category_id).all()

    @classmethod
    def find_by_sid(cls, degree_check_id, sid):
        return cls.query.filter_by(degree_check_id=degree_check_id, sid=sid).all()

    @classmethod
    def update(cls, course_id, note, units):
        course = cls.query.filter_by(id=course_id).first()
        course.units = units
        course.note = note
        std_commit()
        return course

    def to_api_json(self):
        return {
            'categoryId': self.category_id,
            'createdAt': _isoformat(self.created_at),
            'degreeCheckId': self.degree_check_id,
            'grade': self.grade,
            'id': self.id,
            'name': self.display_name,
            'note': self.note,
            'sectionId': self.section_id,
            'sid': self.sid,
            'termId': self.term_id,
            'termName': term_name_for_sis_id(self.term_id),
            'units': self.units,
            'updatedAt': _isoformat(self.updated_at),
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
