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


class DegreeProgressCategoryUnitRequirement(db.Model):
    __tablename__ = 'degree_progress_category_unit_requirements'

    category_id = db.Column(db.Integer, db.ForeignKey('degree_progress_categories.id'), primary_key=True)
    unit_requirement_id = db.Column(db.Integer, db.ForeignKey('degree_progress_unit_requirements.id'), primary_key=True)
    category = db.relationship('DegreeProgressCategory', back_populates='unit_requirements')
    unit_requirement = db.relationship('DegreeProgressUnitRequirement', back_populates='categories')

    def __init__(
            self,
            category_id,
            unit_requirement_id,
    ):
        self.category_id = category_id
        self.unit_requirement_id = unit_requirement_id

    @classmethod
    def create(cls, category_id, unit_requirement_id, db_session=None):
        session = db_session or db.session
        session.add(cls(category_id=category_id, unit_requirement_id=unit_requirement_id))
        std_commit(session=session)

    @classmethod
    def delete_mappings(cls, unit_requirement_id):
        for mapping in cls.query.filter_by(unit_requirement_id=unit_requirement_id).all():
            db.session.delete(mapping)
        std_commit()

    @classmethod
    def find_by_category_id(cls, category_id):
        return cls.query.filter_by(category_id=category_id).all()
