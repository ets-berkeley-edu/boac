"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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
from boac.models.db_relationships import cohort_filter_owners
from sqlalchemy import text


class AuthorizedUser(Base):
    __tablename__ = 'authorized_users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    uid = db.Column(db.String(255), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean)
    in_demo_mode = db.Column(db.Boolean, nullable=False)
    can_access_canvas_data = db.Column(db.Boolean, nullable=False)
    created_by = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    # When True, is_blocked prevents a deleted user from being revived by the automated refresh.
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    department_memberships = db.relationship(
        'UniversityDeptMember',
        back_populates='authorized_user',
        lazy='joined',
    )
    drop_in_departments = db.relationship(
        'DropInAdvisor',
        back_populates='authorized_user',
        primaryjoin='and_(AuthorizedUser.id==DropInAdvisor.authorized_user_id, DropInAdvisor.deleted_at==None)',
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

    def __init__(self, uid, created_by, is_admin=False, in_demo_mode=False, can_access_canvas_data=True):
        self.uid = uid
        self.created_by = created_by
        self.is_admin = is_admin
        self.in_demo_mode = in_demo_mode
        self.can_access_canvas_data = can_access_canvas_data

    def __repr__(self):
        return f"""<AuthorizedUser {self.uid},
                    is_admin={self.is_admin},
                    in_demo_mode={self.in_demo_mode},
                    can_access_canvas_data={self.can_access_canvas_data},
                    created={self.created_at},
                    created_by={self.created_by},
                    updated={self.updated_at},
                    deleted={self.deleted_at},
                    is_blocked={self.is_blocked}>
                """

    @classmethod
    def delete_and_block(cls, uid):
        now = utc_now()
        user = cls.query.filter_by(uid=uid).first()
        user.deleted_at = now
        user.is_blocked = True
        std_commit()
        return user

    @classmethod
    def create_or_restore(cls, uid, created_by, is_admin=False, can_access_canvas_data=True):
        existing_user = cls.query.filter_by(uid=uid).first()
        if existing_user:
            if existing_user.is_blocked:
                return False
            # If restoring a previously deleted user, respect passed-in attributes.
            if existing_user.deleted_at:
                existing_user.is_admin = is_admin
                existing_user.can_access_canvas_data = can_access_canvas_data
                existing_user.created_by = created_by
                existing_user.deleted_at = None
            # If the user currently exists in a non-deleted state, attributes passed in as True
            # should replace existing attributes set to False, but not vice versa.
            else:
                if can_access_canvas_data and not existing_user.can_access_canvas_data:
                    existing_user.can_access_canvas_data = True
                if is_admin and not existing_user.is_admin:
                    existing_user.is_admin = True
                existing_user.created_by = created_by
            user = existing_user
        else:
            user = cls(
                uid=uid,
                created_by=created_by,
                is_admin=is_admin,
                in_demo_mode=False,
                can_access_canvas_data=can_access_canvas_data,
            )
        std_commit()
        return user

    @classmethod
    def get_id_per_uid(cls, uid):
        query = text(f'SELECT id FROM authorized_users WHERE uid = :uid AND deleted_at IS NULL')
        result = db.session.execute(query, {'uid': uid}).first()
        return result and result['id']

    @classmethod
    def get_uid_per_id(cls, user_id):
        query = text(f'SELECT uid FROM authorized_users WHERE id = :user_id AND deleted_at IS NULL')
        result = db.session.execute(query, {'user_id': user_id}).first()
        return result and result['uid']

    @classmethod
    def find_by_id(cls, db_id):
        return AuthorizedUser.query.filter_by(id=db_id, deleted_at=None).first()

    @classmethod
    def find_by_uid(cls, uid):
        return AuthorizedUser.query.filter_by(uid=uid, deleted_at=None).first()

    @classmethod
    def get_all_active_users(cls):
        return cls.query.filter_by(deleted_at=None).all()

    @classmethod
    def get_all_users(cls):
        return cls.query.all()

    @classmethod
    def get_all_uids_in_scope(cls, scope=()):
        sql = 'SELECT uid FROM authorized_users u '
        if not scope:
            return None
        elif 'ADMIN' in scope:
            sql += 'WHERE u.deleted_at IS NULL'
        else:
            sql += """
                JOIN university_dept_members m ON m.authorized_user_id = u.id
                JOIN university_depts d ON d.id = m.university_dept_id
                WHERE
                d.dept_code = ANY(:scope)
                AND u.deleted_at IS NULL
            """
        results = db.session.execute(sql, {'scope': scope})
        return [row['uid'] for row in results]
