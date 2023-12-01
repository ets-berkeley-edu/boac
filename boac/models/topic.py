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
from boac.lib.util import utc_now
from dateutil.tz import tzutc
from sqlalchemy import text


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    topic = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)
    available_in_notes = db.Column(db.Boolean, nullable=False)
    available_in_appointments = db.Column(db.Boolean, nullable=False)

    def __init__(self, topic, available_in_notes, available_in_appointments):
        self.topic = topic
        self.available_in_notes = available_in_notes
        self.available_in_appointments = available_in_appointments

    @classmethod
    def get_all(cls, available_in_notes=None, available_in_appointments=None, include_deleted=False):
        kwargs = {}
        if available_in_appointments is not None:
            kwargs['available_in_appointments'] = available_in_appointments
        if available_in_notes is not None:
            kwargs['available_in_notes'] = available_in_notes
        if not include_deleted:
            kwargs['deleted_at'] = None

        return cls.query.filter_by(**kwargs).order_by(cls.topic).all()

    @classmethod
    def delete(cls, topic_id):
        topic = cls.query.filter_by(id=topic_id, deleted_at=None).first()
        if topic:
            now = utc_now()
            topic.deleted_at = now
            std_commit()

    @classmethod
    def undelete(cls, topic_id):
        topic = cls.query.filter_by(id=topic_id).first()
        if topic:
            topic.deleted_at = None
            std_commit()

    @classmethod
    def create_topic(cls, topic, available_in_appointments=False, available_in_notes=False):
        topic = cls(
            topic=topic,
            available_in_notes=available_in_notes,
            available_in_appointments=available_in_appointments,
        )
        db.session.add(topic)
        std_commit()
        return topic

    @classmethod
    def update_topic(cls, topic_id, topic, available_in_appointments=False, available_in_notes=False):
        existing = cls.find_by_id(topic_id=topic_id)
        existing.topic = topic
        existing.available_in_appointments = available_in_appointments
        existing.available_in_notes = available_in_notes
        std_commit()
        return existing

    @classmethod
    def find_by_id(cls, topic_id):
        return cls.query.filter(cls.id == topic_id).first()  # noqa: E711

    @classmethod
    def get_usage_statistics(cls):
        statistics = {}
        for usage_type in ('appointment', 'note'):
            query = text(f"""
                SELECT t.id AS topic_id, COUNT(n.id)
                FROM {usage_type}_topics n
                JOIN topics t ON t.topic = n.topic
                WHERE n.deleted_at IS NULL
                GROUP BY t.id, n.topic
            """)
            key = f'{usage_type}s'
            statistics[key] = {}
            for row in db.session.execute(query):
                topic_id = row['topic_id']
                statistics[key][topic_id] = row['count']
        return statistics

    def to_api_json(self):
        return {
            'id': self.id,
            'availableInAppointments': self.available_in_appointments,
            'availableInNotes': self.available_in_notes,
            'topic': self.topic,
            'createdAt': _isoformat(self.created_at),
            'deletedAt': _isoformat(self.deleted_at),
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
