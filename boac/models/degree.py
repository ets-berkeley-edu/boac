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
from boac.models.base import Base


class Degree(Base):
    __tablename__ = 'degrees'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    created_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('authorized_users.id'), nullable=False)

    def __init__(self, created_by, name, updated_by):
        self.created_by = created_by
        self.name = name
        self.updated_by = updated_by

    def __repr__(self):
        return f"""<Degree id={self.id},
                    name={self.name},
                    deleted_at={self.deleted_at},
                    deleted_by={self.deleted_by},
                    created_at={self.created_at},
                    created_by={self.created_by},
                    updated_at={self.updated_at}
                    updated_by={self.updated_by}>"""

    @classmethod
    def create(cls, created_by, name):
        degree = cls(
            created_by=created_by,
            name=name,
            updated_by=created_by,
        )
        db.session.add(degree)
        std_commit()
        return degree
