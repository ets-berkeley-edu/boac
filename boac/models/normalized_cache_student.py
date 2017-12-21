from boac import db
from boac.models.base import Base
from flask import current_app as app


class NormalizedCacheStudent(Base):
    __tablename__ = 'normalized_cache_students'

    sid = db.Column(db.String(80), nullable=False, primary_key=True)
    gpa = db.Column(db.Numeric, nullable=True, index=True)
    level = db.Column(db.String(9), nullable=True, index=True)
    units = db.Column(db.Numeric, nullable=True, index=True)

    def __repr__(self):
        return '<NormalizedCacheStudent sid={}, gpa={}, level={}, units={}, created={}>'.format(
            self.sid,
            self.gpa,
            self.level,
            self.updated_at,
            self.created_at,
        )

    @classmethod
    def update_profile(cls, sid, gpa=None, level=None, units=None):
        row = cls.query.filter_by(sid=sid).first()
        if row:
            row.gpa = gpa
            row.level = level
            row.units = units
        else:
            row = cls(sid=sid, gpa=gpa, level=level, units=units)
            db.session.add(row)
        if not app.config['TESTING']:
            db.session.commit()
