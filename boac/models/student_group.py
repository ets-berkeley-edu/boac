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


from boac import db, std_commit
from boac.models.base import Base
from boac.models.db_relationships import student_group_members
from boac.models.student import Student


class StudentGroup(Base):
    __tablename__ = 'student_groups'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    owner_id = db.Column(db.String(80), db.ForeignKey('authorized_users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    students = db.relationship(
        'Student',
        secondary=student_group_members,
        back_populates='group_memberships',
    )

    __table_args__ = (db.UniqueConstraint(
        'owner_id',
        'name',
        name='student_groups_owner_id_name_unique_constraint',
    ),)

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    @classmethod
    def get_or_create_my_primary(cls, owner_id):
        name = 'My Students'
        group = cls.query.filter_by(owner_id=owner_id, name=name).first()
        if not group:
            group = cls.create(owner_id, name)
            std_commit()
        return group

    @classmethod
    def find_by_id(cls, group_id):
        return cls.query.filter_by(id=group_id).first()

    @classmethod
    def get_groups_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).order_by(cls.name).all()

    @classmethod
    def create(cls, owner_id, name):
        group = cls(name, owner_id)
        db.session.add(group)
        std_commit()
        return group

    @classmethod
    def add_student(cls, group_id, sid):
        group = cls.query.filter_by(id=group_id).first()
        student = Student.find_by_sid(sid)
        group.students.append(student)
        std_commit()

    @classmethod
    def remove_student(cls, group_id, sid):
        student = Student.find_by_sid(sid)
        if student:
            group = cls.find_by_id(group_id)
            group.students.remove(student)
            std_commit()

    @classmethod
    def delete(cls, group_id):
        group = cls.query.filter_by(id=group_id).first()
        if group:
            db.session.delete(group)
            std_commit()

    def to_api_json(self):
        return {
            'id': self.id,
            'ownerId': self.owner_id,
            'name': self.name,
            'students': [student.to_api_json() for student in self.students],
            'studentCount': len(self.students),
        }
