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
from boac.models.base import Base
from boac.models.university_dept import UniversityDept


cohort_filter_owners = db.Table(
    'cohort_filter_owners',
    Base.metadata,
    db.Column('cohort_filter_id', db.Integer, db.ForeignKey('cohort_filters.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True),
)


class CuratedCohortStudent(db.Model):
    __tablename__ = 'student_group_members'

    curated_cohort_id = db.Column('student_group_id', db.Integer, db.ForeignKey('student_groups.id'), primary_key=True)
    sid = db.Column('sid', db.String(80), primary_key=True)
    curated_cohort = db.relationship('CuratedCohort', back_populates='students')


class UniversityDeptMember(Base):
    __tablename__ = 'university_dept_members'

    university_dept_id = db.Column(db.Integer, db.ForeignKey('university_depts.id'), primary_key=True)
    authorized_user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True)
    is_advisor = db.Column(db.Boolean, nullable=False)
    is_director = db.Column(db.Boolean, nullable=False)
    authorized_user = db.relationship('AuthorizedUser', back_populates='department_memberships')
    # Pre-load UniversityDept below to avoid 'failed to locate', as seen during routes.py init phase
    university_dept = db.relationship(UniversityDept.__name__, back_populates='authorized_users')

    @classmethod
    def create_membership(cls, university_dept, authorized_user, is_advisor, is_director):
        if not len(authorized_user.department_memberships):
            mapping = cls(is_advisor=is_advisor, is_director=is_director)
            mapping.authorized_user = authorized_user
            mapping.university_dept = university_dept
            authorized_user.department_memberships.append(mapping)
            university_dept.authorized_users.append(mapping)
            db.session.add(mapping)
        std_commit()


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


class NoteAttachment(db.Model):
    __tablename__ = 'note_attachments'

    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), primary_key=True)
    path_to_attachment = db.Column('path_to_attachment', db.String(255), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deleted_at = db.Column(db.DateTime)
    note = db.relationship('Note', back_populates='attachments')
