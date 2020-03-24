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

from datetime import date
from itertools import groupby

from boac import db, std_commit
from boac.models.base import Base
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
        availability_slot = cls(
            authorized_user_id=authorized_user_id,
            dept_code=dept_code,
            date_override=date_override,
            end_time=end_time,
            start_time=start_time,
            weekday=weekday,
        )
        db.session.add(availability_slot)
        std_commit()
        return availability_slot

    @classmethod
    def update(cls, id_, start_time, end_time):
        result = cls.query.filter_by(id=id_).update(start_time=start_time, end_time=end_time)
        std_commit()
        return result

    @classmethod
    def delete(cls, id_):
        result = cls.query.filter_by(id=id_).delete()
        std_commit()
        return result

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
                availability[weekday][date_key] = [a.to_api_json() for a in group_by_date_override]
        return availability

    @classmethod
    def daily_availability_for_department(cls, dept_code, date_):
        # Per distinct UID, select availability slots for the provided date if present as date_override; otherwise
        # fall back to slots with null date_override, indicating recurring per-weekday values.
        sql = """SELECT u.uid, a.start_time, a.end_time FROM appointment_availability a
                 JOIN (
                    SELECT authorized_user_id, weekday, MAX(date_override) AS date_override
                    FROM appointment_availability
                    WHERE weekday = :weekday AND (date_override = :date_ OR date_override IS NULL)
                    GROUP BY authorized_user_id, weekday
                ) t
                ON a.authorized_user_id = t.authorized_user_id
                AND a.weekday = t.weekday
                AND (a.date_override = t.date_override OR (a.date_override IS NULL AND t.date_override IS NULL))
                JOIN authorized_users u on a.authorized_user_id = u.id
                ORDER BY uid, start_time"""
        results = db.session.execute(text(sql), {'date_': str(date_), 'weekday': date_.strftime('%a')})
        availability = {}
        for uid, group_by_uid in groupby(results, lambda x: x.uid):
            availability[uid] = [a.to_api_json() for a in group_by_uid]
        return availability

    def to_api_json(self):
        return {
            'startTime': str(self.start_time) if self.start_time else None,
            'endTime': str(self.end_time) if self.end_time else None,
        }
