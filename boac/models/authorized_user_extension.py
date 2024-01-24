"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from sqlalchemy.ext.declarative import declared_attr


class AuthorizedUserExtension(Base):
    __abstract__ = True

    @declared_attr
    def authorized_user_id(cls):  # noqa: N805
        return db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False, primary_key=True)

    @declared_attr
    def authorized_user(cls):  # noqa: N805
        return db.relationship('AuthorizedUser', back_populates=cls.authorized_user_relationship)

    dept_code = db.Column(db.String(80), nullable=False, primary_key=True)

    @classmethod
    def find_by_dept_and_user(cls, dept_code, authorized_user_id):
        return cls.query.filter_by(authorized_user_id=authorized_user_id, dept_code=dept_code).first()

    @classmethod
    def get_all(cls, authorized_user_id):
        return cls.query.filter_by(authorized_user_id=authorized_user_id).all()

    @classmethod
    def delete(cls, authorized_user_id, dept_code):
        row = cls.query.filter_by(authorized_user_id=authorized_user_id, dept_code=dept_code).first()
        if not row:
            return False
        db.session.delete(row)
        std_commit()
        return True

    @classmethod
    def delete_orphans(cls):
        sql = f"""
            DELETE FROM {cls.__tablename__} AS a
                WHERE a.authorized_user_id NOT IN (
                    SELECT m.authorized_user_id
                    FROM university_depts AS d
                    JOIN university_dept_members AS m
                    ON m.university_dept_id = d.id
                    WHERE d.dept_code = a.dept_code
                );"""
        db.session.execute(sql)
        std_commit()


class Advisor(AuthorizedUserExtension):
    __abstract__ = True

    is_available = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, authorized_user_id, dept_code, is_available):
        self.authorized_user_id = authorized_user_id
        self.dept_code = dept_code
        self.is_available = is_available

    def update_availability(self, available):
        self.is_available = available
        std_commit()

    @classmethod
    def create_or_update_membership(cls, dept_code, authorized_user_id, is_available=False):
        existing_membership = cls.query.filter_by(dept_code=dept_code, authorized_user_id=authorized_user_id).first()
        if existing_membership:
            new_membership = existing_membership
            new_membership.is_available = is_available
        else:
            new_membership = cls(
                authorized_user_id=authorized_user_id,
                dept_code=dept_code,
                is_available=is_available,
            )
        db.session.add(new_membership)
        std_commit()
        return new_membership

    @classmethod
    def advisors_for_dept_code(cls, dept_code):
        return cls.query.filter_by(dept_code=dept_code).all()
