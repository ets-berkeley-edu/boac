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
import boac.api.util as api_util
from boac.lib import util
from boac.models.base import Base


class NormalizedCacheCourseSection(Base):
    __tablename__ = 'normalized_cache_course_sections'
    __table_args__ = (
        db.PrimaryKeyConstraint('term_id', 'section_id'),
    )

    term_id = db.Column(db.INTEGER, nullable=False, index=True)
    section_id = db.Column(db.INTEGER, nullable=False, index=True)
    dept_name = db.Column(db.String(255), nullable=False)
    dept_code = db.Column(db.String(10), nullable=False)
    catalog_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    instruction_format = db.Column(db.String(10), nullable=True)
    section_num = db.Column(db.String(255), nullable=True)
    units = db.Column(db.INTEGER, nullable=True)
    meeting_days = db.Column(db.ARRAY(db.String(50)), nullable=True)
    meeting_times = db.Column(db.ARRAY(db.String(50)), nullable=True)
    locations = db.Column(db.ARRAY(db.String(255)), nullable=True)
    instructors = db.Column(db.ARRAY(db.String(255)), nullable=True)

    def __repr__(self):
        return f"""<NormalizedCacheCourseSection
            term_id={self.term_id},
            section_id={self.section_id},
            dept_name={self.dept_name},
            dept_code={self.dept_code},
            catalog_id={self.catalog_id},
            display_name={self.display_name},
            title={self.title},
            instruction_format={self.instruction_format},
            section_num={self.section_num},
            units={self.units},
            meeting_days={self.meeting_days},
            meeting_times={self.meeting_time},
            locations={self.location},
            instructors={self.instructors}>"""

    @classmethod
    def update_enrollment(cls, term_id, sid, section):
        course = util.get(section['class'], 'course')
        section_id = util.get(section, 'id')
        if course and section_id:
            dept_name = course['subjectArea']['description']
            dept_code = course['subjectArea']['code']
            catalog_id = course['catalogNumber']['formatted']
            instruction_format = section['component']['code'] if 'component' in section else None
            units = util.get(section['class']['allowedUnits'], 'forAcademicProgress')

            s = cls.query.filter_by(term_id=term_id, section_id=section_id).first()
            if s:
                s.term_id = term_id
                s.section_id = section_id
                s.dept_name = dept_name
                s.dept_code = dept_code
                s.catalog_id = catalog_id
                s.display_name = course['displayName']
                s.title = course['title']
                s.instruction_format = instruction_format
                s.section_num = section['number']
                s.units = units
                s.update_meetings(section)
            else:
                row = cls(
                    term_id=term_id,
                    section_id=section_id,
                    dept_name=dept_name,
                    dept_code=dept_code,
                    catalog_id=catalog_id,
                    display_name=course['displayName'],
                    title=course['title'],
                    instruction_format=instruction_format,
                    section_num=section['number'],
                    units=units,
                )
                row.update_meetings(section)
                db.session.add(row)
            std_commit()

    def to_api_json(self):
        return api_util.course_section_to_json(self)

    def update_meetings(self, section):
        self.meeting_days = []
        self.meeting_times = []
        self.instructors = []
        self.locations = []
        meetings = section['meetings'] if 'meetings' in section else []
        for meeting in meetings:
            self.meeting_days.append(meeting['meetsDays'])
            start_time = meeting['startTime']
            end_time = meeting['endTime']
            self.meeting_times.append(f'{start_time} - {end_time}')
            self.locations.append(meeting['location']['description'])
            meeting_instructors = []
            instructors = meeting['assignedInstructors'] if 'assignedInstructors' in meeting else []
            for entry in instructors:
                instructor = entry['instructor']
                for name in instructor['names']:
                    if name['type']['code'] == 'PRF':
                        meeting_instructors.append(name['formattedName'])
            self.instructors.append(', '.join(meeting_instructors))
