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


import csv
import os
from scriptpath import scriptify


os.environ['FIXTURE_OUTPUT_PATH'] = os.path.expanduser('~/tmp/fixtures')


@scriptify.in_app
def main(app):
    from boac.externals import canvas
    request_ctx = app.test_request_context('/')
    request_ctx.push()

    failures = {
        'user_for_uid': [],
        'user_courses': [],
        'student_summaries': [],
    }

    with open(os.path.expanduser('~/tmp/fixtures/cohorts.csv')) as f:
        reader = csv.reader(f)
        headers = next(reader)
        uid_index = headers.index('member_uid')
        for row in reader:
            uid = row[uid_index]

            user_for_uid = canvas._get_user_for_uid(uid)
            if not user_for_uid:
                failures['user_for_uid'].append(uid)

            user_courses = canvas._get_all_user_courses(uid)
            if not user_courses:
                failures['user_courses'].append(uid)
                continue

            for course in user_courses:
                output_path = os.environ['FIXTURE_OUTPUT_PATH']
                course_id = course['id']
                if os.path.isfile(f'{output_path}/canvas_student_summaries_for_course_{course_id}.json'):
                    print(f'Fixture already present for course {course_id}, skipping')
                else:
                    student_summaries = canvas._get_student_summaries(course_id)
                    if not student_summaries:
                        failures['student_summaries'].append(course_id)

    print('Complete. Failures below:')
    print(failures)


main()
