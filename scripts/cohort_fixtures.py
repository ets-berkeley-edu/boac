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

            user_for_uid = canvas.get_user_for_uid(app.canvas_instance, uid)
            if not user_for_uid:
                failures['user_for_uid'].append(uid)

            user_courses = canvas.get_user_courses(app.canvas_instance, uid)
            if not user_courses:
                failures['user_courses'].append(uid)
                continue

            for course in user_courses:
                if os.path.isfile(f"{os.environ['FIXTURE_OUTPUT_PATH']}/canvas_student_summaries_for_course_{course['id']}.json"):
                    print(f"Fixture already present for course {course['id']}, skipping")
                else:
                    student_summaries = canvas.get_student_summaries(app.canvas_instance, course['id'])
                    if not student_summaries:
                        failures['student_summaries'].append(course['id'])

    print('Complete. Failures below:')
    print(failures)


main()
