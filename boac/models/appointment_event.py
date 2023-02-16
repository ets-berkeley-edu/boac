"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from dateutil.tz import tzutc
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import desc


appointment_event_type = ENUM(
    'cancelled',
    'checked_in',
    'reserved',
    'waiting',
    name='appointment_event_types',
    create_type=False,
)


class AppointmentEvent(db.Model):
    __tablename__ = 'appointment_events'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'))
    advisor_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'))
    event_type = db.Column(appointment_event_type, nullable=False)
    cancel_reason = db.Column(db.String(255), nullable=True)
    cancel_reason_explained = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(
        self,
        appointment_id,
        user_id,
        event_type,
        advisor_id=None,
        cancel_reason=None,
        cancel_reason_explained=None,
    ):
        self.appointment_id = appointment_id
        self.user_id = user_id
        self.event_type = event_type
        self.advisor_id = advisor_id
        self.cancel_reason = cancel_reason
        self.cancel_reason_explained = cancel_reason_explained

    @classmethod
    def create(
        cls,
        appointment_id,
        user_id,
        event_type,
        advisor_id=None,
        cancel_reason=None,
        cancel_reason_explained=None,
    ):
        db.session.add(
            cls(
                appointment_id=appointment_id,
                user_id=user_id,
                event_type=event_type,
                advisor_id=advisor_id,
                cancel_reason=cancel_reason,
                cancel_reason_explained=cancel_reason_explained,
            ),
        )
        std_commit()

    @classmethod
    def get_most_recent_per_type(cls, appointment_id, event_type):
        return cls.query.filter(
            cls.appointment_id == appointment_id,
            cls.event_type == event_type,
        ).order_by(desc(cls.created_at)).limit(1).first()

    def to_api_json(self):
        return {
            'advisorId': self.advisor_id,
            'appointmentId': self.appointment_id,
            'cancelReason': self.cancel_reason,
            'cancelReasonExplained': self.cancel_reason_explained,
            'createdAt': _isoformat(self.created_at),
            'userId': self.authorized_users_id,
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
