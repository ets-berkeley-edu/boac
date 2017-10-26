from scriptpath import scriptify

success_count = 0
failures = []


def load_canvas_externals(uid):
    from boac.externals import canvas

    global success_count, failures

    canvas_user_profile = canvas.get_user_for_uid(uid)
    if canvas_user_profile is None:
        failures.append('canvas.get_user_for_uid failed for UID {}'.format(
            uid,
        ))
    elif canvas_user_profile:
        success_count += 1
        sites = canvas.get_student_courses_in_term(uid)
        if sites:
            success_count += 1
            for site in sites:
                site_id = site['id']
                if not canvas.get_course_sections(site_id):
                    failures.append('canvas.get_course_sections failed for UID {}, site_id {}'.format(
                        uid,
                        site_id,
                    ))
                    continue
                success_count += 1
                if not canvas.get_student_summaries(site_id):
                    failures.append('canvas.get_student_summaries failed for site_id {}'.format(
                        site_id,
                    ))
                    continue
                success_count += 1


def load_sis_externals(sis_term_id, csid):
    from boac.externals import sis_enrollments_api, sis_student_api

    global success_count, failures

    if sis_student_api.get_student(csid):
        success_count += 1
    else:
        failures.append('SIS get_student failed for CSID {}'.format(
            csid,
        ))

    if sis_enrollments_api.get_enrollments(csid, sis_term_id):
        success_count += 1
    else:
        failures.append('SIS get_student failed for CSID {}, sis_term_id {}'.format(
            csid,
            sis_term_id,
        ))


@scriptify.in_session_request
def main(app):
    from boac import db
    from boac.lib import berkeley
    from boac.models.cohort import Cohort

    global success_count, failures

    term_name = app.config['CANVAS_CURRENT_ENROLLMENT_TERM']
    sis_term_id = berkeley.sis_term_id_for_name(term_name)

    # Currently, all external data is loaded starting from the individuals who belong
    # to one or more Cohorts.
    for csid, uid in db.session.query(Cohort.member_csid, Cohort.member_uid).distinct():
        load_canvas_externals(uid)
        load_sis_externals(sis_term_id, csid)

    print('Complete. Fetched {} external feeds.'.format(success_count))
    if len(failures):
        print('Failed to fetch {} feeds:'.format(len(failures)))
        print(failures)


main()
