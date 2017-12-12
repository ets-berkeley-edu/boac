from boac import db
from boac.models.base import Base


student_athletes = db.Table(
    'student_athletes',
    Base.metadata,
    db.Column('group_code', db.String(80), db.ForeignKey('athletics.group_code'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


class Athletics(Base):
    __tablename__ = 'athletics'

    group_code = db.Column(db.String(80), nullable=False, primary_key=True)
    group_name = db.Column(db.String(255))
    team_code = db.Column(db.String(80))
    team_name = db.Column(db.String(255))
    members = db.relationship('Student', secondary=student_athletes, back_populates='teams')

    def __repr__(self):
        return '<TeamGroup {} ({}), team {} ({}), updated={}, created={}>'.format(
            self.group_name,
            self.group_code,
            self.team_code,
            self.team_name,
            self.updated_at,
            self.created_at,
        )
