import csv
import os
from scriptpath import scriptify


os.environ['FIXTURE_OUTPUT_PATH'] = os.path.expanduser('~/tmp/fixtures')


@scriptify.in_app
def main(app):
    from boac.externals import sis_student_api
    request_ctx = app.test_request_context('/')
    request_ctx.push()

    success_count = 0
    failures = []

    with open(os.path.expanduser('~/tmp/fixtures/cohorts.csv')) as f:
        reader = csv.reader(f)
        headers = next(reader)
        csid_index = headers.index('member_csid')
        for row in reader:
            csid = row[csid_index]
            response = sis_student_api.get_student(csid)
            if response:
                success_count += 1
            else:
                failures.append(csid)

    print(f'Complete. Generated fixtures for {success_count} CSIDs.')
    if len(failures):
        print(f'Failed to generate fixtures for {len(failures)} CSIDs:')
        print(failures)


main()
