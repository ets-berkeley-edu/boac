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
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import desc


cohort_filter_event_type = ENUM(
    'added',
    'removed',
    name='cohort_filter_event_types',
    create_type=False,
)


class CohortFilterEvent(db.Model):
    __tablename__ = 'cohort_filter_events'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    cohort_filter_id = db.Column(db.Integer, db.ForeignKey('cohort_filters.id'), nullable=False)
    sid = db.Column(db.String(80), nullable=False)
    event_type = db.Column(cohort_filter_event_type, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, cohort_filter_id, sid, event_type):
        self.cohort_filter_id = cohort_filter_id
        self.sid = sid
        self.event_type = event_type

    @classmethod
    def create_bulk(cls, cohort_filter_id, added_sids=(), removed_sids=()):
        events = [cls(cohort_filter_id=cohort_filter_id, sid=sid, event_type='added') for sid in added_sids]
        events.extend([cls(cohort_filter_id=cohort_filter_id, sid=sid, event_type='removed') for sid in removed_sids])
        db.session.bulk_save_objects(events)
        std_commit()

    @classmethod
    def events_for_cohort(cls, cohort_filter_id, offset=0, limit=50):
        count = db.session.query(func.count(cls.id)).filter_by(cohort_filter_id=cohort_filter_id).scalar()
        events = cls.query.filter_by(cohort_filter_id=cohort_filter_id).order_by(desc(cls.created_at)).offset(offset).limit(limit).all()
        return {
            'count': count,
            'events': events,
        }
