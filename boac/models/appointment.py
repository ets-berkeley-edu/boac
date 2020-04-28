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

from datetime import datetime
import json
import re

from boac import db, std_commit
from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.util import (
    camelize, localize_datetime, localized_timestamp_to_utc,
    search_result_text_snippet, TEXT_SEARCH_PATTERN, titleize, utc_now, vacuum_whitespace,
)
from boac.merged import calnet
from boac.models.appointment_event import appointment_event_type, AppointmentEvent
from boac.models.appointment_read import AppointmentRead
from boac.models.appointment_topic import AppointmentTopic
from boac.models.authorized_user import AuthorizedUser
from boac.models.base import Base
from dateutil.tz import tzutc
from flask import current_app as app
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.sql import text


appointment_student_contact_type_enum = ENUM(
    'email',
    'phone',
    name='appointment_student_contact_types',
    create_type=False,
)


appointment_type_enum = ENUM(
    'Drop-in',
    'Scheduled',
    name='appointment_types',
    create_type=False,
)


class Appointment(Base):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    advisor_dept_codes = db.Column(ARRAY(db.String), nullable=True)
    advisor_name = db.Column(db.String(255), nullable=True)
    advisor_role = db.Column(db.String(255), nullable=True)
    advisor_uid = db.Column(db.String(255), nullable=True)
    appointment_type = db.Column(appointment_type_enum, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=True)
    dept_code = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    scheduled_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(appointment_event_type, nullable=False)
    student_contact_info = db.Column(db.String(255), nullable=True)
    student_contact_type = db.Column(appointment_student_contact_type_enum, nullable=True)
    student_sid = db.Column(db.String(80), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=True)
    topics = db.relationship(
        'AppointmentTopic',
        primaryjoin='and_(Appointment.id==AppointmentTopic.appointment_id, AppointmentTopic.deleted_at==None)',
        back_populates='appointment',
        order_by='AppointmentTopic.topic',
        lazy=True,
    )

    def __init__(
        self,
        appointment_type,
        created_by,
        dept_code,
        details,
        status,
        student_sid,
        updated_by,
        advisor_dept_codes=None,
        advisor_name=None,
        advisor_role=None,
        advisor_uid=None,
        scheduled_time=None,
        student_contact_info=None,
        student_contact_type=None,
    ):
        self.advisor_dept_codes = advisor_dept_codes
        self.advisor_name = advisor_name
        self.advisor_role = advisor_role
        self.advisor_uid = advisor_uid
        self.appointment_type = appointment_type
        self.created_by = created_by
        self.dept_code = dept_code
        self.details = details
        self.scheduled_time = scheduled_time
        self.status = status
        self.student_contact_info = student_contact_info
        self.student_contact_type = student_contact_type
        self.student_sid = student_sid
        self.updated_by = updated_by

    @classmethod
    def find_by_id(cls, appointment_id):
        return cls.query.filter(and_(cls.id == appointment_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def get_appointments_per_sid(cls, sid):
        return cls.query.filter(and_(cls.student_sid == sid, cls.deleted_at == None)).all()  # noqa: E711

    @classmethod
    def get_drop_in_waitlist(cls, dept_code, statuses=()):
        local_today = localize_datetime(datetime.now()).strftime('%Y-%m-%d')
        start_of_today = localized_timestamp_to_utc(f'{local_today}T00:00:00')
        criterion = and_(
            cls.created_at >= start_of_today,
            cls.appointment_type == 'Drop-in',
            cls.status.in_(statuses),
            cls.deleted_at == None,
            cls.dept_code == dept_code,
        )  # noqa: E711
        return cls.query.filter(criterion).order_by(cls.created_at).all()

    @classmethod
    def get_scheduled(cls, dept_code, local_date, advisor_uid=None):
        date_str = local_date.strftime('%Y-%m-%d')
        start_of_today = localized_timestamp_to_utc(f'{date_str}T00:00:00')
        end_of_today = localized_timestamp_to_utc(f'{date_str}T23:59:59')
        query = cls.query.filter(
            and_(
                cls.scheduled_time >= start_of_today,
                cls.scheduled_time <= end_of_today,
                cls.appointment_type == 'Scheduled',
                cls.deleted_at == None,
                cls.dept_code == dept_code,
            ),
        )  # noqa: E711
        if advisor_uid:
            query = query.filter(cls.advisor_uid == advisor_uid)
        return query.order_by(cls.scheduled_time).all()

    @classmethod
    def create(
        cls,
        created_by,
        dept_code,
        details,
        appointment_type,
        student_sid,
        advisor_attrs=None,
        topics=(),
        scheduled_time=None,
        student_contact_info=None,
        student_contact_type=None,
    ):
        # If this appointment comes in already assigned to the intake desk, we treat it as resolved.
        if advisor_attrs and advisor_attrs['role'] == 'Intake Desk':
            status = 'checked_in'
        elif advisor_attrs:
            status = 'reserved'
        else:
            status = 'waiting'

        appointment = cls(
            advisor_uid=advisor_attrs and advisor_attrs['uid'],
            advisor_name=advisor_attrs and advisor_attrs['name'],
            advisor_role=advisor_attrs and advisor_attrs['role'],
            advisor_dept_codes=advisor_attrs and advisor_attrs['deptCodes'],
            appointment_type=appointment_type,
            created_by=created_by,
            dept_code=dept_code,
            details=details,
            scheduled_time=scheduled_time,
            status=status,
            student_contact_info=student_contact_info,
            student_contact_type=student_contact_type,
            student_sid=student_sid,
            updated_by=created_by,
        )
        for topic in topics:
            appointment.topics.append(
                AppointmentTopic.create(appointment, topic),
            )
        db.session.add(appointment)
        std_commit()
        AppointmentEvent.create(
            appointment_id=appointment.id,
            advisor_id=advisor_attrs and advisor_attrs['id'],
            user_id=created_by,
            event_type=status,
        )
        cls.refresh_search_index()
        return appointment

    @classmethod
    def check_in(cls, appointment_id, checked_in_by, advisor_attrs):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            appointment.status = 'checked_in'
            appointment.advisor_uid = advisor_attrs['uid']
            appointment.advisor_name = advisor_attrs['name']
            appointment.advisor_role = advisor_attrs['role']
            appointment.advisor_dept_codes = advisor_attrs['deptCodes']
            appointment.updated_by = checked_in_by
            std_commit()
            db.session.refresh(appointment)
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=checked_in_by,
                advisor_id=advisor_attrs['id'],
                event_type='checked_in',
            )
            return appointment
        else:
            return None

    @classmethod
    def cancel(cls, appointment_id, cancelled_by, cancel_reason, cancel_reason_explained):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            event_type = 'cancelled'
            appointment.status = event_type
            appointment.updated_by = cancelled_by
            appointment.advisor_uid = None
            appointment.advisor_name = None
            appointment.advisor_role = None
            appointment.advisor_dept_codes = None
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=cancelled_by,
                event_type=event_type,
                cancel_reason=cancel_reason,
                cancel_reason_explained=cancel_reason_explained,
            )
            std_commit()
            db.session.refresh(appointment)
            cls.refresh_search_index()
            return appointment
        else:
            return None

    @classmethod
    def reserve(cls, appointment_id, reserved_by, advisor_attrs):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            event_type = 'reserved'
            appointment.status = event_type
            appointment.updated_by = reserved_by
            appointment.advisor_uid = advisor_attrs['uid']
            appointment.advisor_name = advisor_attrs['name']
            appointment.advisor_role = advisor_attrs['role']
            appointment.advisor_dept_codes = advisor_attrs['deptCodes']
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=reserved_by,
                advisor_id=advisor_attrs['id'],
                event_type=event_type,
            )
            std_commit()
            db.session.refresh(appointment)
            return appointment
        else:
            return None

    def set_to_waiting(self, updated_by):
        event_type = 'waiting'
        self.status = event_type
        self.updated_by = updated_by
        self.advisor_uid = None
        self.advisor_name = None
        self.advisor_role = None
        self.advisor_dept_codes = None
        AppointmentEvent.create(
            appointment_id=self.id,
            user_id=updated_by,
            event_type=event_type,
        )
        std_commit()
        db.session.refresh(self)

    @classmethod
    def unreserve_all_for_advisor(cls, advisor_uid, updated_by):
        appointments = cls.query.filter(and_(cls.status == 'reserved', cls.advisor_uid == advisor_uid, cls.deleted_at == None)).all()  # noqa: E711
        event_type = 'waiting'
        for appointment in appointments:
            appointment.status = event_type
            appointment.advisor_uid = None
            appointment.advisor_name = None
            appointment.advisor_role = None
            appointment.advisor_dept_codes = None
            appointment.updated_by = updated_by
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=updated_by,
                event_type=event_type,
            )
        std_commit()

    @classmethod
    def search(
        cls,
        search_phrase,
        advisor_uid=None,
        student_csid=None,
        topic=None,
        datetime_from=None,
        datetime_to=None,
        limit=20,
        offset=0,
    ):
        if search_phrase:
            search_terms = [t.group(0) for t in list(re.finditer(TEXT_SEARCH_PATTERN, search_phrase)) if t]
            search_phrase = ' & '.join(search_terms)
            fts_selector = """SELECT id, ts_rank(fts_index, plainto_tsquery('english', :search_phrase)) AS rank
                FROM appointments_fts_index
                WHERE fts_index @@ plainto_tsquery('english', :search_phrase)"""
            params = {
                'search_phrase': search_phrase,
            }
        else:
            search_terms = []
            fts_selector = 'SELECT id, 0 AS rank FROM appointments WHERE deleted_at IS NULL'
            params = {}
        if advisor_uid:
            advisor_filter = 'AND appointments.advisor_uid = :advisor_uid'
            params.update({'advisor_uid': advisor_uid})
        else:
            advisor_filter = ''

        if student_csid:
            student_filter = 'AND appointments.student_sid = :student_csid'
            params.update({'student_csid': student_csid})
        else:
            student_filter = ''

        date_filter = ''
        if datetime_from:
            date_filter += ' AND created_at >= :datetime_from'
            params.update({'datetime_from': datetime_from})
        if datetime_to:
            date_filter += ' AND created_at < :datetime_to'
            params.update({'datetime_to': datetime_to})
        if topic:
            topic_join = 'JOIN appointment_topics nt on nt.topic = :topic AND nt.appointment_id = appointments.id'
            params.update({'topic': topic})
        else:
            topic_join = ''

        query = text(f"""
            SELECT appointments.* FROM ({fts_selector}) AS fts
            JOIN appointments
                ON fts.id = appointments.id
                {advisor_filter}
                {student_filter}
                {date_filter}
            {topic_join}
            ORDER BY fts.rank DESC, appointments.id
            LIMIT {limit} OFFSET {offset}
        """).bindparams(**params)
        result = db.session.execute(query)
        keys = result.keys()
        return [_to_json(search_terms, dict(zip(keys, row))) for row in result.fetchall()]

    def update(
        self,
        updated_by,
        details=None,
        scheduled_time=None,
        student_contact_info=None,
        student_contact_type=None,
        topics=(),
    ):
        if details != self.details:
            self.updated_at = utc_now()
            self.updated_by = updated_by
        self.details = details
        self.scheduled_time = scheduled_time
        self.student_contact_info = student_contact_info
        self.student_contact_type = student_contact_type
        _update_appointment_topics(self, topics, updated_by)
        std_commit()
        db.session.refresh(self)
        self.refresh_search_index()

    @classmethod
    def refresh_search_index(cls):
        db.session.execute(text('REFRESH MATERIALIZED VIEW appointments_fts_index'))
        db.session.execute(text('REFRESH MATERIALIZED VIEW advisor_author_index'))
        std_commit()

    @classmethod
    def delete(cls, appointment_id):
        appointment = cls.find_by_id(appointment_id)
        if appointment:
            now = utc_now()
            appointment.deleted_at = now
            for topic in appointment.topics:
                topic.deleted_at = now
            std_commit()
            cls.refresh_search_index()

    def status_change_available(self):
        return self.status in ['reserved', 'waiting']

    def to_api_json(self, current_user_id):
        topics = [t.to_api_json() for t in self.topics if not t.deleted_at]
        departments = None
        if self.advisor_dept_codes:
            departments = [{'code': c, 'name': BERKELEY_DEPT_CODE_TO_NAME.get(c, c)} for c in self.advisor_dept_codes]
        api_json = {
            'id': self.id,
            'advisorId': AuthorizedUser.get_id_per_uid(self.advisor_uid),
            'advisorName': self.advisor_name,
            'advisorRole': self.advisor_role,
            'advisorUid': self.advisor_uid,
            'advisorDepartments': departments,
            'appointmentType': self.appointment_type,
            'createdAt': _isoformat(self.created_at),
            'createdBy': self.created_by,
            'deptCode': self.dept_code,
            'details': self.details,
            'read': AppointmentRead.was_read_by(current_user_id, self.id),
            'student': {
                'sid': self.student_sid,
            },
            'topics': topics,
            'updatedAt': _isoformat(self.updated_at),
            'updatedBy': self.updated_by,
        }
        if self.appointment_type == 'Scheduled':
            api_json.update({
                'scheduledTime': _isoformat(self.scheduled_time),
                'studentContactInfo': self.student_contact_info,
                'studentContactType': self.student_contact_type,
            })
        return {
            **api_json,
            **appointment_event_to_json(self.id, self.status),
        }


