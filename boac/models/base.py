from datetime import datetime

from boac import db


"""
This base model class defines common behavior inherited by all database-backed models. Here the
only such common behavior is timestamp columns.
"""


class Base(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
