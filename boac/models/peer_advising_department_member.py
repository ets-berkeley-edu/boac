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

from boac import db, std_commit
from boac.models.base import Base
from sqlalchemy.dialects.postgresql import ENUM

role_types = ENUM(
    'peer_advisor',
    'peer_advisor_manager',
    name='role_types',
    create_type=False,
)


class PeerAdvisingDepartmentMember(Base):
    __tablename__ = 'peer_advising_department_members'

    role_type = db.Column(role_types, nullable=False)
    peer_advising_department_id = db.Column(db.Integer, db.ForeignKey('peer_advising_departments.id'), nullable=False, primary_key=True)
    authorized_user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False, primary_key=True)
    deleted_at = db.Column(db.DateTime)

    def __init__(self, authorized_user_id, peer_advising_department_id, role_type):
        self.authorized_user_id = authorized_user_id
        self.peer_advising_department_id = peer_advising_department_id
        self.role_type = role_type

    @classmethod
    def create_or_update_membership(
            cls,
            authorized_user_id,
            peer_advising_department_id,
            role_type,
    ):
        membership = cls.query.filter_by(
            authorized_user_id=authorized_user_id,
            peer_advising_department_id=peer_advising_department_id,
            role_type=role_type,
        ).first()
        if membership:
            membership.role_type = role_type
        else:
            membership = cls(
                authorized_user_id=authorized_user_id,
                peer_advising_department_id=peer_advising_department_id,
                role_type=role_type,
            )
            db.session.add(membership)
        std_commit()
        return membership

    @classmethod
    def delete_membership(cls, authorized_user_id, peer_advising_department_id):
        membership = cls.query.filter_by(
            authorized_user_id=authorized_user_id,
            peer_advising_department_id=peer_advising_department_id,
        ).first()
        if not membership:
            return False
        db.session.delete(membership)
        std_commit()
        return True

    @classmethod
    def get_peer_advising_department_memberships(cls, authorized_user_id):
        def _to_dict(row):
            return {
                'peer_advising_department_name': row['name'],
                'peer_advising_department_id': row['peer_advising_department_id'],
                'role_type': row['role_type'],
                'university_dept_code': row['university_dept_code'],
                'university_dept_name': row['university_dept_name'],
            }
        sql = """
            SELECT
                d.name,
                m.peer_advising_department_id,
                m.role_type,
                u.dept_code AS university_dept_code,
                u.dept_name AS university_dept_name
            FROM peer_advising_department_members m
            JOIN peer_advising_departments d ON d.id = m.peer_advising_department_id
            JOIN university_depts u ON u.id = d.university_dept_id
            WHERE
                m.authorized_user_id = :authorized_user_id
                AND m.deleted_at IS NULL
        """
        return [_to_dict(row) for row in db.session.execute(sql, {'authorized_user_id': authorized_user_id})]
