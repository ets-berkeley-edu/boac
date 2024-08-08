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


class Section(object):

    def __init__(self,
                 ccn,
                 code,
                 instruction_format,
                 is_primary,
                 meetings,
                 number,
                 term,
                 title,
                 enrollments=None):
        self.ccn = ccn
        self.code = code
        self.instruction_format = instruction_format
        self.is_primary = is_primary
        self.meetings = meetings
        self.number = number
        self.term = term
        self.title = title
        self.enrollments = enrollments or []


class SectionMeeting(object):

    def __init__(self,
                 days,
                 end_time,
                 instructors,
                 location,
                 mode,
                 start_time):
        self.days = days
        self.end_time = end_time
        self.instructors = instructors
        self.location = location
        self.mode = mode
        self.start_time = start_time


class SectionEnrollment(object):

    def __init__(self,
                 sid,
                 status,
                 uid):
        self.sid = sid
        self.status = status
        self.uid = uid
