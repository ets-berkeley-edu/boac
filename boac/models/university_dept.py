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

from boac import db, std_commit
from boac.models.base import Base
from sqlalchemy.sql import text


class UniversityDept(Base):
    __tablename__ = 'university_depts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
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
    def find_by_id(cls, university_dept_id):
        return cls.query.filter_by(id=university_dept_id).first()

    @classmethod
    def find_by_dept_code(cls, dept_code):
        return cls.query.filter_by(dept_code=dept_code).first()

    @classmethod
    def get_all_departments(cls, exclude_empty=False):
        sql = f"""
            SELECT
                d.id, d.dept_code, d.dept_name, COUNT(m.authorized_user_id) AS member_count,
                p.id AS peer_advising_department_id,
                p.name AS peer_advising_department_name
            FROM university_dept_members m
            JOIN university_depts d ON d.id = m.university_dept_id
            LEFT JOIN authorized_users u ON u.id = m.authorized_user_id
            LEFT JOIN peer_advising_departments p ON p.university_dept_id = m.university_dept_id
            WHERE u.deleted_at IS NULL
            GROUP BY d.id, d.dept_code, d.dept_name, p.id, p.name
            {'HAVING COUNT(m.authorized_user_id) > 0' if exclude_empty else ''}
            ORDER BY d.dept_name
        """
        results = []
        for row in db.session.execute(text(sql)):
            dept_code = row['dept_code']
            department_json = next((d for d in results if d['dept_code'] == dept_code), None)
            if not department_json:
                department_json = {
                    'id': row['id'],
                    'dept_code': row['dept_code'],
                    'dept_name': row['dept_name'],
                    'member_count': row['member_count'],
                    'peer_advising_departments': [],
                }
                results.append(department_json)
            if row['peer_advising_department_id']:
                department_json['peer_advising_departments'].append({
                    'id': row['peer_advising_department_id'],
                    'name': row['peer_advising_department_name'],
                })
        return results

    @classmethod
    def create(cls, dept_code, dept_name):
        dept = cls(dept_code=dept_code, dept_name=dept_name)
        db.session.add(dept)
        std_commit()
        return dept

    def delete_automated_members(self):
        sql = """
            DELETE FROM university_dept_members
                WHERE university_dept_id = :id
                AND automate_membership IS TRUE;
            UPDATE authorized_users SET deleted_at = now()
                WHERE is_admin IS FALSE
                AND deleted_at IS NULL
                AND id NOT IN (SELECT authorized_user_id FROM university_dept_members)
                AND id NOT IN (SELECT authorized_user_id FROM peer_advising_department_members WHERE deleted_at IS NULL)
        """
        db.session.execute(text(sql), {'id': self.id})
        std_commit()

    def to_api_json(self):
        dept_code = self.dept_code
        return {
            'id': self.id,
            'deptCode': dept_code,
            'deptName': self.dept_name,
        }
