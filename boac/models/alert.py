from datetime import datetime

from boac import db, std_commit
from boac.api.errors import BadRequestError
from boac.lib.berkeley import current_term_id
from boac.lib.util import camelize
from boac.models.base import Base
from boac.models.db_relationships import AlertView
from flask import current_app as app
import pytz
from sqlalchemy import text


class Alert(Base):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    sid = db.Column(db.String(80), db.ForeignKey('students.sid'), nullable=False)
    alert_type = db.Column(db.String(80), nullable=False)
    key = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    views = db.relationship(
        'AlertView',
        back_populates='alert',
        lazy=True,
    )

    __table_args__ = (db.UniqueConstraint(
        'sid',
        'alert_type',
        'key',
        name='alerts_sid_alert_type_key_unique_constraint',
    ),)

    @classmethod
    def create(cls, sid, alert_type, key=None, message=None, active=True):
        # Alerts must contain a key, unique per SID and alert type, which will allow them to be located
        # and modified on updates to the data that originally generated the alert. The key defaults
        # to a string representation of today's date, but will more often (depending on the alert type)
        # contain a reference to a related resource, such as a course or assignment id.
        if key is None:
            key = datetime.now().strftime('%Y-%m-%d')
        else:
            # If we get a blank string as key, deliver a stern warning to the code that submitted it.
            key = key.strip()
            if not key:
                raise ValueError('Blank string submitted for alert key')
        alert = cls(sid, alert_type, key, message, active)
        db.session.add(alert)
        std_commit()

    def __init__(self, sid, alert_type, key, message=None, active=True):
        self.sid = sid
        self.alert_type = alert_type
        self.key = key
        self.message = message
        self.active = active

    def __repr__(self):
        return f"""<Alert {self.id},
                    sid={self.sid},
                    alert_type={self.alert_type},
                    key={self.key},
                    message={self.message},
                    active={self.active},
                    updated={self.updated_at},
                    created={self.created_at}>
                """

    @classmethod
    def dismiss(cls, alert_id, viewer_id):
        alert = cls.query.filter_by(id=alert_id).first()
        if alert:
            alert_view = AlertView.query.filter_by(viewer_id=viewer_id, alert_id=alert_id).first()
            if alert_view:
                alert_view.dismissed_at = datetime.now()
            else:
                db.session.add(AlertView(viewer_id=viewer_id, alert_id=alert_id, dismissed_at=datetime.now()))
            std_commit()
        else:
            raise BadRequestError(f'No alert found for id {alert_id}')

    @classmethod
    def current_alert_counts_for_sids(cls, viewer_id, sids):
        query = text("""
            SELECT * FROM students s JOIN (
                SELECT alerts.sid, count(*) as alert_count
                FROM alerts LEFT JOIN alert_views
                    ON alert_views.alert_id = alerts.id
                    AND alert_views.viewer_id = :viewer_id
                WHERE alerts.active = true
                    AND alerts.key LIKE :key
                    AND alert_views.dismissed_at IS NULL
                GROUP BY alerts.sid
            ) alert_counts
            ON s.sid = alert_counts.sid
                AND s.sid = ANY(:sids)
            ORDER BY s.last_name
        """)
        results = db.session.execute(query, {'viewer_id': viewer_id, 'key': current_term_id() + '_%', 'sids': sids})

        def result_to_dict(result):
            return {camelize(key): result[key] for key in ['sid', 'uid', 'first_name', 'last_name', 'alert_count']}
        return [result_to_dict(result) for result in results]

    @classmethod
    def current_alerts_for_sid(cls, viewer_id, sid):
        query = text("""
            SELECT alerts.*, alert_views.dismissed_at
            FROM alerts LEFT JOIN alert_views
                ON alert_views.alert_id = alerts.id
                AND alert_views.viewer_id = :viewer_id
            WHERE alerts.active = true
                AND alerts.key LIKE :key
                AND alerts.sid = :sid
            ORDER BY alerts.created_at
        """)
        results = db.session.execute(query, {'viewer_id': viewer_id, 'key': current_term_id() + '_%', 'sid': sid})

        def result_to_dict(result):
            return {camelize(key): result[key] for key in ['id', 'alert_type', 'key', 'message']}
        feed = {
            'dismissed': [],
            'shown': [],
        }
        for result in results:
            if result['dismissed_at']:
                feed['dismissed'].append(result_to_dict(result))
            else:
                feed['shown'].append(result_to_dict(result))
        return feed

    def activate(self):
        self.active = True
        std_commit()

    def deactivate(self):
        self.active = False
        std_commit()

    @classmethod
    def create_or_activate(cls, sid, alert_type, key, message):
        existing_alert = cls.query.filter_by(sid=sid, alert_type=alert_type, key=key).first()
        if existing_alert:
            existing_alert.message = message
            existing_alert.activate()
        else:
            cls.create(sid=sid, alert_type=alert_type, key=key, message=message)

    @classmethod
    def deactivate_all(cls, sid, term_id, alert_types):
        query = (
            cls.query.
            filter(cls.sid == sid).
            filter(cls.alert_type.in_(alert_types)).
            filter(cls.key.startswith(f'{term_id}_%'))
        )
        results = query.update({cls.active: False}, synchronize_session='fetch')
        std_commit()
        return results

    @classmethod
    def update_assignment_alerts(cls, sid, term_id, assignment_id, due_at, status, course_site_name):
        alert_type = status + '_assignment'
        key = f'{term_id}_{assignment_id}'
        due_at_datetime = pytz.utc.localize(datetime.strptime(due_at, '%Y-%m-%dT%H:%M:%SZ'))
        due_at_date = due_at_datetime.astimezone(pytz.timezone(app.config['TIMEZONE'])).strftime('%b %-d, %Y')
        message = f'{course_site_name} assignment due on {due_at_date}.'
        cls.create_or_activate(sid=sid, alert_type=alert_type, key=key, message=message)

    @classmethod
    def update_midterm_grade_alerts(cls, sid, term_id, section_id, class_name, grade):
        key = f'{term_id}_{section_id}'
        message = f'{class_name} midterm grade of {grade}.'
        cls.create_or_activate(sid=sid, alert_type='midterm', key=key, message=message)
