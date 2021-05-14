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
from boac.externals import data_loch
from boac.lib.util import utc_now
from boac.merged.sis_terms import current_term_id
from boac.merged.student import merge_enrollment_terms
from boac.models.base import Base
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_course import DegreeProgressCourse
from boac.models.degree_progress_note import DegreeProgressNote
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
from dateutil.tz import tzutc
from sqlalchemy import and_, func, text
from sqlalchemy.dialects.postgresql import ARRAY


class DegreeProgressTemplate(Base):
    __tablename__ = 'degree_progress_templates'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    advisor_dept_codes = db.Column(ARRAY(db.String), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    degree_name = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    student_sid = db.Column(db.String(80), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)

    note = db.relationship(
        DegreeProgressNote.__name__,
        back_populates='template',
        uselist=False,
    )
    unit_requirements = db.relationship(
        DegreeProgressUnitRequirement.__name__,
        back_populates='template',
        order_by='DegreeProgressUnitRequirement.created_at',
    )

    def __init__(self, advisor_dept_codes, created_by, degree_name, student_sid, updated_by):
        self.advisor_dept_codes = advisor_dept_codes
        self.created_by = created_by
        self.degree_name = degree_name
        self.student_sid = student_sid
        self.updated_by = updated_by

    def __repr__(self):
        return f"""<DegreeProgressTemplate id={self.id},
                    degree_name={self.degree_name},
                    student_sid={self.student_sid},
                    advisor_dept_codes={self.advisor_dept_codes},
                    deleted_at={self.deleted_at},
                    created_at={self.created_at},
                    created_by={self.created_by},
                    updated_at={self.updated_at}
                    updated_by={self.updated_by}>"""

    @classmethod
    def create(
            cls,
            advisor_dept_codes,
            created_by,
            degree_name,
            student_sid=None,
    ):
        degree = cls(
            advisor_dept_codes=advisor_dept_codes,
            created_by=created_by,
            degree_name=degree_name,
            student_sid=student_sid,
            updated_by=created_by,
        )
        db.session.add(degree)
        std_commit()
        return degree

    @classmethod
    def delete(cls, template_id):
        template = cls.query.filter_by(id=template_id).first()
        template.deleted_at = utc_now()
        std_commit()

    @classmethod
    def find_by_id(cls, template_id):
        return cls.query.filter_by(id=template_id, deleted_at=None).first()

    @classmethod
    def find_by_name(cls, name, student_sids=None, case_insensitive=False):
        if student_sids:
            return db.session.query(
                cls.student_sid,
                func.max(cls.updated_at),
            ).filter(
                cls.degree_name == name,
                cls.deleted_at == None,  # noqa: E711
                cls.student_sid.in_(student_sids),
            ).group_by(cls.student_sid).all()
        if case_insensitive:
            return cls.query.filter(and_(cls.degree_name.ilike(name), cls.deleted_at == None, cls.student_sid == None)).first()  # noqa: E711
        else:
            return cls.query.filter_by(degree_name=name, deleted_at=None, student_sid=None).first()

    @classmethod
    def find_by_sid(cls, student_sid):
        sql = text(f"""
            SELECT id, created_at, degree_name, created_by, student_sid, updated_at, updated_by
            FROM degree_progress_templates
            WHERE student_sid = '{student_sid}' AND deleted_at IS NULL
            ORDER BY updated_at DESC
        """)
        # Most recently updated record is considered 'current'.
        api_json = []
        for index, row in enumerate(db.session.execute(sql)):
            api_json.append({
                **_row_to_simple_json(row),
                'isCurrent': index == 0,
            })
        return api_json

    @classmethod
    def get_all_templates(cls):
        sql = text("""
            SELECT id, created_at, degree_name, created_by, student_sid, updated_at, updated_by
            FROM degree_progress_templates
            WHERE student_sid IS NULL AND deleted_at IS NULL
            ORDER BY created_at
        """)
        return [_row_to_simple_json(row) for row in db.session.execute(sql)]

    @classmethod
    def refresh_updated_at(cls, template_id):
        sql_text = text('UPDATE degree_progress_templates SET updated_at = now() WHERE id = :id')
        db.session.execute(sql_text, {'id': template_id})

    @classmethod
    def update(cls, template_id, name):
        template = cls.query.filter_by(id=template_id).first()
        template.degree_name = name
        std_commit()
        return template

    def to_api_json(self, include_courses=False):
        unit_requirements = [u.to_api_json() for u in self.unit_requirements]
        api_json = {
            'id': self.id,
            'advisorDeptCodes': self.advisor_dept_codes,
            'categories': DegreeProgressCategory.get_categories(template_id=self.id),
            'createdAt': _isoformat(self.created_at),
            'createdBy': self.created_by,
            'name': self.degree_name,
            'note': self.note.to_api_json() if self.note else None,
            'sid': self.student_sid,
            'unitRequirements': sorted(unit_requirements, key=lambda r: r['name']),
            'updatedAt': _isoformat(self.updated_at),
            'updatedBy': self.updated_by,
        }
        if self.student_sid and include_courses:
            assigned_courses, unassigned_courses = self._get_partitioned_courses_json()
            api_json['courses'] = {
                'assigned': assigned_courses,
                'unassigned': unassigned_courses,
            }
        return api_json

    def _get_partitioned_courses_json(self):
        assigned_courses = []
        unassigned_courses = []
        degree_progress_courses = {}
        sid = self.student_sid
        # Sort courses by created_at (asc) so "copied" courses come after the primary assigned course.
        courses = DegreeProgressCourse.find_by_sid(degree_check_id=self.id, sid=sid)
        courses = sorted(courses, key=lambda c: c.created_at)

        def _key(section_id_, term_id_):
            return f'{section_id_}_{term_id_}'
        for course in courses:
            key = _key(course.section_id, course.term_id)
            if key not in degree_progress_courses:
                degree_progress_courses[key] = []
            degree_progress_courses[key].append(course)

        enrollments = data_loch.get_enrollments_for_sid(
            sid=sid,
            latest_term_id=current_term_id(),
        )
        for index, term in enumerate(merge_enrollment_terms(enrollments)):
            for enrollment in term.get('enrollments', []):
                for section in enrollment['sections']:
                    section_id = section['ccn']
                    term_id = term['termId']
                    key = _key(section_id, term_id)
                    if key in degree_progress_courses:
                        for idx, course in enumerate(degree_progress_courses[key]):
                            course_json = {
                                **course.to_api_json(),
                                'isCopy': idx > 0,
                            }
                            if course_json['categoryId']:
                                assigned_courses.append(course_json)
                            else:
                                unassigned_courses.append(course_json)
                    else:
                        grade = section['grade']
                        units = section['units']
                        if section.get('primary') and grade and units:
                            course = DegreeProgressCourse.create(
                                degree_check_id=self.id,
                                display_name=f"{enrollment['displayName']} {section['component']} {section['sectionNumber']}",
                                grade=grade,
                                section_id=section_id,
                                sid=sid,
                                term_id=term_id,
                                units=units,
                            )
                            unassigned_courses.append({
                                **course.to_api_json(),
                                'isCopy': False,
                            })
        return assigned_courses, unassigned_courses


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()


def _row_to_simple_json(row):
    return {
        'id': row['id'],
        'createdAt': _isoformat(row['created_at']),
        'createdBy': row['created_by'],
        'name': row['degree_name'],
        'sid': row['student_sid'],
        'updatedAt': _isoformat(row['updated_at']),
        'updatedBy': row['updated_by'],
    }
