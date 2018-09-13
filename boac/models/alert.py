"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from datetime import datetime
import json
import time

from boac import db, std_commit
from boac.api.errors import BadRequestError
from boac.externals import data_loch
from boac.lib.berkeley import current_term_id, term_name_for_sis_id
from boac.lib.util import camelize, utc_timestamp_to_localtime
from boac.merged.student import get_full_student_profiles, get_student_query_scope
from boac.models.base import Base
from boac.models.db_relationships import AlertView
from flask import current_app as app
from sqlalchemy import text


class Alert(Base):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    sid = db.Column(db.String(80), nullable=False)
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
    def current_alert_counts_for_viewer(cls, viewer_id):
        query = """
            SELECT alerts.sid, count(*) as alert_count
            FROM alerts LEFT JOIN alert_views
                ON alert_views.alert_id = alerts.id
                AND alert_views.viewer_id = :viewer_id
            WHERE alerts.active = true
                AND alerts.key LIKE :key
                AND alert_views.dismissed_at IS NULL
            GROUP BY alerts.sid
        """
        params = {'viewer_id': viewer_id, 'key': current_term_id() + '_%'}
        return cls.alert_counts_by_query(query, params)

    @classmethod
    def current_alert_counts_for_sids(cls, viewer_id, sids):
        query = """
            SELECT alerts.sid, count(*) as alert_count
            FROM alerts LEFT JOIN alert_views
                ON alert_views.alert_id = alerts.id
                AND alert_views.viewer_id = :viewer_id
            WHERE alerts.active = true
                AND alerts.key LIKE :key
                AND alerts.sid = ANY(:sids)
                AND alert_views.dismissed_at IS NULL
            GROUP BY alerts.sid
        """
        params = {'viewer_id': viewer_id, 'key': current_term_id() + '_%', 'sids': sids}
        return cls.alert_counts_by_query(query, params)

    @classmethod
    def alert_counts_by_query(cls, query, params):
        results = db.session.execute(text(query), params)
        alert_counts_by_sid = {row['sid']: row['alert_count'] for row in results}
        sids = list(alert_counts_by_sid.keys())

        def result_to_dict(result):
            result_dict = {
                'sid': result.get('sid'),
                'uid': result.get('uid'),
                'firstName': result.get('firstName'),
                'lastName': result.get('lastName'),
                'alertCount': alert_counts_by_sid.get(result.get('sid')),
            }
            scope = get_student_query_scope()
            if 'UWASC' in scope or 'ADMIN' in scope:
                result_dict['isActiveAsc'] = result.get('athleticsProfile', {}).get('isActiveAsc')
            return result_dict
        return [result_to_dict(result) for result in get_full_student_profiles(sids)]

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
    def infrequent_activity_alerts_enabled(cls):
        return (
            app.config['ALERT_INFREQUENT_ACTIVITY_ENABLED'] and
            not app.config['CANVAS_CURRENT_ENROLLMENT_TERM'].startswith('Summer')
        )

    @classmethod
    def no_activity_alerts_enabled(cls):
        session = data_loch.get_regular_undergraduate_session(current_term_id())[0]
        days_into_session = (datetime.date(datetime.today()) - session['session_begins']).days
        return (
            app.config['ALERT_NO_ACTIVITY_ENABLED'] and
            not app.config['CANVAS_CURRENT_ENROLLMENT_TERM'].startswith('Summer') and
            days_into_session >= app.config['ALERT_NO_ACTIVITY_DAYS_INTO_SESSION']
        )

    @classmethod
    def deactivate_all_for_term(cls, term_id):
        query = (
            cls.query.
            filter(cls.key.startswith(f'{term_id}_%'))
        )
        results = query.update({cls.active: False}, synchronize_session='fetch')
        std_commit()
        return results

    @classmethod
    def update_all_for_term(cls, term_id):
        app.logger.info('Starting alert update')
        enrollments_for_term = data_loch.get_enrollments_for_term(str(term_id))
        no_activity_alerts_enabled = cls.no_activity_alerts_enabled()
        infrequent_activity_alerts_enabled = cls.infrequent_activity_alerts_enabled()
        for row in enrollments_for_term:
            enrollments = json.loads(row['enrollment_term']).get('enrollments', [])
            for enrollment in enrollments:
                for section in enrollment['sections']:
                    if section.get('midtermGrade'):
                        cls.update_midterm_grade_alerts(row['sid'], term_id, section['ccn'], enrollment['displayName'], section['midtermGrade'])
                    for canvas_site in enrollment.get('canvasSites', []):
                        student_activity = canvas_site.get('analytics', {}).get('lastActivity', {}).get('student')
                        if not student_activity or student_activity.get('roundedUpPercentile') is None:
                            continue
                        if student_activity.get('raw') == 0:
                            if (
                                no_activity_alerts_enabled and
                                student_activity.get('roundedUpPercentile') <= app.config['ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF']
                            ):
                                cls.update_no_activity_alerts(row['sid'], term_id, canvas_site['canvasCourseId'], enrollment['displayName'])
                        else:
                            days_since = round((int(time.time()) - student_activity.get('raw')) / 86400)
                            if (
                                infrequent_activity_alerts_enabled and
                                days_since >= app.config['ALERT_INFREQUENT_ACTIVITY_DAYS'] and
                                student_activity.get('roundedUpPercentile') <= app.config['ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF']
                            ):
                                cls.update_infrequent_activity_alerts(
                                    row['sid'],
                                    term_id,
                                    canvas_site['canvasCourseId'],
                                    enrollment['displayName'],
                                    days_since,
                                )

        if app.config['ALERT_HOLDS_ENABLED'] and str(term_id) == current_term_id():
            holds = data_loch.get_sis_holds()
            for row in holds:
                hold_feed = json.loads(row['feed'])
                cls.update_hold_alerts(row['sid'], term_id, hold_feed.get('type'), hold_feed.get('reason'))
        app.logger.info('Alert update complete')

    @classmethod
    def update_assignment_alerts(cls, sid, term_id, assignment_id, due_at, status, course_site_name):
        alert_type = status + '_assignment'
        key = f'{term_id}_{assignment_id}'
        due_at_date = utc_timestamp_to_localtime(due_at).strftime('%b %-d, %Y')
        message = f'{course_site_name} assignment due on {due_at_date}.'
        cls.create_or_activate(sid=sid, alert_type=alert_type, key=key, message=message)

    @classmethod
    def update_midterm_grade_alerts(cls, sid, term_id, section_id, class_name, grade):
        key = f'{term_id}_{section_id}'
        message = f'{class_name} midterm grade of {grade}.'
        cls.create_or_activate(sid=sid, alert_type='midterm', key=key, message=message)

    @classmethod
    def update_no_activity_alerts(cls, sid, term_id, canvas_course_id, class_name):
        key = f'{term_id}_{canvas_course_id}'
        message = f'No activity! Student has yet to use the {class_name} bCourses site for {term_name_for_sis_id(term_id)}.'
        cls.create_or_activate(sid=sid, alert_type='no_activity', key=key, message=message)

    @classmethod
    def update_infrequent_activity_alerts(cls, sid, term_id, canvas_course_id, class_name, days_since):
        key = f'{term_id}_{canvas_course_id}'
        message = f'Infrequent activity! Last {class_name} bCourses activity was {days_since} days ago.'
        cls.create_or_activate(sid=sid, alert_type='infrequent_activity', key=key, message=message)

    @classmethod
    def update_hold_alerts(cls, sid, term_id, hold_type, hold_reason):
        key = f"{term_id}_{hold_type.get('code')}_{hold_reason.get('code')}"
        message = f"Hold: {hold_reason.get('description')}! {hold_reason.get('formalDescription')}."
        cls.create_or_activate(sid=sid, alert_type='hold', key=key, message=message)
