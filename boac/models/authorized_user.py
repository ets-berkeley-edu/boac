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
from boac.models.db_relationships import advisor_watchlists, cohort_filter_owners
from flask_login import UserMixin


class AuthorizedUser(Base, UserMixin):
    __tablename__ = 'authorized_users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    uid = db.Column(db.String(255), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean)
    is_advisor = db.Column(db.Boolean)
    is_director = db.Column(db.Boolean)
    cohort_filters = db.relationship(
        'CohortFilter',
        secondary=cohort_filter_owners,
        back_populates='owners',
        lazy=True,
    )
    watchlist = db.relationship(
        'Student',
        secondary=advisor_watchlists,
        lazy=True,
    )
    alert_views = db.relationship(
        'AlertView',
        back_populates='viewer',
        lazy=True,
    )

    def __init__(self, uid, is_admin=False, is_advisor=True, is_director=False):
        self.uid = uid
        self.is_admin = is_admin
        self.is_advisor = is_advisor
        self.is_director = is_director

    def __repr__(self):
        return f"""<AuthorizedUser {self.uid},
                    is_admin={self.is_admin},
                    is_advisor={self.is_advisor},
                    is_director={self.is_director},
                    updated={self.updated_at},
                    created={self.created_at}>
                """

    def get_id(self):
        """Override UserMixin, since our DB conventionally reserves 'id' for generated keys."""
        return self.uid

    def append_to_watchlist(self, student):
        self.watchlist.append(student)
        std_commit()

    def remove_from_watchlist(self, sid):
        watchlist = [s for s in self.watchlist if not s.sid == sid]
        self.watchlist = watchlist
        std_commit()

    @classmethod
    def find_by_uid(cls, uid):
        return AuthorizedUser.query.filter_by(uid=uid).first()
