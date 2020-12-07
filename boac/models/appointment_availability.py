"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from datetime import date, datetime, time, timedelta
from itertools import groupby

from boac import db, std_commit
from boac.models.base import Base
from dateutil.tz import tzutc
from flask import current_app as app
import pytz
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql.expression import nullsfirst


weekday_types_enum = ENUM(
    *[date(2001, 1, i + 1).strftime('%a') for i in range(7)],
    name='weekday_types',
    create_type=False,
)


class AppointmentAvailability(Base):
    __tablename__ = 'appointment_availability'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    authorized_user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    dept_code = db.Column(db.String(80), nullable=False)
    weekday = db.Column(weekday_types_enum, nullable=False)
    # A null date_override indicates a recurring weekday value.
    date_override = db.Column(db.Date, nullable=True)
    # A null start_time and end_time indicates unavailability for the day (meaningful only when date_override is not null).
    start_time = db.Column(db.Date, nullable=True)
    end_time = db.Column(db.Date, nullable=True)

    def __init__(
        self,
        authorized_user_id,
        dept_code,
        start_time,
        end_time,
        weekday,
        date_override,
    ):
        self.authorized_user_id = authorized_user_id
        self.dept_code = dept_code
        self.start_time = start_time
        self.end_time = end_time
        self.weekday = weekday
        self.date_override = date_override

    @classmethod
    def create(
        cls,
        authorized_user_id,
        dept_code,
        start_time,
        end_time,
        weekday=None,
        date_override=None,
    ):
        start_time, end_time = cls._parse_and_validate(start_time, end_time, allow_null=(date_override is not None))
        slot = cls(
            authorized_user_id=authorized_user_id,
            dept_code=dept_code,
            date_override=date_override,
            end_time=end_time,
            start_time=start_time,
            weekday=weekday,
        )
        db.session.add(slot)
        std_commit()
        cls._merge_overlaps(slot.authorized_user_id, slot.dept_code, slot.weekday, slot.date_override)
        return True

    @classmethod
    def update(cls, id_, start_time, end_time):
        start_time, end_time = cls._parse_and_validate(start_time, end_time, allow_null=False)
        slot = cls.query.filter_by(id=id_).first()
        slot.start_time = start_time
        slot.end_time = end_time
        std_commit()
        db.session.refresh(slot)
        cls._merge_overlaps(slot.authorized_user_id, slot.dept_code, slot.weekday, slot.date_override)
        return True

    @classmethod
    def delete(cls, id_):
        db.session.execute(cls.__table__.delete().where(cls.id == id_))
        std_commit()
        return True

    @classmethod
    def availability_for_advisor(cls, authorized_user_id, dept_code):
        results = cls.query.filter_by(authorized_user_id=authorized_user_id, dept_code=dept_code).order_by(
            cls.weekday,
            nullsfirst(cls.date_override),
            cls.start_time,
        )
        availability = {}
        for weekday, group_by_weekday in groupby(results, lambda x: x.weekday):
            availability[weekday] = {}
            for date_key, group_by_date_override in groupby(group_by_weekday, lambda x: x.date_override):
                if date_key is None:
                    date_key = 'recurring'
                else:
                    date_key = str(date_key)
                availability[weekday][date_key] = [cls.to_api_json(a.id, a.start_time, a.end_time) for a in group_by_date_override]
        return availability

    @classmethod
    def daily_availability_for_department(cls, dept_code, date_):
        results = cls._query_availability(dept_code, date_)
        availability = {}
        for uid, group_by_uid in groupby(results, lambda x: x.uid):
            availability_for_uid = [cls.to_api_json(a['id'], a['start_time'], a['end_time']) for a in group_by_uid if a['start_time']]
            if len(availability_for_uid):
                availability[uid] = availability_for_uid
        return availability

    @classmethod
    def get_openings(cls, dept_code, date_, appointments):
        results = cls._query_availability(dept_code, date_)
        openings = []
        for uid, group_by_uid in groupby(results, lambda x: x.uid):
            for a in group_by_uid:
                if a['start_time'] and a['end_time']:
                    start_opening = datetime.combine(date_, a['start_time']).replace(tzinfo=date_.tzinfo).astimezone(pytz.utc)
                    end_availability = datetime.combine(date_, a['end_time']).replace(tzinfo=date_.tzinfo).astimezone(pytz.utc)
                    while (end_availability - start_opening).total_seconds() >= app.config['SCHEDULED_APPOINTMENT_LENGTH'] * 60:
                        end_opening = start_opening + timedelta(minutes=app.config['SCHEDULED_APPOINTMENT_LENGTH'])
                        start_time_str = _isoformat(start_opening)
                        if next((a for a in appointments if a['scheduledTime'] == start_time_str and a['advisorUid'] == uid), None) is None:
                            openings.append({
                                'uid': uid,
                                'startTime': start_time_str,
                                'endTime': str(end_opening),
                            })
                        start_opening = end_opening
        return sorted(openings, key=lambda i: (i['startTime'], i['uid']))

    @classmethod
    def _query_availability(cls, dept_code, date_):
        # Per distinct UID, select availability slots for the provided date if present as date_override; otherwise
        # fall back to slots with null date_override, indicating recurring per-weekday values.
        sql = """SELECT u.uid, a.id, a.start_time, a.end_time FROM appointment_availability a
                 JOIN (
                    SELECT authorized_user_id, weekday, dept_code, MAX(date_override) AS date_override
                    FROM appointment_availability
                    WHERE weekday = :weekday
                        AND dept_code = :dept_code
                        AND (date_override = :date_ OR date_override IS NULL)
                    GROUP BY authorized_user_id, weekday, dept_code
                ) t
                ON a.authorized_user_id = t.authorized_user_id
                AND a.weekday = t.weekday
                AND a.dept_code = t.dept_code
                AND (a.date_override = t.date_override OR (a.date_override IS NULL AND t.date_override IS NULL))
                JOIN authorized_users u on a.authorized_user_id = u.id
                ORDER BY uid, start_time"""
        return db.session.execute(text(sql), {'date_': str(date_), 'weekday': date_.strftime('%a'), 'dept_code': dept_code})

    @classmethod
    def to_api_json(cls, id_, start_time, end_time):
        return {
            'id': id_,
            'startTime': start_time and str(start_time),
            'endTime': start_time and str(end_time),
        }

    @classmethod
    def _parse_and_validate(cls, start_time, end_time, allow_null):
        if start_time is None and (not allow_null or end_time is not None):
            raise ValueError('Start time cannot be null')
        elif end_time is None and (not allow_null or end_time is not None):
            raise ValueError('End time cannot be null')
        elif start_time is None and end_time is None:
            return None, None
        try:
            start_time = time(*[int(i) for i in start_time.split(':')])
        except Exception:
            raise ValueError('Could not parse start time')
        try:
            end_time = time(*[int(i) for i in end_time.split(':')])
        except Exception:
            raise ValueError('Could not parse end time')
        if start_time >= end_time:
            raise ValueError('Start time must be before end time')
        return start_time, end_time

    @classmethod
    def _merge_overlaps(cls, authorized_user_id, dept_code, weekday, date_override):
        previous_slot = None
        for slot in cls.query.filter_by(
            authorized_user_id=authorized_user_id,
            dept_code=dept_code,
            weekday=weekday,
            date_override=date_override,
        ).order_by(cls.start_time):
            if previous_slot is not None and previous_slot.end_time >= slot.start_time:
                if previous_slot.end_time < slot.end_time:
                    previous_slot.end_time = slot.end_time
                db.session.delete(slot)
            else:
                previous_slot = slot
        std_commit()


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
