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


class NormalizedCacheStudentMajor(Base):
    __tablename__ = 'normalized_cache_student_majors'
    __table_args__ = (
        db.PrimaryKeyConstraint('sid', 'major'),
    )

    sid = db.Column(db.String(80), nullable=False, index=True)
    major = db.Column(db.String(255), nullable=False, index=True)

    def __repr__(self):
        return '<NormalizedCacheStudentMajor sid={}, major={}, updated={}, created={}>'.format(
            self.sid,
            self.major,
            self.updated_at,
            self.created_at,
        )

    @classmethod
    def distinct_majors(cls):
        return [row[0] for row in db.session.query(cls.major).distinct(cls.major).all()]

    @classmethod
    def update_majors(cls, sid, new_majors):
        existing_rows = cls.query.filter_by(sid=sid).all()
        existing_majors = []
        for row in existing_rows:
            existing_majors.append(row.major)
            if row.major not in new_majors:
                db.session.delete(row)
        for new_major in new_majors:
            if new_major not in existing_majors:
                row = cls(sid=sid, major=new_major)
                db.session.add(row)
        std_commit()
