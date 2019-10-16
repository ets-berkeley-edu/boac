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

from boac import db, std_commit
from boac.models.base import Base
from boac.models.university_dept import UniversityDept


class UniversityDeptMember(Base):
    __tablename__ = 'university_dept_members'

    university_dept_id = db.Column(db.Integer, db.ForeignKey('university_depts.id'), primary_key=True)
    authorized_user_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), primary_key=True)
    is_advisor = db.Column(db.Boolean, nullable=False)
    is_director = db.Column(db.Boolean, nullable=False)
    is_drop_in_advisor = db.Column(db.Boolean, nullable=False)
    is_scheduler = db.Column(db.Boolean, nullable=False)
    automate_membership = db.Column(db.Boolean, nullable=False)
    authorized_user = db.relationship('AuthorizedUser', back_populates='department_memberships')
    # Pre-load UniversityDept below to avoid 'failed to locate', as seen during routes.py init phase
    university_dept = db.relationship(UniversityDept.__name__, back_populates='authorized_users')

    def __init__(self, is_advisor, is_director, is_drop_in_advisor, is_scheduler, automate_membership=True):
        self.is_advisor = is_advisor
        self.is_director = is_director
        self.is_drop_in_advisor = is_drop_in_advisor
        self.is_scheduler = is_scheduler
        self.automate_membership = automate_membership

    @classmethod
    def create_or_update_membership(
            cls,
            university_dept,
            authorized_user,
            is_advisor,
            is_director,
            is_drop_in_advisor,
            is_scheduler,
            automate_membership=True,
    ):
        dept_id = university_dept.id
        user_id = authorized_user.id
        existing_membership = cls.query.filter_by(university_dept_id=dept_id, authorized_user_id=user_id).first()
        if existing_membership:
            membership = existing_membership
            membership.is_advisor = is_advisor
            membership.is_director = is_director
            membership.is_drop_in_advisor = is_drop_in_advisor
            membership.is_scheduler = is_scheduler
            membership.automate_membership = automate_membership
        else:
            membership = cls(
                is_advisor=is_advisor,
                is_director=is_director,
                is_drop_in_advisor=is_drop_in_advisor,
                is_scheduler=is_scheduler,
                automate_membership=automate_membership,
            )
            membership.authorized_user = authorized_user
            membership.university_dept = university_dept
            authorized_user.department_memberships.append(membership)
            university_dept.authorized_users.append(membership)
        db.session.add(membership)
        std_commit()
        return membership

    @classmethod
    def update_membership(
            cls,
            university_dept_id,
            authorized_user_id,
            is_advisor,
            is_director,
            is_drop_in_advisor,
            is_scheduler,
            automate_membership,
    ):
        membership = cls.query.filter_by(university_dept_id=university_dept_id, authorized_user_id=authorized_user_id).first()
        if membership:
            membership.is_advisor = membership.is_advisor if is_advisor is None else is_advisor
            membership.is_director = membership.is_director if is_director is None else is_director
            membership.is_drop_in_advisor = membership.is_drop_in_advisor if is_drop_in_advisor is None else is_drop_in_advisor
            membership.is_scheduler = membership.is_scheduler if is_scheduler is None else is_scheduler
            membership.automate_membership = membership.automate_membership if automate_membership is None else automate_membership
            std_commit()
            return membership
        return None

    @classmethod
    def delete_membership(cls, university_dept_id, authorized_user_id):
        membership = cls.query.filter_by(university_dept_id=university_dept_id, authorized_user_id=authorized_user_id).first()
        if not membership:
            return False
        db.session.delete(membership)
        std_commit()
        return True

    @classmethod
    def memberships_for_dept_code(cls, dept_code, **kwargs):
        return cls.query.filter_by(**kwargs).join(cls.university_dept, aliased=True).filter_by(dept_code=dept_code).all()

    def to_api_json(self):
        return {
            'universityDeptId': self.university_dept_id,
            'authorizedUserId': self.authorized_user_id,
            'isAdvisor': self.is_advisor,
            'isDirector': self.is_director,
            'isDropInAdvisor': self.is_drop_in_advisor,
            'isScheduler': self.is_scheduler,
            'automateMembership': self.automate_membership,
        }
