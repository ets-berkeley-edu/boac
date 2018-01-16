import csv
from datetime import datetime

from boac import db, std_commit


"""
This base model class defines common behavior inherited by all database-backed models. Here the
only such common behavior is timestamp columns.
"""


class Base(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def load_csv(cls, filename):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for csvrow in reader:
                record = cls(**csvrow)
                db.session.add(record)
        std_commit()
