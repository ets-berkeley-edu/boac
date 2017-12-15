from boac import db
from boac.models.base import Base


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
