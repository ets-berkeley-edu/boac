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

from boac import db, std_commit
from boac.lib.util import get_benchmarker
from boac.merged.admitted_student import get_admitted_students_by_sids
from boac.merged.student import query_students
from boac.models.base import Base
from boac.models.cohort_filter import CohortFilter
from boac.models.db_relationships import cohort_domain_type
from flask import current_app as app
from sqlalchemy import text


class CuratedGroup(Base):
    __tablename__ = 'student_groups'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    domain = db.Column(cohort_domain_type, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint(
        'owner_id',
        'name',
        name='student_groups_owner_id_name_unique_constraint',
    ),)

    def __init__(self, domain, name, owner_id):
        self.domain = domain
        self.name = name
        self.owner_id = owner_id

    def __repr__(self):
        return f"""<CohortFilter {self.id},
            domain={self.domain},
            name={self.name},
            owner_id={self.owner_id},
            updated_at={self.updated_at},
            created_at={self.created_at}>"""

    @classmethod
    def find_by_id(cls, curated_group_id):
        return cls.query.filter_by(id=curated_group_id).first()

    @classmethod
    def get_curated_groups(cls, owner_id):
        if app.config['FEATURE_FLAG_ADMITTED_STUDENTS']:
            filter_by = cls.query.filter_by(owner_id=owner_id)
        else:
            filter_by = cls.query.filter_by(domain='default', owner_id=owner_id)
        return filter_by.order_by(cls.name).all()

    @classmethod
    def get_groups_owned_by_uids(cls, uids):
        domain_clause = 'true' if app.config['FEATURE_FLAG_ADMITTED_STUDENTS'] else "sg.domain = 'default'"
        query = text(f"""
            SELECT sg.id, sg.domain, sg.name, count(sgm.sid) AS student_count, au.uid AS owner_uid
            FROM student_groups sg
            LEFT JOIN student_group_members sgm ON sg.id = sgm.student_group_id
            JOIN authorized_users au ON sg.owner_id = au.id
            WHERE au.uid = ANY(:uids) AND {domain_clause}
            GROUP BY sg.id, sg.name, au.id, au.uid
        """)
        results = db.session.execute(query, {'uids': uids})

        def transform(row):
            return {
                'id': row['id'],
                'domain': row['domain'],
                'name': row['name'],
                'totalStudentCount': row['student_count'],
                'ownerUid': row['owner_uid'],
            }
        return [transform(row) for row in results]

    @classmethod
    def curated_group_ids_per_sid(cls, domain, sid, user_id):
        query = text("""SELECT
            student_group_id as id
            FROM student_group_members m
            JOIN student_groups g ON g.id = m.student_group_id
            WHERE g.domain = :domain AND g.owner_id = :user_id AND m.sid = :sid""")
        results = db.session.execute(query, {
            'domain': domain,
            'sid': sid,
            'user_id': user_id,
        })
        return [row['id'] for row in results]

    @classmethod
    def create(cls, owner_id, name, domain='default'):
        curated_group = cls(domain=domain, name=name, owner_id=owner_id)
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
            _refresh_related_cohorts(curated_group)

    @classmethod
    def add_students(cls, curated_group_id, sids):
        curated_group = cls.query.filter_by(id=curated_group_id).first()
        if curated_group:
            CuratedGroupStudent.add_students(curated_group_id=curated_group_id, sids=sids)
            std_commit()
            _refresh_related_cohorts(curated_group)

    @classmethod
    def remove_student(cls, curated_group_id, sid):
        curated_group = cls.find_by_id(curated_group_id)
        if curated_group:
            CuratedGroupStudent.remove_student(curated_group_id, sid)
            _refresh_related_cohorts(curated_group)

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
            # Delete all cohorts that reference the deleted group
            for cohort_filter_id in curated_group.get_referencing_cohort_ids():
                CohortFilter.delete(cohort_filter_id)
                std_commit()

    def get_referencing_cohort_ids(self):
        query = text("""SELECT
            c.id, c.filter_criteria
            FROM cohort_filters c
            WHERE filter_criteria->>'curatedGroupIds' IS NOT NULL AND owner_id = :user_id""")
        results = db.session.execute(query, {'user_id': self.owner_id})
        cohort_filter_ids = []
        for row in results:
            if self.id in row['filter_criteria'].get('curatedGroupIds', []):
                cohort_filter_ids.append(row['id'])
        return cohort_filter_ids

    def to_api_json(self, include_students, order_by='last_name', offset=0, limit=50):
        benchmark = get_benchmarker(f'CuratedGroup {self.id} to_api_json')
        benchmark('begin')
        sids = CuratedGroupStudent.get_sids(curated_group_id=self.id)
        feed = {
            'domain': self.domain,
            'id': self.id,
            'name': self.name,
            'ownerId': self.owner_id,
            'sids': sids,
            'totalStudentCount': len(sids),
        }
        if include_students:
            if sids:
                if self.domain == 'admitted_students':
                    feed['students'] = get_admitted_students_by_sids(
                        limit=limit,
                        offset=offset,
                        order_by=order_by,
                        sids=sids,
                    )
                else:
                    result = query_students(
                        sids=sids,
                        academic_career_status=('active', 'inactive'),
                        include_profiles=False,
                        order_by=order_by,
                        offset=offset,
                        limit=limit,
                    )
                    feed['students'] = result['students']
            else:
                feed['students'] = []
        benchmark('end')
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


def _refresh_related_cohorts(curated_group):
    for cohort_id in curated_group.get_referencing_cohort_ids():
        cohort = CohortFilter.query.filter_by(id=cohort_id).first()
        cohort.clear_sids_and_student_count()
        cohort.update_alert_count(None)
        cohort.to_api_json(include_alerts_for_user_id=cohort.owner_id, include_students=False)
