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
from boac.merged.student import query_students
from boac.models.base import Base
from sqlalchemy import text


class CuratedGroup(Base):
    __tablename__ = 'student_groups'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    owner_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

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
    def get_all_sids(cls, curated_group_id):
        return CuratedGroupStudent.get_sids(curated_group_id=curated_group_id)

    @classmethod
    def add_student(cls, curated_group_id, sid):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        if curated_group:
            CuratedGroupStudent.add_student(curated_group_id=curated_group_id, sid=sid)

    @classmethod
    def add_students(cls, curated_group_id, sids):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        if curated_group:
            CuratedGroupStudent.add_students(curated_group_id=curated_group_id, sids=sids)
            std_commit()

    @classmethod
    def remove_student(cls, curated_group_id, sid):
        if cls.find_by_id(curated_group_id):
            CuratedGroupStudent.remove_student(curated_group_id, sid)

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

    def to_api_json(self, order_by='last_name', offset=0, limit=50, include_students=True):
        feed = {
            'id': self.id,
            'ownerId': self.owner_id,
            'name': self.name,
        }
        if include_students:
            sids = CuratedGroupStudent.get_sids(curated_group_id=self.id)
            if sids:
                result = query_students(sids=sids, order_by=order_by, offset=offset, limit=limit, include_profiles=False)
                feed['students'] = result['students']
                feed['studentCount'] = result['totalStudentCount']
            else:
                feed['students'] = []
                feed['studentCount'] = 0
        return feed


class CuratedGroupStudent(db.Model):
    __tablename__ = 'student_group_members'

    curated_group_id = db.Column('student_group_id', db.Integer, db.ForeignKey('student_groups.id'), primary_key=True)
    sid = db.Column('sid', db.String(80), primary_key=True)

    def __init__(self, curated_group_id, sid):
        self.curated_group_id = curated_group_id
        self.sid = sid

    @classmethod
    def get_sids(cls, curated_group_id):
        return [row.sid for row in cls.query.filter_by(curated_group_id=curated_group_id).all()]

    @classmethod
    def add_student(cls, curated_group_id, sid):
        db.session.add(cls(curated_group_id, sid))
        std_commit()

    @classmethod
    def add_students(cls, curated_group_id, sids):
        existing_sids = [row.sid for row in cls.query.filter_by(curated_group_id=curated_group_id).all()]
        for sid in set(sids).difference(existing_sids):
            db.session.add(cls(curated_group_id, sid))
        std_commit()

    @classmethod
    def remove_student(cls, curated_group_id, sid):
        row = cls.query.filter_by(sid=sid, curated_group_id=curated_group_id).first()
        if row:
            db.session.delete(row)
            std_commit()
