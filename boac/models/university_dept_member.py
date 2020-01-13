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

from boac import db, std_commit
from boac.models.base import Base
from boac.models.university_dept import UniversityDept


class UniversityDeptMember(Base):
    __tablename__ = 'university_dept_members'

    university_dept_id = db.Column(db.Integer, db.ForeignKey('university_depts.id'), primary_key=True)
    authorized_user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True)
    is_advisor = db.Column(db.Boolean, nullable=False)
    is_director = db.Column(db.Boolean, nullable=False)
    is_scheduler = db.Column(db.Boolean, nullable=False)
    automate_membership = db.Column(db.Boolean, nullable=False)
    authorized_user = db.relationship('AuthorizedUser', back_populates='department_memberships')
    # Pre-load UniversityDept below to avoid 'failed to locate', as seen during routes.py init phase
    university_dept = db.relationship(UniversityDept.__name__, back_populates='authorized_users')

    def __init__(
            self,
            university_dept_id,
            authorized_user_id,
            is_advisor,
            is_director,
            is_scheduler,
            automate_membership=True,
    ):
        self.university_dept_id = university_dept_id
        self.authorized_user_id = authorized_user_id
        self.is_advisor = is_advisor
        self.is_director = is_director
        self.is_scheduler = is_scheduler
        self.automate_membership = automate_membership

    @classmethod
    def create_or_update_membership(
            cls,
            university_dept_id,
            authorized_user_id,
            is_advisor,
            is_director,
            is_scheduler,
            automate_membership=True,
    ):
        existing_membership = cls.query.filter_by(
            university_dept_id=university_dept_id,
            authorized_user_id=authorized_user_id,
        ).first()
        if existing_membership:
            membership = existing_membership
            membership.is_advisor = is_advisor
            membership.is_director = is_director
            membership.is_scheduler = is_scheduler
            membership.automate_membership = automate_membership
        else:
            membership = cls(
                university_dept_id=university_dept_id,
                authorized_user_id=authorized_user_id,
                is_advisor=is_advisor,
                is_director=is_director,
                is_scheduler=is_scheduler,
                automate_membership=automate_membership,
            )
        db.session.add(membership)
        std_commit()
        return membership

    @classmethod
    def get_existing_memberships(cls, authorized_user_id):
        return cls.query.filter_by(authorized_user_id=authorized_user_id).all()

    @classmethod
    def update_membership(
            cls,
            university_dept_id,
            authorized_user_id,
            is_advisor,
            is_director,
            is_scheduler,
            automate_membership,
    ):
        membership = cls.query.filter_by(university_dept_id=university_dept_id, authorized_user_id=authorized_user_id).first()
        if membership:
            membership.is_advisor = membership.is_advisor if is_advisor is None else is_advisor
            membership.is_director = membership.is_director if is_director is None else is_director
            membership.is_scheduler = membership.is_scheduler if is_scheduler is None else is_scheduler
            membership.automate_membership = membership.automate_membership if automate_membership is None else automate_membership
            std_commit()
            return membership
        return None

    @classmethod
    def get_distinct_departments(
            cls,
            authorized_user_id=None,
            is_advisor=None,
            is_director=None,
            is_scheduler=None,
    ):
        sql = """
            SELECT DISTINCT dept_code FROM university_depts d
            JOIN university_dept_members m ON m.university_dept_id = d.id
            WHERE TRUE
        """
        if authorized_user_id:
            sql += ' AND m.authorized_user_id = :authorized_user_id'
        else:
            sql += ' AND d.id IN (SELECT DISTINCT university_dept_id FROM university_depts)'
        if is_advisor is not None:
            sql += f" AND m.is_advisor IS {'TRUE' if is_advisor else 'FALSE'}"
        if is_director is not None:
            sql += f" AND m.is_director IS {'TRUE' if is_director else 'FALSE'}"
        if is_scheduler is not None:
            sql += f" AND m.is_scheduler IS {'TRUE' if is_scheduler else 'FALSE'}"
        return [row['dept_code'] for row in db.session.execute(sql, {'authorized_user_id': authorized_user_id})]

    @classmethod
    def delete_membership(cls, university_dept_id, authorized_user_id):
        membership = cls.query.filter_by(university_dept_id=university_dept_id, authorized_user_id=authorized_user_id).first()
        if not membership:
            return False
        db.session.delete(membership)
        std_commit()
        return True

    def to_api_json(self):
        return {
            'universityDeptId': self.university_dept_id,
            'authorizedUserId': self.authorized_user_id,
            'isAdvisor': self.is_advisor,
            'isDirector': self.is_director,
            'isScheduler': self.is_scheduler,
            'automateMembership': self.automate_membership,
        }
