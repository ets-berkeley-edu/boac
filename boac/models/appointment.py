"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

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
import re

from boac import db, std_commit
from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.lib.util import camelize, get_benchmarker, search_result_text_snippet, utc_now
from boac.merged import calnet
from boac.models.appointment_event import appointment_event_type, AppointmentEvent
from boac.models.appointment_read import AppointmentRead
from boac.models.appointment_topic import AppointmentTopic
from boac.models.authorized_user import AuthorizedUser
from boac.models.base import Base
from dateutil.tz import tzutc
from flask import current_app as app
import pytz
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import desc, text


APPOINTMENT_SEARCH_PATTERN = r'(\w*[.:/-@]\w+([.:/-]\w+)*)|[^\s?!(),;:.`]+'


class Appointment(Base):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    advisor_dept_codes = db.Column(ARRAY(db.String), nullable=True)
    advisor_name = db.Column(db.String(255), nullable=True)
    advisor_role = db.Column(db.String(255), nullable=True)
    advisor_uid = db.Column(db.String(255), nullable=True)
    appointment_type = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=True)
    dept_code = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    status = db.Column(appointment_event_type, nullable=False)
    student_sid = db.Column(db.String(80), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=True)
    topics = db.relationship(
        'AppointmentTopic',
        primaryjoin='and_(Appointment.id==AppointmentTopic.appointment_id, AppointmentTopic.deleted_at==None)',
        back_populates='appointment',
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
    ):
        self.advisor_dept_codes = advisor_dept_codes
        self.advisor_name = advisor_name
        self.advisor_role = advisor_role
        self.advisor_uid = advisor_uid
        self.appointment_type = appointment_type
        self.created_by = created_by
        self.dept_code = dept_code
        self.details = details
        self.status = status
        self.student_sid = student_sid
        self.updated_by = updated_by

    @classmethod
    def find_by_id(cls, appointment_id):
        return cls.query.filter(and_(cls.id == appointment_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def find_advisors_by_name(cls, tokens, limit=None):
        benchmark = get_benchmarker('appointments find_advisors_by_name')
        benchmark('begin')
        token_conditions = []
        params = {}
        for idx, token in enumerate(tokens):
            token_conditions.append(
                f"""JOIN appointments a{idx}
                ON UPPER(a{idx}.advisor_name) LIKE :token_{idx}
                AND a{idx}.advisor_uid = a.advisor_uid""",
            )
            params[f'token_{idx}'] = f'%{token}%'
        sql = f"""SELECT DISTINCT a.advisor_name, a.advisor_uid
            FROM appointments a
            {' '.join(token_conditions)}
            ORDER BY a.advisor_name"""
        if limit:
            sql += f' LIMIT {limit}'
        benchmark('execute query')
        results = db.session.execute(sql, params)
        benchmark('end')
        return results

    @classmethod
    def get_appointments_per_sid(cls, sid):
        return cls.query.filter(and_(cls.student_sid == sid, cls.deleted_at == None)).all()  # noqa: E711

    @classmethod
    def get_waitlist(cls, dept_code, statuses=()):
        start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        criterion = and_(
            cls.created_at >= start_of_today.astimezone(pytz.utc),
            cls.status.in_(statuses),
            cls.deleted_at == None,
            cls.dept_code == dept_code,
        )  # noqa: E711
        return cls.query.filter(criterion).order_by(desc(cls.created_at)).all()

    @classmethod
    def create(
            cls,
            created_by,
            dept_code,
            details,
            appointment_type,
            student_sid,
            advisor_dept_codes=None,
            advisor_name=None,
            advisor_role=None,
            advisor_uid=None,
            topics=(),
    ):

        if advisor_uid:
            status = 'reserved'
            status_by = AuthorizedUser.get_id_per_uid(advisor_uid)
        else:
            status = 'waiting'
            status_by = created_by

        appointment = cls(
            advisor_uid=advisor_uid,
            advisor_name=advisor_name,
            advisor_role=advisor_role,
            advisor_dept_codes=advisor_dept_codes,
            appointment_type=appointment_type,
            created_by=created_by,
            dept_code=dept_code,
            details=details,
            status=status,
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
            user_id=status_by,
            event_type=status,
        )
        cls.refresh_search_index()
        return appointment

    @classmethod
    def check_in(cls, appointment_id, checked_in_by, advisor_uid, advisor_name, advisor_role, advisor_dept_codes):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            appointment.status = 'checked_in'
            appointment.advisor_uid = advisor_uid
            appointment.advisor_name = advisor_name
            appointment.advisor_role = advisor_role
            appointment.advisor_dept_codes = advisor_dept_codes
            appointment.updated_by = checked_in_by
            std_commit()
            db.session.refresh(appointment)
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=checked_in_by,
                event_type='checked_in',
            )
            return appointment
        else:
            return None

    @classmethod
    def cancel(cls, appointment_id, canceled_by, cancel_reason, cancel_reason_explained):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            event_type = 'canceled'
            appointment.status = event_type
            appointment.updated_by = canceled_by
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=canceled_by,
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
    def reserve(cls, appointment_id, reserved_by):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            event_type = 'reserved'
            appointment.status = event_type
            appointment.updated_by = reserved_by
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=reserved_by,
                event_type=event_type,
            )
            std_commit()
            db.session.refresh(appointment)
            return appointment
        else:
            return None

    @classmethod
    def unreserve(cls, appointment_id, unreserved_by):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            event_type = 'waiting'
            appointment.status = event_type
            appointment.updated_by = unreserved_by
            AppointmentEvent.create(
                appointment_id=appointment.id,
                user_id=unreserved_by,
                event_type=event_type,
            )
            std_commit()
            db.session.refresh(appointment)
            return appointment
        else:
            return None

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
            search_terms = [t.group(0) for t in list(re.finditer(APPOINTMENT_SEARCH_PATTERN, search_phrase)) if t]
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
        response = [_to_json(search_terms, dict(zip(keys, row))) for row in result.fetchall()]
        return response

    @classmethod
    def refresh_search_index(cls):
        db.session.execute(text('REFRESH MATERIALIZED VIEW appointments_fts_index'))
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
        return {
            **api_json,
            **_appointment_event_to_json(self.id, self.status),
        }


def _to_json(search_terms, search_result):
    appointment_id = search_result['id']
    student = data_loch.get_student_by_sid(search_result['student_sid'])
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
        'detailsSnippet': search_result_text_snippet(search_result['details'], search_terms, APPOINTMENT_SEARCH_PATTERN),
        'student': {camelize(key): student[key] for key in student.keys()},
        'updatedAt': _isoformat(search_result['updated_at']),
        'updatedBy': search_result['updated_by'],
    }
    return {
        **api_json,
        **_appointment_event_to_json(appointment_id, search_result['status']),
    }


def _appointment_event_to_json(appointment_id, event_type):
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


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
