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
from boac.models.appointment_read import AppointmentRead
from boac.models.appointment_topic import AppointmentTopic
from boac.models.base import Base
from dateutil.tz import tzutc
from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY


class Appointment(Base):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    advisor_dept_codes = db.Column(ARRAY(db.String), nullable=True)
    advisor_name = db.Column(db.String(255), nullable=True)
    advisor_role = db.Column(db.String(255), nullable=True)
    advisor_uid = db.Column(db.String(255), nullable=True)
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
    def get_waitlist(cls, dept_code):
        # TODO: When 'dept_code' column has been added to the appointments table, add 'dept_code' to query below.
        return cls.query.filter(
            and_(
                cls.canceled_at == None,
                cls.checked_in_at == None,
                cls.deleted_at == None,
                cls.dept_code == dept_code,
            ),
        ).all()  # noqa: E711

    @classmethod
    def create(
            cls,
            created_by,
            dept_code,
            details,
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
            return appointment
        else:
            return None

    def to_api_json(self, current_user_id):
        topics = [t.to_api_json() for t in self.topics if not t.deleted_at]
        return {
            'id': self.id,
            'advisorName': self.advisor_name,
            'advisorRole': self.advisor_role,
            'advisorUid': self.advisor_uid,
            'advisorDeptCodes': self.advisor_dept_codes,
            'cancelReason': self.cancel_reason,
            'cancelReasonExplained': self.cancel_reason_explained,
            'canceledAt': _isoformat(self.canceled_at),
            'canceledBy': self.canceled_by,
            'checkedInAt': _isoformat(self.checked_in_at),
            'checkedInBy': self.checked_in_by,
            'createdAt': _isoformat(self.created_at),
            'createdBy': self.created_by,
            'dept_code': self.dept_code,
            'details': self.details,
            'read': AppointmentRead.was_read_by(current_user_id, self.id),
            'studentSid': self.student_sid,
            'topics': topics,
            'updatedAt': _isoformat(self.updated_at),
            'updatedBy': self.updated_by,
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
