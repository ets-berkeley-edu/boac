"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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


class PeerAdvisingDepartment(Base):
    __tablename__ = 'peer_advising_departments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    name = db.Column(db.String(255), nullable=False)
    university_dept_id = db.Column(db.Integer, db.ForeignKey('university_depts.id'), nullable=False)

    def __init__(self, name, university_dept_id):
        self.name = name
        self.university_dept_id = university_dept_id

    @classmethod
    def create(cls, name, university_dept_id):
        peer_advising_department = cls(name, university_dept_id)
        db.session.add(peer_advising_department)
        std_commit()
        return peer_advising_department

    @classmethod
    def find_by_university_dept_id(cls, university_dept_id):
        return cls.query.filter_by(university_dept_id=university_dept_id).all()
