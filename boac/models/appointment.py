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

from boac import db, std_commit
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_NAME
from boac.merged.calnet import get_uid_for_csid
from boac.models.appointment_read import AppointmentRead
from boac.models.appointment_topic import AppointmentTopic
from boac.models.base import Base
from dateutil.tz import tzutc
from flask import current_app as app
import pytz
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import desc, text


class Appointment(Base):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    advisor_dept_codes = db.Column(ARRAY(db.String), nullable=True)
    advisor_name = db.Column(db.String(255), nullable=True)
    advisor_role = db.Column(db.String(255), nullable=True)
    advisor_uid = db.Column(db.String(255), nullable=True)
    appointment_type = db.Column(db.String(255), nullable=True)
    cancel_reason = db.Column(db.String(255), nullable=True)
    cancel_reason_explained = db.Column(db.String(255), nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)
    canceled_by = db.Column(db.String(255), nullable=True)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    checked_in_by = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.String(255), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.String(255), nullable=True)
    dept_code = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    student_sid = db.Column(db.String(80), nullable=False)
    updated_by = db.Column(db.String(255), nullable=False)
    topics = db.relationship(
        'AppointmentTopic',
        primaryjoin='and_(Appointment.id==AppointmentTopic.appointment_id, AppointmentTopic.deleted_at==None)',
        back_populates='appointment',
        lazy=True,
    )

    def __init__(
        self,
        advisor_dept_codes,
        advisor_name,
        advisor_role,
        advisor_uid,
        appointment_type,
        created_by,
        dept_code,
        details,
        student_sid,
        updated_by,
    ):
        self.advisor_dept_codes = advisor_dept_codes
        self.advisor_name = advisor_name
        self.advisor_role = advisor_role
        self.advisor_uid = advisor_uid
        self.appointment_type = appointment_type
        self.created_by = created_by
        self.dept_code = dept_code
        self.details = details
        self.student_sid = student_sid
        self.updated_by = updated_by

    @classmethod
    def find_by_id(cls, appointment_id):
        return cls.query.filter(and_(cls.id == appointment_id, cls.deleted_at == None)).first()  # noqa: E711

    @classmethod
    def get_appointments_per_sid(cls, sid):
        return cls.query.filter(and_(cls.student_sid == sid, cls.deleted_at == None)).all()  # noqa: E711

    @classmethod
    def get_waitlist(cls, dept_code, include_resolved=False):
        if include_resolved:
            start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            criterion = and_(
                cls.created_at >= start_of_today.astimezone(pytz.utc),
                cls.deleted_at == None,
                cls.dept_code == dept_code,
            )  # noqa: E711
        else:
            criterion = and_(
                cls.canceled_at == None,
                cls.checked_in_at == None,
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
            topics=(),
            advisor_dept_codes=None,
            advisor_name=None,
            advisor_role=None,
            advisor_uid=None,
    ):
        appointment = cls(
            advisor_dept_codes,
            advisor_name,
            advisor_role,
            advisor_uid,
            appointment_type,
            created_by,
            dept_code,
            details,
            student_sid,
            updated_by=created_by,
        )
        for topic in topics:
            appointment.topics.append(
                AppointmentTopic.create(appointment, topic),
            )
        db.session.add(appointment)
        std_commit()
        cls.refresh_search_index()
        return appointment

    @classmethod
    def check_in(cls, appointment_id, checked_in_by, advisor_uid, advisor_name, advisor_role, advisor_dept_codes):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            appointment.checked_in_at = datetime.now()
            appointment.checked_in_by = checked_in_by
            appointment.advisor_uid = advisor_uid
            appointment.advisor_name = advisor_name
            appointment.advisor_role = advisor_role
            appointment.advisor_dept_codes = advisor_dept_codes
            appointment.updated_by = checked_in_by
            std_commit()
            db.session.refresh(appointment)
            return appointment
        else:
            return None

    @classmethod
    def cancel(cls, appointment_id, canceled_by, cancel_reason, cancel_reason_explained):
        appointment = cls.find_by_id(appointment_id=appointment_id)
        if appointment:
            appointment.canceled_at = datetime.now()
            appointment.canceled_by = canceled_by
            appointment.cancel_reason = cancel_reason
            appointment.cancel_reason_explained = cancel_reason_explained
            appointment.updated_by = canceled_by
            std_commit()
            db.session.refresh(appointment)
            cls.refresh_search_index()
            return appointment
        else:
            return None

    @classmethod
    def search(
        cls,
        search_phrase,
        advisor_csid=None,
        student_csid=None,
        topic=None,
        datetime_from=None,
        datetime_to=None,
        limit=20,
        offset=0,
    ):
        if search_phrase:
            fts_selector = """SELECT id, ts_rank(fts_index, plainto_tsquery('english', :search_phrase)) AS rank
                FROM appointments_fts_index
                WHERE fts_index @@ plainto_tsquery('english', :search_phrase)"""
            params = {
                'search_phrase': search_phrase,
            }
        else:
            fts_selector = 'SELECT id, 0 AS rank FROM appointments WHERE deleted_at IS NULL'
            params = {}
        if advisor_csid:
            advisor_uid = get_uid_for_csid(app, advisor_csid)
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
            date_filter += ' AND updated_at >= :datetime_from'
            params.update({'datetime_from': datetime_from})
        if datetime_to:
            date_filter += ' AND updated_at < :datetime_to'
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
        response = [_to_json(dict(zip(keys, row))) for row in result.fetchall()]
        return response

    @classmethod
    def refresh_search_index(cls):
        db.session.execute(text('REFRESH MATERIALIZED VIEW appointments_fts_index'))
        std_commit()

    def to_api_json(self, current_user_id):
        topics = [t.to_api_json() for t in self.topics if not t.deleted_at]
        departments = None
        if self.advisor_dept_codes:
            departments = [{'code': c, 'name': BERKELEY_DEPT_CODE_TO_NAME.get(c, c)} for c in self.advisor_dept_codes]
        return {
            'id': self.id,
            'advisorName': self.advisor_name,
            'advisorRole': self.advisor_role,
            'advisorUid': self.advisor_uid,
            'advisorDepartments': departments,
            'appointmentType': self.appointment_type,
            'cancelReason': self.cancel_reason,
            'cancelReasonExplained': self.cancel_reason_explained,
            'canceledAt': _isoformat(self.canceled_at),
            'canceledBy': self.canceled_by,
            'checkedInAt': _isoformat(self.checked_in_at),
            'checkedInBy': self.checked_in_by,
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


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()


def _to_json(search_result):
    return {
        'id': search_result['id'],
        'advisorName': search_result['advisor_name'],
        'advisorRole': search_result['advisor_role'],
        'advisorUid': search_result['advisor_uid'],
        'advisorDeptCodes': search_result['advisor_dept_codes'],
        'cancelReason': search_result['cancel_reason'],
        'cancelReasonExplained': search_result['cancel_reason_explained'],
        'canceledAt': _isoformat(search_result['canceled_at']),
        'canceledBy': search_result['canceled_by'],
        'checkedInAt': _isoformat(search_result['checked_in_at']),
        'checkedInBy': search_result['checked_in_by'],
        'createdAt': _isoformat(search_result['created_at']),
        'createdBy': search_result['created_by'],
        'dept_code': search_result['dept_code'],
        'details': search_result['details'],
        'student': {
            'sid': search_result['student_sid'],
        },
        'updatedAt': _isoformat(search_result['updated_at']),
        'updatedBy': search_result['updated_by'],
    }
