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


"""This package integrates with Flask-Login. Determine who can use the app and which privileges they have."""
from boac import db, std_commit
from boac.models.base import Base
from boac.models.db_relationships import cohort_filter_owners
from boac.models.student_group import StudentGroup
from flask_login import UserMixin


class AuthorizedUser(Base, UserMixin):
    __tablename__ = 'authorized_users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    uid = db.Column(db.String(255), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean)
    department_memberships = db.relationship(
        'UniversityDeptMember',
        back_populates='authorized_user',
        lazy=True,
    )
    cohort_filters = db.relationship(
        'CohortFilter',
        secondary=cohort_filter_owners,
        back_populates='owners',
        lazy=True,
    )
    alert_views = db.relationship(
        'AlertView',
        back_populates='viewer',
        lazy=True,
    )

    def __init__(self, uid, is_admin=False):
        self.uid = uid
        self.is_admin = is_admin

    def __repr__(self):
        return f"""<AuthorizedUser {self.uid},
                    is_admin={self.is_admin},
                    updated={self.updated_at},
                    created={self.created_at}>
                """

    def get_id(self):
        """Override UserMixin, since our DB conventionally reserves 'id' for generated keys."""
        return self.uid

    @classmethod
    def find_by_uid(cls, uid):
        return AuthorizedUser.query.filter_by(uid=uid).first()

    # TODO This method is presently not called, since we currently create authorized users manually in the database. As
    # we move to creating users programmatically, they will be given a default "My Students" group on creation.
    @classmethod
    def create(cls, uid, is_admin):
        user = cls(uid=uid, is_admin=is_admin)
        db.session.add(user)
        std_commit()
        StudentGroup.create(cls, user.id, 'My Students')
        return user
