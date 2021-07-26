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

from datetime import datetime

from boac import db, std_commit
from boac.lib.berkeley import term_name_for_sis_id
from boac.lib.util import is_int
from boac.models.base import Base
from boac.models.degree_progress_category_unit_requirement import DegreeProgressCategoryUnitRequirement
from boac.models.degree_progress_course_unit_requirement import DegreeProgressCourseUnitRequirement
from dateutil.tz import tzutc


class DegreeProgressCourse(Base):
    __tablename__ = 'degree_progress_courses'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    accent_color = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('degree_progress_categories.id'))
    degree_check_id = db.Column(db.Integer, db.ForeignKey('degree_progress_templates.id'), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(255), nullable=False)
    ignore = db.Column(db.Boolean, nullable=False)
    note = db.Column(db.Text)
    manually_created_at = db.Column(db.DateTime)
    manually_created_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'))
    section_id = db.Column(db.Integer)
    sid = db.Column(db.String(80), nullable=False)
    term_id = db.Column(db.Integer)
    units = db.Column(db.Numeric, nullable=False)
    unit_requirements = db.relationship(
        DegreeProgressCourseUnitRequirement.__name__,
        back_populates='course',
        lazy='joined',
    )

    __table_args__ = (db.UniqueConstraint(
        'category_id',
        'degree_check_id',
        'display_name',
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
            accent_color=None,
            category_id=None,
            ignore=False,
            manually_created_by=None,
            note=None,
    ):
        self.accent_color = accent_color
        self.category_id = category_id
        self.degree_check_id = degree_check_id
        self.display_name = display_name
        self.grade = grade
        self.ignore = ignore
        self.manually_created_by = manually_created_by
        if self.manually_created_by:
            self.manually_created_at = datetime.now()
        self.note = note
        self.section_id = section_id
        self.sid = sid
        self.term_id = term_id
        self.units = units

    def __repr__(self):
        return f"""<DegreeProgressCourse id={self.id},
            accent_color={self.accent_color},
            category_id={self.category_id},
            degree_check_id={self.degree_check_id},
            display_name={self.display_name},
            grade={self.grade},
            ignore={self.ignore},
            manually_created_at={self.manually_created_at},
            manually_created_by={self.manually_created_by},
            note={self.note},
            section_id={self.section_id},
            sid={self.sid},
            term_id={self.term_id},
            units={self.units},>"""

    @classmethod
    def assign(cls, category_id, course_id):
        course = cls.query.filter_by(id=course_id).first()
        course.category_id = category_id
        course.ignore = False
        std_commit()
        DegreeProgressCourseUnitRequirement.delete(course_id)
        for u in DegreeProgressCategoryUnitRequirement.find_by_category_id(category_id):
            DegreeProgressCourseUnitRequirement.create(course.id, u.unit_requirement_id)
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
            accent_color=None,
            category_id=None,
            manually_created_by=None,
            note=None,
            unit_requirement_ids=(),
    ):
        course = cls(
            accent_color=accent_color,
            category_id=category_id,
            degree_check_id=degree_check_id,
            display_name=display_name,
            grade=grade,
            manually_created_by=manually_created_by,
            note=note,
            section_id=section_id,
            sid=sid,
            term_id=term_id,
            units=units if is_int(units) else 0,
        )
        db.session.add(course)
        std_commit()

        for unit_requirement_id in unit_requirement_ids:
            DegreeProgressCourseUnitRequirement.create(
                course_id=course.id,
                unit_requirement_id=unit_requirement_id,
            )
        return course

    @classmethod
    def delete(cls, course):
        db.session.delete(course)
        std_commit()

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
    def get_courses(cls, degree_check_id, section_id, sid, term_id):
        return cls.query.filter_by(
            degree_check_id=degree_check_id,
            section_id=section_id,
            sid=sid,
            term_id=term_id,
        ).all()

    @classmethod
    def unassign(cls, course_id, ignore=False):
        course = cls.query.filter_by(id=course_id).first()
        course.category_id = None
        course.ignore = ignore
        std_commit()
        DegreeProgressCourseUnitRequirement.delete(course_id)
        return course

    @classmethod
    def update(cls, course_id, note, units, unit_requirement_ids):
        course = cls.query.filter_by(id=course_id).first()
        course.units = units
        course.note = note

        existing_unit_requirements = DegreeProgressCourseUnitRequirement.find_by_course_id(course_id)
        existing_unit_requirement_id_set = set([u.unit_requirement_id for u in existing_unit_requirements])
        unit_requirement_id_set = set(unit_requirement_ids or [])
        for unit_requirement_id in (unit_requirement_id_set - existing_unit_requirement_id_set):
            DegreeProgressCourseUnitRequirement.create(
                course_id=course.id,
                unit_requirement_id=unit_requirement_id,
            )
        for unit_requirement_id in (existing_unit_requirement_id_set - unit_requirement_id_set):
            delete_me = next(e for e in existing_unit_requirements if e.unit_requirement_id == unit_requirement_id)
            db.session.delete(delete_me)

        std_commit()
        return course

    def to_api_json(self):
        unit_requirements = [m.unit_requirement.to_api_json() for m in (self.unit_requirements or [])]
        return {
            'accentColor': self.accent_color,
            'categoryId': self.category_id,
            'createdAt': _isoformat(self.created_at),
            'degreeCheckId': self.degree_check_id,
            'grade': self.grade,
            'id': self.id,
            'ignore': self.ignore,
            'manuallyCreatedAt': _isoformat(self.manually_created_at),
            'manuallyCreatedBy': self.manually_created_by,
            'name': self.display_name,
            'note': self.note,
            'sectionId': self.section_id,
            'sid': self.sid,
            'termId': self.term_id,
            'termName': term_name_for_sis_id(self.term_id),
            'unitRequirements': sorted(unit_requirements, key=lambda r: r['name']),
            'units': self.units,
            'updatedAt': _isoformat(self.updated_at),
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
