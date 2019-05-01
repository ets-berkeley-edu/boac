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
from boac.merged.student import get_api_json, query_students
from boac.models.base import Base
from boac.models.db_relationships import CuratedGroupStudent
from sqlalchemy import text


class CuratedGroup(Base):
    __tablename__ = 'student_groups'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    owner_id = db.Column(db.String(80), db.ForeignKey('authorized_users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    students = db.relationship('CuratedGroupStudent', back_populates='curated_group', cascade='all')

    __table_args__ = (db.UniqueConstraint(
        'owner_id',
        'name',
        name='student_groups_owner_id_name_unique_constraint',
    ),)

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    @classmethod
    def find_by_id(cls, curated_group_id):
        return cls.query.filter_by(id=curated_group_id).first()

    @classmethod
    def get_curated_groups_by_owner_id(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).order_by(cls.name).all()

    @classmethod
    def curated_group_ids_per_sid(cls, user_id, sid):
        query = text(f"""SELECT
            student_group_id as id
            FROM student_group_members m
            JOIN student_groups g ON g.id = m.student_group_id
            WHERE g.owner_id = :user_id AND m.sid = :sid""")
        results = db.session.execute(query, {'user_id': user_id, 'sid': sid})
        return [row['id'] for row in results]

    @classmethod
    def create(cls, owner_id, name):
        curated_group = cls(name, owner_id)
        db.session.add(curated_group)
        std_commit()
        return curated_group

    @classmethod
    def add_student(cls, curated_group_id, sid):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        if curated_group:
            curated_group.students.append(CuratedGroupStudent(sid=sid, curated_group_id=curated_group_id))
            std_commit()

    @classmethod
    def add_students(cls, curated_group_id, sids):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        if curated_group:
            sids = set(sids).difference([s.sid for s in curated_group.students])
            for sid in sids:
                curated_group.students.append(CuratedGroupStudent(sid=sid, curated_group_id=curated_group_id))
            std_commit()

    @classmethod
    def remove_student(cls, curated_group_id, sid):
        curated_group = cls.find_by_id(curated_group_id)
        membership = CuratedGroupStudent.query.filter_by(sid=sid, curated_group_id=curated_group_id).first()
        if curated_group and membership:
            db.session.delete(membership)
            std_commit()

    @classmethod
    def rename(cls, curated_group_id, name):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        curated_group.name = name
        std_commit()

    @classmethod
    def delete(cls, curated_group_id):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        if curated_group:
            db.session.delete(curated_group)
            std_commit()

    def to_api_json(self, sids_only=False, include_students=True):
        api_json = {
            'id': self.id,
            'ownerId': self.owner_id,
            'name': self.name,
            'studentCount': len(self.students),
        }
        sids = [s.sid for s in self.students]
        # TODO: When the BOA business rules change and all advisors have access to all students
        #  then remove this filtering of SIDs based on current user dept_code. See BOAC-2130
        sids_available_per_user_role = query_students(sids=sids, sids_only=True)['sids']
        if sids_only:
            api_json['students'] = [{'sid': sid} for sid in sids_available_per_user_role]
        elif include_students:
            api_json['students'] = get_api_json(sids_available_per_user_role)
        return api_json
