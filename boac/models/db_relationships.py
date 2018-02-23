"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import db
from boac.models.base import Base


advisor_watchlists = db.Table(
    'advisor_watchlists',
    Base.metadata,
    db.Column('watchlist_owner_uid', db.String(80), db.ForeignKey('authorized_users.uid'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


student_athletes = db.Table(
    'student_athletes',
    Base.metadata,
    db.Column('group_code', db.String(80), db.ForeignKey('athletics.group_code'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


cohort_filter_owners = db.Table(
    'cohort_filter_owners',
    Base.metadata,
    db.Column('cohort_filter_id', db.Integer, db.ForeignKey('cohort_filters.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True),
)


student_enrollments = db.Table(
    'normalized_cache_enrollments',
    Base.metadata,
    db.Column('term_id', db.Integer, db.ForeignKey('normalized_cache_course_sections.term_id'), primary_key=True),
    db.Column('section_id', db.String(80), db.ForeignKey('normalized_cache_course_sections.section_id'), primary_key=True),
    db.Column('sid', db.String(80), db.ForeignKey('students.sid'), primary_key=True),
)


# Alert views are represented as a model class because they contain 'created_at' and 'dismissed_at' metadata in
# addition to join columns.
# http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#association-object
class AlertView(db.Model):
    __tablename__ = 'alert_views'

    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), primary_key=True)
    viewer_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    dismissed_at = db.Column(db.DateTime)
    viewer = db.relationship('AuthorizedUser', back_populates='alert_views')
    alert = db.relationship('Alert', back_populates='views')
