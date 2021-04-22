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
from boac.models.base import Base
from dateutil.tz import tzutc


class DegreeProgressCourse(Base):
    __tablename__ = 'degree_progress_courses'

    section_id = db.Column(db.Integer, nullable=False, primary_key=True)
    sid = db.Column(db.String(80), nullable=False, primary_key=True)
    term_id = db.Column(db.Integer, nullable=False, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('degree_progress_categories.id'), nullable=True)
    display_name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text)
    units = db.Column(db.Integer, nullable=False)

    def __init__(
            self,
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
        self.display_name = display_name
        self.grade = grade
        self.note = note
        self.section_id = section_id
        self.sid = sid
        self.term_id = term_id
        self.units = units

    def __repr__(self):
        return f"""<DegreeProgressCourse
            category_id={self.category_id},
            display_name={self.display_name},
            grade={self.grade},
            note={self.note},
            section_id={self.section_id},
            sid={self.sid},
            term_id={self.term_id},
            units={self.units},>"""

    @classmethod
    def assign_category(cls, category_id, section_id, sid, term_id):
        course = cls.query.filter_by(section_id=section_id, sid=sid, term_id=term_id).first()
        course.category_id = category_id
        std_commit()
        return course

    @classmethod
    def create(
            cls,
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
            display_name=display_name,
            grade=grade,
            note=note,
            section_id=section_id,
            sid=sid,
            term_id=term_id,
            units=units,
        )
        db.session.add(course)
        return course

    @classmethod
    def get_unassigned_by_sid(cls, sid):
        return cls.query.filter_by(sid=sid).all()

    @classmethod
    def update(
            cls,
            note,
            section_id,
            sid,
            term_id,
            units,
    ):
        course = cls.query.filter_by(section_id=section_id, sid=sid, term_id=term_id).first()
        course.units = units
        course.note = note
        std_commit()
        return course

    def to_api_json(self):
        return {
            'categoryId': self.category_id,
            'createdAt': _isoformat(self.created_at),
            'displayName': self.display_name,
            'grade': self.grade,
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
