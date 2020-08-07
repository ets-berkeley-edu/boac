"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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


import re

from boac.externals import data_loch
from boac.models.json_cache import stow


@stow('sis_section_{sis_section_id}', for_term=True)
def get_sis_section(term_id, sis_section_id):
    """Provide detailed SIS Class Section data such as meeting schedules and instructors.

    This feed is not used in search, analytics, cohort views, or student views, and is not
    preloaded by cache refresh. Instead, it's lazy-loaded when an advisor first requests
    a class view.
    """
    from boac.lib.berkeley import term_name_for_sis_id

    rows = data_loch.get_sis_section(term_id, sis_section_id)
    if rows is None:
        return None
    if not rows:
        return False

    # If there are multiple rows, all values should be repeated except for meeting schedules and/or instructors.
    section = {
        'termId': term_id,
        'termName': term_name_for_sis_id(term_id),
        'sectionId': rows[0]['sis_section_id'],
        'displayName': rows[0]['sis_course_name'],
        'title': rows[0]['sis_course_title'],
        'instructionFormat': rows[0]['sis_instruction_format'],
        'sectionNum': rows[0]['sis_section_num'],
        'units': _maximum_units(rows[0]),
        'meetings': _get_meetings(rows),
    }
    return section


def _get_meetings(section_rows):
    meetings = {}
    for row in section_rows:
        times = None
        meeting_days = _days_in_friendly_format(row)
        if meeting_days:
            start_time = _format_time(row['meeting_start_time'])
            end_time = _format_time(row['meeting_end_time'])
            if start_time and end_time and (start_time != end_time):
                times = f'{start_time} - {end_time}'
        meeting = {
            'days': meeting_days,
            'instructionMode': row['sis_instruction_mode'],
            'location': row['meeting_location'],
            'time': times,
        }
        key = str(meeting)
        if meetings.get(key):
            meeting = meetings[key]
        else:
            meeting['instructors'] = []
            meetings[key] = meeting
        instructor_name = row['instructor_name']
        if instructor_name and instructor_name not in meeting['instructors']:
            meeting['instructors'].append(instructor_name)
    return list(meetings.values())


def _format_time(time):
    if not time:
        return None
    split = re.split(':', time)
    if len(split) >= 2 and split[0].isdigit():
        hour = int(split[0])
        suffix = 'am' if hour < 12 else 'pm'
        hour = hour if hour < 13 else hour - 12
        return f'{hour}:{split[1]} {suffix}'
    else:
        return None


def _days_in_friendly_format(section_row):
    meets_days = section_row.get('meeting_days')
    if not meets_days:
        return None
    days = re.findall('[A-Z][A-Z]', meets_days.upper())
    day_lookup = {
        'MO': 'Monday',
        'TU': 'Tuesday',
        'WE': 'Wednesday',
        'TH': 'Thursday',
        'FR': 'Friday',
        'SA': 'Saturday',
        'SU': 'Sunday',
    }
    if len(days) == 1:
        return day_lookup[days[0]]
    else:
        day_list = [day_lookup[d][0:3] for d in days]
        return ', '.join(day_list)


def _maximum_units(section_row):
    units = section_row['allowed_units']
    # Education Abroad Program needs to map one-off CS section IDs to externally administered
    # classes. As a placeholder which won't interfere with any real earned-credits awarded the student,
    # the "allowed units" for those sections are generally set to an unrealistically large number.
    if units and units > 20 and section_row['sis_course_name'].startswith('EAP'):
        units = None
    return units
