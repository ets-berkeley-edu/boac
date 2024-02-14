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
from boac.lib.util import utc_now, vacuum_whitespace
from boac.models.base import Base
from flask import current_app as app
from sqlalchemy import and_, text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import deferred

generic_permission_type_enum = ENUM(
    'read',
    'read_write',
    name='generic_permission_types',
    create_type=False,
)


class AuthorizedUser(Base):
    __tablename__ = 'authorized_users'

    SEARCH_HISTORY_ITEM_MAX_LENGTH = 256

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    automate_degree_progress_permission = db.Column(db.Boolean, nullable=False)
    can_access_advising_data = db.Column(db.Boolean, nullable=False)
    can_access_canvas_data = db.Column(db.Boolean, nullable=False)
    created_by = db.Column(db.String(255), nullable=False)
    degree_progress_permission = db.Column(generic_permission_type_enum)
    deleted_at = db.Column(db.DateTime, nullable=True)
    in_demo_mode = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean)
    # When True, is_blocked prevents a deleted user from being revived by the automated refresh.
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    search_history = deferred(db.Column(ARRAY(db.String), nullable=True))
    uid = db.Column(db.String(255), nullable=False, unique=True)
    department_memberships = db.relationship(
        'UniversityDeptMember',
        back_populates='authorized_user',
        lazy='joined',
    )
    cohort_filters = db.relationship(
        'CohortFilter',
        back_populates='owner',
        lazy='joined',
    )
    alert_views = db.relationship(
        'AlertView',
        back_populates='viewer',
        lazy='joined',
    )

    def __init__(
            self,
            uid,
            created_by,
            automate_degree_progress_permission=False,
            is_admin=False,
            is_blocked=False,
            in_demo_mode=False,
            can_access_advising_data=True,
            can_access_canvas_data=True,
            degree_progress_permission=None,
            search_history=(),
    ):
        self.automate_degree_progress_permission = automate_degree_progress_permission
        self.can_access_advising_data = can_access_advising_data
        self.can_access_canvas_data = can_access_canvas_data
        self.created_by = created_by
        self.degree_progress_permission = degree_progress_permission
        self.in_demo_mode = in_demo_mode
        self.is_admin = is_admin
        self.is_blocked = is_blocked
        self.search_history = search_history
        self.uid = uid

    def __repr__(self):
        return f"""<AuthorizedUser {self.uid},
                    automate_degree_progress_permission={self.automate_degree_progress_permission},
                    can_access_advising_data={self.can_access_advising_data},
                    can_access_canvas_data={self.can_access_canvas_data},
                    created={self.created_at},
                    created_by={self.created_by},
                    degree_progress_permission={self.degree_progress_permission},
                    deleted={self.deleted_at},
                    in_demo_mode={self.in_demo_mode},
                    is_admin={self.is_admin},
                    is_blocked={self.is_blocked},
                    search_history={self.search_history},
                    updated={self.updated_at}>
                """

    @classmethod
    def delete(cls, uid):
        now = utc_now()
        user = cls.query.filter_by(uid=uid).first()
        user.deleted_at = now
        std_commit()
        return user

    @classmethod
    def un_delete(cls, uid):
        user = cls.query.filter_by(uid=uid).first()
        user.deleted_at = None
        std_commit()
        return user

    @classmethod
    def create_or_restore(
            cls,
            uid,
            created_by,
            automate_degree_progress_permission=False,
            can_access_advising_data=True,
            can_access_canvas_data=True,
            degree_progress_permission=None,
            is_admin=False,
            is_blocked=False,
    ):
        existing_user = cls.query.filter_by(uid=uid).first()
        if existing_user:
            if existing_user.is_blocked:
                return False
            # If restoring a previously deleted user, respect passed-in attributes.
            if existing_user.deleted_at:
                existing_user.automate_degree_progress_permission = automate_degree_progress_permission
                existing_user.is_admin = is_admin
                existing_user.is_blocked = is_blocked
                existing_user.can_access_advising_data = can_access_advising_data
                existing_user.can_access_canvas_data = can_access_canvas_data
                existing_user.created_by = created_by
                existing_user.degree_progress_permission = degree_progress_permission
                existing_user.deleted_at = None
            # If the user currently exists in a non-deleted state, attributes passed in as True
            # should replace existing attributes set to False, but not vice versa.
            else:
                if automate_degree_progress_permission and not existing_user.automate_degree_progress_permission:
                    existing_user.automate_degree_progress_permission = True
                if can_access_advising_data and not existing_user.can_access_advising_data:
                    existing_user.can_access_advising_data = True
                if can_access_canvas_data and not existing_user.can_access_canvas_data:
                    existing_user.can_access_canvas_data = True
                if is_admin and not existing_user.is_admin:
                    existing_user.is_admin = True
                if is_blocked and not existing_user.is_blocked:
                    existing_user.is_blocked = True
                existing_user.degree_progress_permission = degree_progress_permission
                existing_user.created_by = created_by
            user = existing_user
        else:
            user = cls(
                automate_degree_progress_permission=automate_degree_progress_permission,
                can_access_advising_data=can_access_advising_data,
                can_access_canvas_data=can_access_canvas_data,
                created_by=created_by,
                degree_progress_permission=degree_progress_permission,
                in_demo_mode=False,
                is_admin=is_admin,
                is_blocked=is_blocked,
                uid=uid,
            )
        db.session.add(user)
        std_commit()
        return user

    @classmethod
    def get_id_per_uid(cls, uid, include_deleted=False):
        sql = 'SELECT id FROM authorized_users WHERE uid = :uid'
        if not include_deleted:
            sql += ' AND deleted_at IS NULL'
        query = text(sql)
        result = db.session.execute(query, {'uid': uid}).first()
        return result and result['id']

    @classmethod
    def get_uid_per_id(cls, user_id):
        query = text('SELECT uid FROM authorized_users WHERE id = :user_id AND deleted_at IS NULL')
        result = db.session.execute(query, {'user_id': user_id}).first()
        return result and result['uid']

    @classmethod
    def find_by_id(cls, user_id, include_deleted=False):
        query = cls.query.filter_by(id=user_id) if include_deleted else cls.query.filter_by(id=user_id, deleted_at=None)
        return query.first()

    @classmethod
    def users_with_uid_like(cls, uid_snippet, include_deleted=False):
        like_uid_snippet = cls.uid.like(f'%{uid_snippet}%')
        criteria = like_uid_snippet if include_deleted else and_(like_uid_snippet, cls.deleted_at == None)  # noqa: E711
        return cls.query.filter(criteria).all()

    @classmethod
    def find_by_uid(cls, uid, ignore_deleted=True):
        query = cls.query.filter_by(uid=uid, deleted_at=None) if ignore_deleted else cls.query.filter_by(uid=uid)
        return query.first()

    @classmethod
    def get_all_active_users(cls, include_deleted=False):
        return cls.query.all() if include_deleted else cls.query.filter_by(deleted_at=None).all()

    @classmethod
    def get_admin_users(cls, ignore_deleted=True):
        if ignore_deleted:
            query = cls.query.filter(and_(cls.is_admin, cls.deleted_at == None))  # noqa: E711
        else:
            query = cls.query.filter(cls.is_admin)
        return query.all()

    @classmethod
    def add_to_search_history(cls, user_id, search_phrase):
        search_phrase = vacuum_whitespace(search_phrase)
        query = text('SELECT search_history FROM authorized_users WHERE id = :user_id')
        result = db.session.execute(query, {'user_id': user_id}).first()
        if result:
            search_history = result['search_history'] or []
            if len(search_phrase) > cls.SEARCH_HISTORY_ITEM_MAX_LENGTH:
                if ' ' in search_phrase:
                    search_phrase = search_phrase[:cls.SEARCH_HISTORY_ITEM_MAX_LENGTH + 1]
                    search_phrase = search_phrase[:search_phrase.rindex(' ') + 1].strip()
                else:
                    search_phrase = search_phrase[:cls.SEARCH_HISTORY_ITEM_MAX_LENGTH]
            phrase_lowered = search_phrase.lower()
            for idx, entry in enumerate(search_history):
                if phrase_lowered == entry.lower():
                    del search_history[idx]
            search_history.insert(0, search_phrase)

            max_size = app.config['USER_SEARCH_HISTORY_MAX_SIZE']
            if len(search_history) > max_size:
                del search_history[max_size:]

            sql_text = text('UPDATE authorized_users SET search_history = :history WHERE id = :id')
            db.session.execute(sql_text, {'history': search_history, 'id': user_id})
            return cls.get_search_history(user_id)
        else:
            return None

    @classmethod
    def get_search_history(cls, user_id):
        query = text('SELECT search_history FROM authorized_users WHERE id = :id')
        result = db.session.execute(query, {'id': user_id}).first()
        return result and result['search_history']

    @classmethod
    def get_users(
            cls,
            deleted=None,
            blocked=None,
            dept_code=None,
            role=None,
    ):
        query_tables, query_filter, query_bindings = _users_sql(
            blocked=blocked,
            deleted=deleted,
            dept_code=dept_code,
            role=role,
        )
        query = text(f"""
            SELECT u.id
            {query_tables}
            {query_filter}
        """)
        results = db.session.execute(query, query_bindings)
        user_ids = [row['id'] for row in results]
        return cls.query.filter(cls.id.in_(user_ids)).all(), len(user_ids)

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

    @classmethod
    def update_user(
        cls,
        user_id,
        automate_degree_progress_permission=None,
        can_access_advising_data=False,
        can_access_canvas_data=False,
        degree_progress_permission=None,
        is_admin=False,
        is_blocked=False,
        include_deleted=False,
    ):
        user = AuthorizedUser.find_by_id(user_id, include_deleted)
        if automate_degree_progress_permission is not None:
            user.automate_degree_progress_permission = automate_degree_progress_permission
        user.can_access_advising_data = can_access_advising_data
        user.can_access_canvas_data = can_access_canvas_data
        user.degree_progress_permission = degree_progress_permission
        user.is_admin = is_admin
        user.is_blocked = is_blocked
        std_commit()
        return user


