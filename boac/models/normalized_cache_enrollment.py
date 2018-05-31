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
from boac.merged.sis_sections import get_sis_section
from boac.models.base import Base
from boac.models.student import Student


class NormalizedCacheEnrollment(Base):
    __tablename__ = 'normalized_cache_enrollments'

    term_id = db.Column(db.INTEGER, primary_key=True)
    section_id = db.Column(db.INTEGER, primary_key=True)
    sid = db.Column(db.String(80), db.ForeignKey('students.sid'), primary_key=True)

    def __repr__(self):
        return f'<NormalizedCacheEnrollment term_id={self.term_id}, section_id={self.section_id}, sid={self.sid}>'

    @classmethod
    def get_enrolled_sids(cls, term_id, section_id):
        sids = []
        for enrollment in cls.query.filter_by(term_id=term_id, section_id=section_id).all():
            sids.append(enrollment.sid)
        return sids

    @classmethod
    def update_enrollments(cls, term_id, sid, enrollments):
        term_id = int(term_id)
        # Previous enrollments might have been dropped
        cls.query.filter_by(term_id=term_id, sid=sid).delete()
        std_commit()
        # Add fresh enrollment data
        for enrollment in enrollments:
            normalized = cls(term_id=term_id, section_id=int(enrollment['sis_section_id']), sid=sid)
            db.session.add(normalized)
        std_commit()

    @classmethod
    def get_course_section(cls, term_id, section_id):
        course_section = get_sis_section(term_id, section_id)
        if course_section:
            sids = NormalizedCacheEnrollment.get_enrolled_sids(term_id=term_id, section_id=section_id)
            students = Student.find_students(sids)
            course_section['students'] = [student.to_expanded_api_json() for student in students]
        return course_section or None