def appointment_event_to_json(appointment_id, event_type):
    event = AppointmentEvent.get_most_recent_per_type(
        appointment_id=appointment_id,
        event_type=event_type,
    ) if event_type else None

    def _status_by_user():
        uid = AuthorizedUser.get_uid_per_id(event.user_id)
        return {
            'id': event.user_id,
            **calnet.get_calnet_user_for_uid(app, uid),
        }
    return {
        'cancelReason': event and event.cancel_reason,
        'cancelReasonExplained': event and event.cancel_reason_explained,
        'status': event_type,
        'statusBy': event and _status_by_user(),
        'statusDate': event and _isoformat(event.created_at),
    }


def _to_json(search_terms, search_result):
    appointment_id = search_result['id']
    sid = search_result['student_sid']

    api_json = {
        'id': appointment_id,
        'advisorName': search_result['advisor_name'],
        'advisorRole': search_result['advisor_role'],
        'advisorUid': search_result['advisor_uid'],
        'advisorDeptCodes': search_result['advisor_dept_codes'],
        'createdAt': _isoformat(search_result['created_at']),
        'createdBy': search_result['created_by'],
        'deptCode': search_result['dept_code'],
        'details': search_result['details'],
        'detailsSnippet': search_result_text_snippet(search_result['details'], search_terms, TEXT_SEARCH_PATTERN),
        'studentSid': sid,
        'updatedAt': _isoformat(search_result['updated_at']),
        'updatedBy': search_result['updated_by'],
    }
    return {
        **api_json,
        **appointment_event_to_json(appointment_id, search_result['status']),
        **_student_to_json(sid),
    }


def _student_to_json(sid):
    student = data_loch.get_student_by_sid(sid)
    if student:
        return {
            'student': {camelize(key): student[key] for key in student.keys()},
        }
    profiles = data_loch.get_historical_student_profiles_for_sids([sid])
    if profiles and profiles[0]:
        return {
            'student': json.loads(profiles[0].get('profile')),
        }


def _update_appointment_topics(appointment, topics, updated_by):
    modified = False
    now = utc_now()
    topics = set([titleize(vacuum_whitespace(topic)) for topic in topics])
    existing_topics = set(appointment_topic.topic for appointment_topic in AppointmentTopic.find_by_appointment_id(appointment.id))
    topics_to_delete = existing_topics - topics
    topics_to_add = topics - existing_topics
    for topic in topics_to_delete:
        topic_to_delete = next((t for t in appointment.topics if t.topic == topic), None)
        if topic_to_delete:
            topic_to_delete.deleted_at = now
            modified = True
    for topic in topics_to_add:
        appointment.topics.append(
            AppointmentTopic.create(appointment, topic),
        )
        modified = True
    if modified:
        appointment.updated_at = now
        appointment.updated_by = updated_by


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