def _users_sql(
        blocked=None,
        deleted=None,
        dept_code=None,
        role=None,
):
    query_tables = 'FROM authorized_users u '
    query_filter = _users_sql_where_clause(blocked, deleted, role == 'admin')
    query_bindings = {}

    if dept_code and role:
        query_tables += """
            JOIN university_depts d ON
                d.dept_code = :dept_code
            JOIN university_dept_members m ON
                m.university_dept_id = d.id
                AND m.authorized_user_id = u.id
        """
        if role == 'noCanvasDataAccess':
            query_filter += 'AND u.can_access_canvas_data IS FALSE '
        elif role == 'noAdvisingDataAccess':
            query_filter += 'AND u.can_access_advising_data IS FALSE '
        elif role in ['advisor', 'director']:
            query_tables += f"AND m.role = '{role}'"
        query_bindings['dept_code'] = dept_code
    elif not dept_code and role:
        if role == 'noCanvasDataAccess':
            query_filter += 'AND u.can_access_canvas_data IS FALSE '
        elif role == 'noAdvisingDataAccess':
            query_filter += 'AND u.can_access_advising_data IS FALSE '
        else:
            query_tables += f"""
                JOIN university_dept_members m ON
                    m.authorized_user_id = u.id
                    AND m.role = '{role}'
            """
    elif dept_code and not role:
        query_tables += """
            JOIN university_depts d ON d.dept_code = :dept_code
            JOIN university_dept_members m ON
                m.university_dept_id = d.id
                AND m.authorized_user_id = u.id
        """
        query_bindings['dept_code'] = dept_code
    return query_tables, query_filter, query_bindings


def _users_sql_where_clause(blocked, deleted, is_admin):
    query_filter = 'WHERE TRUE '
    if blocked is True:
        query_filter += 'AND u.is_blocked IS TRUE '
    elif blocked is False:
        query_filter += 'AND u.is_blocked IS FALSE '

    if deleted is True:
        query_filter += 'AND u.deleted_at IS NOT NULL '
    elif deleted is False:
        query_filter += 'AND u.deleted_at IS NULL '

    if is_admin:
        query_filter += 'AND u.is_admin IS TRUE '

    return query_filter
