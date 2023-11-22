"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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


from functools import reduce
from itertools import groupby
from operator import itemgetter

from boac import db, std_commit
from boac.externals import data_loch
from boac.lib.berkeley import BERKELEY_DEPT_CODE_TO_PROGRAM_AFFILIATIONS
from boac.models.base import Base
from sqlalchemy.sql import text


class UniversityDept(Base):
    __tablename__ = 'university_depts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    dept_code = db.Column(db.String(80), nullable=False)
    dept_name = db.Column(db.String(255), nullable=False)
    authorized_users = db.relationship(
        'UniversityDeptMember',
        back_populates='university_dept',
    )

    __table_args__ = (db.UniqueConstraint('dept_code', 'dept_name', name='university_depts_code_unique_constraint'),)

    def __init__(self, dept_code, dept_name):
        self.dept_code = dept_code
        self.dept_name = dept_name

    @classmethod
    def find_by_dept_code(cls, dept_code):
        return cls.query.filter_by(dept_code=dept_code).first()

    @classmethod
    def get_all(cls, exclude_empty=False):
        if exclude_empty:
            results = db.session.execute(text('select distinct university_dept_id from university_dept_members'))
            dept_ids = [row['university_dept_id'] for row in results.mappings()]
            return cls.query.filter(cls.id.in_(dept_ids)).order_by(cls.dept_name).all()
        else:
            return cls.query.order_by(cls.dept_name).all()

    @classmethod
    def create(cls, dept_code, dept_name):
        dept = cls(dept_code=dept_code, dept_name=dept_name)
        db.session.add(dept)
        std_commit()
        return dept

    def delete_automated_members(self):
        sql = """
            DELETE FROM university_dept_members
                WHERE university_dept_id = :id
                AND automate_membership IS TRUE;
            UPDATE authorized_users SET deleted_at = now()
                WHERE is_admin IS FALSE
                AND deleted_at IS NULL
                AND id NOT IN (SELECT authorized_user_id FROM university_dept_members);"""
        db.session.execute(text(sql), {'id': self.id})
        std_commit()

    def memberships_from_loch(self):
        program_affiliations = BERKELEY_DEPT_CODE_TO_PROGRAM_AFFILIATIONS.get(self.dept_code)
        if not program_affiliations:
            return []
        advisors = data_loch.get_advisor_uids_for_affiliations(
            program_affiliations.get('program'),
            program_affiliations.get('affiliations'),
        )

        def _resolve(uid, rows):
            rows = list(rows)
            if len(rows) == 1:
                return rows[0]
            can_access_advising_data = reduce((lambda r, s: r['can_access_advising_data'] or s['can_access_advising_data']), rows)
            can_access_canvas_data = reduce((lambda r, s: r['can_access_canvas_data'] or s['can_access_canvas_data']), rows)
            degree_progress_permission = reduce((lambda r, s: r['degree_progress_permission'] or s['degree_progress_permission']), rows)
            return {
                'uid': uid,
                'can_access_advising_data': can_access_advising_data,
                'can_access_canvas_data': can_access_canvas_data,
                'degree_progress_permission': degree_progress_permission,
            }
        advisors.sort(key=itemgetter('uid'))
        return [_resolve(uid, rows) for (uid, rows) in groupby(advisors, itemgetter('uid'))]
