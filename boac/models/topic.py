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
from boac.lib.util import utc_now
from dateutil.tz import tzutc
from sqlalchemy import text


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    topic = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, topic):
        self.topic = topic

    @classmethod
    def get_all(cls, include_deleted=False):
        kwargs = {}
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
    def create_topic(cls, topic):
        topic = cls(topic=topic)
        db.session.add(topic)
        std_commit()
        return topic

    @classmethod
    def find_by_id(cls, topic_id):
        return cls.query.filter(cls.id == topic_id).first()  # noqa: E711

    @classmethod
    def get_usage_statistics(cls):
        statistics = {
            'notes': {},
        }
        query = text("""
            SELECT t.id AS topic_id, COUNT(n.id) AS count
            FROM note_topics n
            JOIN topics t ON t.topic = n.topic
            WHERE n.deleted_at IS NULL
            GROUP BY t.id, n.topic
        """)
        for row in db.session.execute(query):
            topic_id = row['topic_id']
            statistics['notes'][topic_id] = row['count']
        return statistics

    def to_api_json(self):
        return {
            'id': self.id,
            'topic': self.topic,
            'createdAt': _isoformat(self.created_at),
            'deletedAt': _isoformat(self.deleted_at),
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
