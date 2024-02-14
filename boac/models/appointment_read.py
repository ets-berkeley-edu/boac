"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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
from sqlalchemy import and_


class AppointmentRead(db.Model):
    __tablename__ = 'appointments_read'

    viewer_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False, primary_key=True)
    appointment_id = db.Column(db.String(255), nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    __table_args__ = (db.UniqueConstraint(
        'viewer_id',
        'appointment_id',
        name='appointments_read_viewer_id_appointment_id_unique_constraint',
    ),)

    def __init__(self, viewer_id, appointment_id):
        self.viewer_id = viewer_id
        self.appointment_id = appointment_id

    @classmethod
    def find_or_create(cls, viewer_id, appointment_id):
        appointment_read = cls.query.filter(and_(cls.viewer_id == viewer_id, cls.appointment_id == str(appointment_id))).one_or_none()
        if not appointment_read:
            appointment_read = cls(viewer_id, appointment_id)
            db.session.add(appointment_read)
            std_commit()
        return appointment_read

    @classmethod
    def was_read_by(cls, viewer_id, appointment_id):
        appointment_read = cls.query.filter(
            AppointmentRead.viewer_id == viewer_id,
            AppointmentRead.appointment_id == str(appointment_id),
        ).first()
        return appointment_read is not None

    @classmethod
    def get_appointments_read_by_user(cls, viewer_id, appointment_ids):
        return cls.query.filter(AppointmentRead.viewer_id == viewer_id, AppointmentRead.appointment_id.in_(appointment_ids)).all()

    @classmethod
    def when_user_read_appointment(cls, viewer_id, appointment_id):
        appointment_read = cls.query.filter(
            AppointmentRead.viewer_id == viewer_id,
            AppointmentRead.appointment_id == str(appointment_id),
        ).first()
        return appointment_read and appointment_read.created_at

    def to_api_json(self):
        return {
            'appointmentId': self.appointment_id,
            'createdAt': _isoformat(self.created_at),
            'viewerId': self.viewer_id,
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
