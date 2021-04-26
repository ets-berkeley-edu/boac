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

from datetime import datetime

from boac import db, std_commit
from sqlalchemy import ForeignKeyConstraint


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


class DegreeProgressCategoryCourse(db.Model):
    __tablename__ = 'degree_progress_category_courses'

    category_id = db.Column(db.Integer, db.ForeignKey('degree_progress_categories.id'), primary_key=True)
    section_id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(80), primary_key=True)
    term_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    category = db.relationship('DegreeProgressCategory', back_populates='courses')
    course = db.relationship('DegreeProgressCourse', back_populates='categories')

    __table_args__ = (
        ForeignKeyConstraint(
            (section_id, sid, term_id),
            ['degree_progress_courses.section_id', 'degree_progress_courses.sid', 'degree_progress_courses.term_id'],
        ),
    )

    def __init__(self, category_id, section_id, sid, term_id):
        self.category_id = category_id
        self.section_id = section_id
        self.sid = sid
        self.term_id = term_id

    @classmethod
    def create(cls, category_id, section_id, sid, term_id):
        db.session.add(cls(category_id=category_id, section_id=section_id, sid=sid, term_id=term_id))
        std_commit()

    @classmethod
    def delete_all(cls, section_id, sid, term_id):
        for mapping in cls.query.filter_by(section_id=section_id, sid=sid, term_id=term_id).all():
            db.session.delete(mapping)
        std_commit()
