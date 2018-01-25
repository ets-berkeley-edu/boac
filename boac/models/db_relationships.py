from datetime import datetime

from boac import db
from boac.models.base import Base


advisor_watchlists = db.Table(
    'advisor_watchlists',
    Base.metadata,
    db.Column('watchlist_owner_uid', db.String(80), db.ForeignKey('authorized_users.uid'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


student_athletes = db.Table(
    'student_athletes',
    Base.metadata,
    db.Column('group_code', db.String(80), db.ForeignKey('athletics.group_code'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


cohort_filter_owners = db.Table(
    'cohort_filter_owners',
    Base.metadata,
    db.Column('cohort_filter_id', db.Integer, db.ForeignKey('cohort_filters.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True),
)


# Alert views are represented as a model class because they contain 'created_at' and 'dismissed_at' metadata in
# addition to join columns.
# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-object
class AlertView(db.Model):
    __tablename__ = 'alert_views'

    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), primary_key=True)
    viewer_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    dismissed_at = db.Column(db.DateTime)
    viewer = db.relationship('AuthorizedUser', back_populates='alert_views')
    alert = db.relationship('Alert', back_populates='views')
