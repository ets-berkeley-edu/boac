from boac import db, std_commit
from boac.models.base import Base


class NormalizedCacheStudentMajor(Base):
    __tablename__ = 'normalized_cache_student_majors'
    __table_args__ = (
        db.PrimaryKeyConstraint('sid', 'major'),
    )

    sid = db.Column(db.String(80), nullable=False, index=True)
    major = db.Column(db.String(255), nullable=False, index=True)

    def __repr__(self):
        return '<NormalizedCacheStudentMajor sid={}, major={}, updated={}, created={}>'.format(
            self.sid,
            self.major,
            self.updated_at,
            self.created_at,
        )

    @classmethod
    def distinct_majors(cls):
        return [row[0] for row in db.session.query(cls.major).distinct(cls.major).all()]

    @classmethod
    def update_majors(cls, sid, new_majors):
        existing_rows = cls.query.filter_by(sid=sid).all()
        existing_majors = []
        for row in existing_rows:
            existing_majors.append(row.major)
            if row.major not in new_majors:
                db.session.delete(row)
        for new_major in new_majors:
            if new_major not in existing_majors:
                row = cls(sid=sid, major=new_major)
                db.session.add(row)
        std_commit()
