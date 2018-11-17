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
from boac.models.db_relationships import cohort_filter_owners
from flask_login import UserMixin


class AuthorizedUser(Base, UserMixin):
    __tablename__ = 'authorized_users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    uid = db.Column(db.String(255), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean)
    in_demo_mode = db.Column(db.Boolean, nullable=False)
    department_memberships = db.relationship(
        'UniversityDeptMember',
        back_populates='authorized_user',
        lazy='joined',
    )
    cohort_filters = db.relationship(
        'CohortFilter',
        secondary=cohort_filter_owners,
        back_populates='owners',
        lazy='joined',
    )
    alert_views = db.relationship(
        'AlertView',
        back_populates='viewer',
        lazy='joined',
    )

    def __init__(self, uid, is_admin=False, in_demo_mode=False):
        self.uid = uid
        self.is_admin = is_admin
        self.in_demo_mode = in_demo_mode

    def __repr__(self):
        return f"""<AuthorizedUser {self.uid},
                    is_admin={self.is_admin},
                    in_demo_mode={self.in_demo_mode},
                    updated={self.updated_at},
                    created={self.created_at}>
                """

    def get_id(self):
        """Override UserMixin, since our DB conventionally reserves 'id' for generated keys."""
        return self.uid

    @classmethod
    def find_by_id(cls, db_id):
        user = AuthorizedUser.query.filter_by(id=db_id).first()
        std_commit()
        return user

    @classmethod
    def find_by_uid(cls, uid):
        """Supports Flask-Login via user_loader in routes.py."""
        user = AuthorizedUser.query.filter_by(uid=uid).first()
        std_commit()
        return user
