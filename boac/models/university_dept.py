"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.base import Base

ASC_DEPT = {
    'code': 'UWASC',
    'name': 'Athletic Study Center',
}


class UniversityDept(Base):
    __tablename__ = 'university_depts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    dept_code = db.Column(db.String(80), nullable=False)
    dept_name = db.Column(db.String(255), nullable=False)
    authorized_users = db.relationship(
        'UniversityDeptMember',
        back_populates='university_dept',
    )

    __table_args__ = (db.UniqueConstraint('dept_code', 'dept_name', name='university_depts_code_unique_constraint'),)

    def __init__(self, dept_code, dept_name):
        self.dept_code = dept_code
        self.dept_name = dept_name

    @classmethod
    def find_by_dept_code(cls, dept_code):
        return cls.query.filter_by(dept_code=dept_code).first()

    @classmethod
    def create(cls, dept_code, dept_name):
        dept = cls(dept_code=dept_code, dept_name=dept_name)
        db.session.add(dept)
        std_commit()
        return dept
