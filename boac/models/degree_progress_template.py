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
from boac.lib.util import utc_now
from boac.models.base import Base
from boac.models.degree_progress_category import DegreeProgressCategory
from boac.models.degree_progress_unit_requirement import DegreeProgressUnitRequirement
from dateutil.tz import tzutc
from sqlalchemy import and_
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
    def find_by_name(cls, name, case_insensitive=False):
        if case_insensitive:
            return cls.query.filter(and_(cls.degree_name.ilike(name), cls.deleted_at == None)).first()  # noqa: E711
        else:
            return cls.query.filter_by(degree_name=name, deleted_at=None).first()

    @classmethod
    def find_by_sid(cls, student_sid, order_by=None):
        order_by = cls.created_at if order_by is None else order_by
        return cls.query.filter_by(student_sid=student_sid, deleted_at=None).order_by(order_by).all()

    @classmethod
    def get_all_templates(cls):
        criterion = and_(
            cls.student_sid == None,  # noqa: E711
            cls.deleted_at == None,  # noqa: E711
        )
        return cls.query.filter(criterion).order_by(cls.created_at).all()

    @classmethod
    def update(cls, template_id, name):
        template = cls.query.filter_by(id=template_id).first()
        template.degree_name = name
        std_commit()
        return template

    def to_api_json(self):
        return {
            'id': self.id,
            'advisorDeptCodes': self.advisor_dept_codes,
            'categories': DegreeProgressCategory.get_categories(template_id=self.id),
            'createdAt': _isoformat(self.created_at),
            'createdBy': self.created_by,
            'name': self.degree_name,
            'sid': self.student_sid,
            'unitRequirements': [u.to_api_json() for u in self.unit_requirements],
            'updatedAt': _isoformat(self.updated_at),
            'updatedBy': self.updated_by,
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
