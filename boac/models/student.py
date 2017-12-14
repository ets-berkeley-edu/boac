from boac import db
from boac.models.base import Base


class Student(Base):
    __tablename__ = 'students'

    sid = db.Column(db.String(80), nullable=False, primary_key=True)
    uid = db.Column(db.String(80))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    in_intensive_cohort = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Athlete {} {}, uid={}, sid={}, team_groups={}, in_intensive_cohort={}, updated={}, created={}>'.format(
            self.first_name,
            self.last_name,
            self.uid,
            self.sid,
            self.team_groups,
            self.in_intensive_cohort,
            self.updated_at,
            self.created_at,
        )

    def to_api_json(self):
        return {
            'sid': self.sid,
            'uid': self.uid,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'inIntensiveCohort': self.in_intensive_cohort,
        }
