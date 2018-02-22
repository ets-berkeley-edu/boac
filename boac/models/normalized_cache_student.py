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


class NormalizedCacheStudent(Base):
    __tablename__ = 'normalized_cache_students'

    sid = db.Column(db.String(80), nullable=False, primary_key=True)
    gpa = db.Column(db.Numeric, nullable=True, index=True)
    level = db.Column(db.String(9), nullable=True, index=True)
    units = db.Column(db.Numeric, nullable=True, index=True)

    def __repr__(self):
        return '<NormalizedCacheStudent sid={}, gpa={}, level={}, units={}, created={}>'.format(
            self.sid,
            self.gpa,
            self.level,
            self.updated_at,
            self.created_at,
        )

    @classmethod
    def update_profile(cls, sid, gpa=None, level=None, units=None):
        row = cls.query.filter_by(sid=sid).first()
        if row:
            row.gpa = gpa
            row.level = level
            row.units = units
        else:
            row = cls(sid=sid, gpa=gpa, level=level, units=units)
            db.session.add(row)
        std_commit()
