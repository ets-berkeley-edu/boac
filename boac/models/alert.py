"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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


from datetime import datetime, timezone
import json
import re
import time

from boac import db, std_commit
from boac.api.errors import BadRequestError
from boac.externals import data_loch
from boac.lib.berkeley import section_is_eligible_for_alerts, term_name_for_sis_id
from boac.lib.util import camelize, unix_timestamp_to_localtime, utc_timestamp_to_localtime
from boac.merged.sis_terms import current_term_id
from boac.models.base import Base
from boac.models.db_relationships import AlertView
from flask import current_app as app
from sqlalchemy import text
from sqlalchemy.sql import desc


def _get_current_term_start():
    session = data_loch.get_undergraduate_term(current_term_id())[0]
    return session['term_begins']


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
        'created_at',
        name='alerts_sid_alert_type_key_created_at_unique_constraint',
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
    def current_alert_counts_for_sids(cls, viewer_id, sids, count_only=False, offset=None, limit=None):
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
            ORDER BY alert_count DESC, alerts.sid
        """
        if offset:
            query += ' OFFSET :offset'
        if limit:
            query += ' LIMIT :limit'
        params = {
            'viewer_id': viewer_id,
            'key': current_term_id() + '_%',
            'sids': sids,
            'offset': offset,
            'limit': limit,
        }
        return cls.alert_counts_by_query(query, params, count_only=count_only)

    @classmethod
    def alert_counts_by_query(cls, query, params, count_only=False):
        results = db.session.execute(text(query), params)

        # If we're only interested in the alert count, skip the student data fetch below.
        if count_only:
            return [{'sid': row['sid'], 'alertCount': row['alert_count']} for row in results]

        alert_counts_by_sid = {row['sid']: row['alert_count'] for row in results}
        sids = list(alert_counts_by_sid.keys())

        def result_to_dict(result):
            result_dict = {
                'sid': result.get('sid'),
                'uid': result.get('uid'),
                'firstName': result.get('first_name'),
                'lastName': result.get('last_name'),
                'alertCount': alert_counts_by_sid.get(result.get('sid')),
            }
            return result_dict
        return [result_to_dict(result) for result in data_loch.get_basic_student_data(sids)]

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
        feed = []

        def result_to_dict(result):
            return {camelize(key): result[key] for key in ['id', 'alert_type', 'key', 'message']}
        for result in results:
            dismissed_at = result['dismissed_at']
            alert = {
                **result_to_dict(result),
                **{
                    'dismissed': dismissed_at and dismissed_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'createdAt': result['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    'updatedAt': result['updated_at'].strftime('%Y-%m-%d %H:%M:%S'),
                },
            }
            feed.append(alert)
        return feed

    def activate(self, preserve_creation_date=False):
        self.active = True
        # Some alert types, such as withdrawals and midpoint deficient grades, don't include a time-shifted message
        # and shouldn't be treated as updated after creation.
        if preserve_creation_date:
            self.updated_at = self.created_at
        std_commit()

    def deactivate(self):
        self.active = False
        std_commit()

    @classmethod
    def create_or_activate(cls, sid, alert_type, key, message, preserve_creation_date=False):
        # If any previous alerts exist with the same type, key and sid, grab the most recently updated one.
        existing_alert = cls.query.filter_by(sid=sid, alert_type=alert_type, key=key).order_by(desc(cls.updated_at)).first()
        # If the existing alert was only just deactivated in the last two hours, assume that the deactivation was part of the
        # current refresh cycle, and go ahead and reactivate it. But if the alert was deactivated farther back in the past,
        # assume that it represents a previous state of affairs, and create a new alert for current conditions.
        if existing_alert and (datetime.now(timezone.utc) - existing_alert.updated_at).total_seconds() < (2 * 3600):
            existing_alert.message = message
            existing_alert.activate(preserve_creation_date=preserve_creation_date)
        else:
            cls.create(sid=sid, alert_type=alert_type, key=key, message=message)

    @classmethod
    def deactivate_all(cls, sid, term_id, alert_types):
        query = (
            cls.query.
            filter(cls.sid == sid).
            filter(cls.alert_type.in_(alert_types)).
            filter(cls.key.startswith(f'{term_id}_%')).
            filter(cls.active == True)  # noqa: E712
        )
        results = query.update({cls.active: False}, synchronize_session='fetch')
        std_commit()
        return results

    @classmethod
    def infrequent_activity_alerts_enabled(cls):
        if not app.config['ALERT_INFREQUENT_ACTIVITY_ENABLED']:
            return False
        if app.config['CANVAS_CURRENT_ENROLLMENT_TERM'].startswith('Summer'):
            return False
        days_into_session = (datetime.date(datetime.today()) - _get_current_term_start()).days
        return days_into_session >= app.config['ALERT_INFREQUENT_ACTIVITY_DAYS']

    @classmethod
    def no_activity_alerts_enabled(cls):
        if not app.config['ALERT_NO_ACTIVITY_ENABLED']:
            return False
        if app.config['CANVAS_CURRENT_ENROLLMENT_TERM'].startswith('Summer'):
            return False
        days_into_session = (datetime.date(datetime.today()) - _get_current_term_start()).days
        return days_into_session >= app.config['ALERT_NO_ACTIVITY_DAYS_INTO_SESSION']

    @classmethod
    def deactivate_all_for_term(cls, term_id):
        query = (
            cls.query.
            filter(cls.key.startswith(f'{term_id}_%')).
            filter(cls.active == True)  # noqa: E712
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
                cls.update_alerts_for_enrollment(row['sid'], term_id, enrollment, no_activity_alerts_enabled, infrequent_activity_alerts_enabled)
        if app.config['ALERT_WITHDRAWAL_ENABLED'] and str(term_id) == current_term_id():
            profiles = data_loch.get_student_profiles()
            for row in profiles:
                profile_feed = json.loads(row['profile'])
                if 'withdrawalCancel' in (profile_feed.get('sisProfile') or {}):
                    cls.update_withdrawal_cancel_alerts(row['sid'], term_id)
        app.logger.info('Alert update complete')

    @classmethod
    def update_alerts_for_enrollment(cls, sid, term_id, enrollment, no_activity_alerts_enabled, infrequent_activity_alerts_enabled):
        for section in enrollment['sections']:
            if section_is_eligible_for_alerts(enrollment=enrollment, section=section):
                # If the grade is in, what's done is done.
                if section.get('grade'):
                    continue
                if section.get('midtermGrade'):
                    cls.update_midterm_grade_alerts(sid, term_id, section['ccn'], enrollment['displayName'], section['midtermGrade'])
                last_activity = None
                activity_percentile = None
                for canvas_site in enrollment.get('canvasSites', []):
                    student_activity = canvas_site.get('analytics', {}).get('lastActivity', {}).get('student')
                    if not student_activity or student_activity.get('roundedUpPercentile') is None:
                        continue
                    raw_epoch = student_activity.get('raw')
                    if last_activity is None or raw_epoch > last_activity:
                        last_activity = raw_epoch
                        activity_percentile = student_activity.get('roundedUpPercentile')
                if last_activity is None:
                    continue
                if (
                    no_activity_alerts_enabled
                        and last_activity == 0
                        and activity_percentile <= app.config['ALERT_NO_ACTIVITY_PERCENTILE_CUTOFF']
                ):
                    cls.update_no_activity_alerts(sid, term_id, enrollment['displayName'])
                elif (
                    infrequent_activity_alerts_enabled
                    and last_activity > 0
                ):
                    localized_last_activity = unix_timestamp_to_localtime(last_activity).date()
                    localized_today = unix_timestamp_to_localtime(time.time()).date()
                    days_since = (localized_today - localized_last_activity).days
                    if (
                            days_since >= app.config['ALERT_INFREQUENT_ACTIVITY_DAYS']
                            and activity_percentile <= app.config['ALERT_INFREQUENT_ACTIVITY_PERCENTILE_CUTOFF']
                    ):
                        cls.update_infrequent_activity_alerts(
                            sid,
                            term_id,
                            enrollment['displayName'],
                            days_since,
                        )

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
        message = f'{class_name} midpoint deficient grade of {grade}.'
        cls.create_or_activate(sid=sid, alert_type='midterm', key=key, message=message, preserve_creation_date=True)

    @classmethod
    def update_no_activity_alerts(cls, sid, term_id, class_name):
        key = f'{term_id}_{class_name}'
        message = f'No activity! Student has never visited the {class_name} bCourses site for {term_name_for_sis_id(term_id)}.'
        cls.create_or_activate(sid=sid, alert_type='no_activity', key=key, message=message)

    @classmethod
    def update_infrequent_activity_alerts(cls, sid, term_id, class_name, days_since):
        key = f'{term_id}_{class_name}'
        message = f'Infrequent activity! Last {class_name} bCourses activity was {days_since} days ago.'
        # If an active infrequent activity alert already exists and is more recent, skip the update.
        existing_alert = cls.query.filter_by(sid=sid, alert_type='infrequent_activity', key=key, active=True).first()
        if existing_alert:
            match = re.search('(\d+) days ago.$', message)
            if match and match[1] and int(match[1]) < days_since:
                return
        cls.create_or_activate(sid=sid, alert_type='infrequent_activity', key=key, message=message)

    @classmethod
    def update_withdrawal_cancel_alerts(cls, sid, term_id):
        key = f'{term_id}_withdrawal'
        message = f'Student is no longer enrolled in the {term_name_for_sis_id(term_id)} term.'
        cls.create_or_activate(sid=sid, alert_type='withdrawal', key=key, message=message, preserve_creation_date=True)

    @classmethod
    def include_alert_counts_for_students(cls, viewer_user_id, group, count_only=False, offset=None, limit=None):
        sids = group.get('sids') if 'sids' in group else [s['sid'] for s in group.get('students', [])]
        alert_counts = cls.current_alert_counts_for_sids(viewer_user_id, sids, count_only=count_only, offset=offset, limit=limit)
        if 'students' in group:
            counts_per_sid = {s.get('sid'): s.get('alertCount') for s in alert_counts}
            for student in group.get('students'):
                sid = student['sid']
                student['alertCount'] = counts_per_sid.get(sid) if sid in counts_per_sid else 0
        return alert_counts
