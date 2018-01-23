"""This package integrates with Flask-Login. Determine who can use the app and which privileges they have."""
from datetime import datetime

from boac import db, std_commit
from boac.api.errors import BadRequestError
from boac.models.base import Base
from boac.models.db_relationships import advisor_watchlists, AlertView, cohort_filter_owners
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

    def dismiss_alert(self, alert_id):
        alert_view = AlertView.query.filter_by(viewer_id=self.id, alert_id=alert_id, dismissed_at=None).first()
        if alert_view:
            alert_view.dismissed_at = datetime.now()
            std_commit()
        else:
            raise BadRequestError(f'No current alert view found for alert {alert_id} and UID {self.uid}')

    @classmethod
    def find_by_uid(cls, uid):
        return AuthorizedUser.query.filter_by(uid=uid).first()
