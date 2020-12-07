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

from datetime import timedelta
from itertools import islice

from boac import db
from boac.api.errors import BadRequestError, ForbiddenRequestError
from boac.api.util import add_alert_counts, advising_data_access_required, advisor_required, ce3_required, is_unauthorized_search
from boac.externals.data_loch import get_enrolled_primary_sections, get_enrolled_primary_sections_for_parsed_code, match_advising_note_authors_by_name
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged.admitted_student import search_for_admitted_students
from boac.merged.advising_appointment import search_advising_appointments
from boac.merged.advising_note import search_advising_notes
from boac.merged.calnet import get_uid_for_csid
from boac.merged.sis_terms import current_term_id
from boac.merged.student import search_for_students
from boac.models.alert import Alert
from boac.models.authorized_user import AuthorizedUser
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/search', methods=['POST'])
@advisor_required
def search():
    params = util.remove_none_values(request.get_json())
    order_by = util.get(params, 'orderBy', None)
    if is_unauthorized_search(list(params.keys()), order_by):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    domain = {
        'appointments': util.get(params, 'appointments'),
        'students': util.get(params, 'students'),
        'courses': util.get(params, 'courses'),
        'notes': util.get(params, 'notes'),
    }
    if not domain['students'] and not domain['courses'] and not domain['notes'] and not domain['appointments']:
        raise BadRequestError('No search domain specified')
    if not len(search_phrase) and not (domain['notes'] or domain['appointments']):
        raise BadRequestError('Invalid or empty search input')
    if domain['courses'] and not current_user.can_access_canvas_data:
        raise ForbiddenRequestError('Unauthorized to search courses')
    if (domain['notes'] or domain['appointments']) and not current_user.can_access_advising_data:
        raise ForbiddenRequestError('Unauthorized to search notes and appointments')

    feed = {}

    if domain['appointments']:
        feed.update(_appointments_search(search_phrase, params))

    if len(search_phrase) and domain['students']:
        feed.update(_student_search(search_phrase, params, order_by))

    if len(search_phrase) and domain['courses']:
        feed.update(_course_search(search_phrase))

    if domain['notes']:
        feed.update(_notes_search(search_phrase, params))

    return tolerant_jsonify(feed)


@app.route('/api/search/admits', methods=['POST'])
@ce3_required
def search_admits():
    params = request.get_json()
    search_phrase = util.get(params, 'searchPhrase', '').strip()
    if not len(search_phrase):
        raise BadRequestError('Invalid or empty search input')
    order_by = util.get(params, 'orderBy', None)
    admit_results = search_for_admitted_students(
        search_phrase=search_phrase.replace(',', ' '),
        order_by=order_by,
    )
    return tolerant_jsonify(admit_results)


@app.route('/api/search/add_to_search_history', methods=['POST'])
@login_required
def add_to_search_history():
    search_phrase = request.get_json().get('phrase')
    search_phrase = search_phrase and search_phrase.strip()
    if search_phrase:
        search_history = AuthorizedUser.add_to_search_history(current_user.get_id(), search_phrase)
        return tolerant_jsonify(search_history)
    else:
        raise BadRequestError('Search phrase not found in request')


@app.route('/api/search/my_search_history')
@login_required
def my_search_history():
    search_history = AuthorizedUser.get_search_history(current_user.get_id()) or []
    return tolerant_jsonify(search_history)


@app.route('/api/search/advisors/find_by_name', methods=['GET'])
@advising_data_access_required
def find_advisors_by_name():
    query = request.args.get('q')
    if not query:
        raise BadRequestError('Search query must be supplied')
    limit = request.args.get('limit')
    query_fragments = list(filter(None, set(query.upper().split(' '))))
    advisors = _advisors_by_name(query_fragments, limit=limit)
    legacy_note_authors = match_advising_note_authors_by_name(query_fragments, limit=limit)
    advisors_feed = _local_advisors_feed(advisors) + _loch_authors_feed(legacy_note_authors)
    advisors_by_uid = {a.get('uid'): a for a in advisors_feed}
    return tolerant_jsonify(list(advisors_by_uid.values()))


def _advisors_by_name(tokens, limit=None):
    benchmark = util.get_benchmarker('search find_advisors_by_name')
    benchmark('begin')
    token_conditions = []
    params = {}
    for token in tokens:
        idx = tokens.index(token)
        token_conditions.append(
            f"""JOIN advisor_author_index a{idx}
            ON UPPER(a{idx}.advisor_name) LIKE :token_{idx}
            AND a{idx}.advisor_uid = a.advisor_uid
            AND a{idx}.advisor_name = a.advisor_name""",
        )
        params[f'token_{idx}'] = f'%{token}%'
    sql = f"""SELECT DISTINCT a.advisor_name, a.advisor_uid
        FROM advisor_author_index a
        {' '.join(token_conditions)}
        ORDER BY a.advisor_name"""
    if limit:
        sql += f' LIMIT {limit}'
    benchmark('execute query')
    results = db.session.execute(sql, params)
    benchmark('end')
    keys = results.keys()
    return [dict(zip(keys, row)) for row in results.fetchall()]


def _local_advisors_feed(local_results):
    return [
        {
            'label': a.get('advisor_name'),
            'uid': a.get('advisor_uid'),
        } for a in local_results
    ]


def _loch_authors_feed(loch_results):
    return [
        {
            'label': f"{a.get('first_name')} {a.get('last_name')}",
            'sid': a.get('sid'),
            'uid': a.get('uid'),
        } for a in loch_results
    ]


def _appointments_search(search_phrase, params):
    appointment_options = util.get(params, 'appointmentOptions', {})
    advisor_uid = appointment_options.get('advisorUid')
    advisor_csid = appointment_options.get('advisorCsid')
    student_csid = appointment_options.get('studentCsid')
    topic = appointment_options.get('topic')
    limit = int(util.get(appointment_options, 'limit', 20))
    offset = int(util.get(appointment_options, 'offset', 0))

    date_from = appointment_options.get('dateFrom')
    date_to = appointment_options.get('dateTo')

    if not len(search_phrase) and not (advisor_uid or advisor_csid or student_csid or topic or date_from or date_to):
        raise BadRequestError('Invalid or empty search input')

    if advisor_csid and not advisor_uid:
        advisor_uid = get_uid_for_csid(app, advisor_csid)

    if date_from:
        try:
            datetime_from = util.localized_timestamp_to_utc(f'{date_from}T00:00:00')
        except ValueError:
            raise BadRequestError('Invalid dateFrom value')
    else:
        datetime_from = None

    if date_to:
        try:
            datetime_to = util.localized_timestamp_to_utc(f'{date_to}T00:00:00') + timedelta(days=1)
        except ValueError:
            raise BadRequestError('Invalid dateTo value')
    else:
        datetime_to = None

    if datetime_from and datetime_to and datetime_to <= datetime_from:
        raise BadRequestError('dateFrom must be less than dateTo')

    appointment_results = search_advising_appointments(
        search_phrase=search_phrase,
        advisor_uid=advisor_uid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=offset,
        limit=limit,
    )
    return {
        'appointments': appointment_results,
    }


def _student_search(search_phrase, params, order_by):
    student_results = search_for_students(
        search_phrase=search_phrase.replace(',', ' '),
        order_by=order_by,
        offset=util.get(params, 'offset', 0),
        limit=util.get(params, 'limit', 50),
    )
    students = student_results['students']
    sids = [s['sid'] for s in students]
    alert_counts = Alert.current_alert_counts_for_sids(current_user.get_id(), sids)
    add_alert_counts(alert_counts, students)
    return {
        'students': students,
        'totalStudentCount': student_results['totalStudentCount'],
    }


def _course_search(search_phrase):
    term_id = current_term_id()
    course_rows = []

    def _compress_to_alphanumeric(s):
        return ''.join(e for e in s if e.isalnum())

    words = search_phrase.rsplit(' ', 1)
    if len(words) == 1:
        candidate_subject_area = None
        candidate_catalog_id = words[0]
    else:
        candidate_subject_area = words[0]
        candidate_catalog_id = words[1]

    # If the search phrase appears to contain a catalog id, set up the course search that way.
    if any(c.isdigit() for c in candidate_catalog_id):
        subject_area = candidate_subject_area and _compress_to_alphanumeric(candidate_subject_area).upper()
        catalog_id = candidate_catalog_id.upper()
        course_rows = get_enrolled_primary_sections_for_parsed_code(term_id, subject_area, catalog_id)
    # Otherwise just compress the search phrase to alphanumeric characters and look for a simple match.
    else:
        compressed_search_phrase = _compress_to_alphanumeric(search_phrase)
        if compressed_search_phrase:
            course_rows = get_enrolled_primary_sections(term_id, compressed_search_phrase.upper())

    courses = []
    if course_rows:
        for row in islice(course_rows, 50):
            courses.append({
                'termId': row['term_id'],
                'sectionId': row['sis_section_id'],
                'courseName': row['sis_course_name'],
                'courseTitle': row['sis_course_title'],
                'instructionFormat': row['sis_instruction_format'],
                'sectionNum': row['sis_section_num'],
                'instructors': row['instructors'],
            })
    return {
        'courses': courses,
        'totalCourseCount': len(course_rows),
    }


def _notes_search(search_phrase, params):
    note_options = util.get(params, 'noteOptions', {})
    author_csid = note_options.get('advisorCsid')
    author_uid = note_options.get('advisorUid')
    student_csid = note_options.get('studentCsid')
    topic = note_options.get('topic')
    limit = int(util.get(note_options, 'limit', 20))
    offset = int(util.get(note_options, 'offset', 0))

    date_from = note_options.get('dateFrom')
    date_to = note_options.get('dateTo')

    if not len(search_phrase) and not (author_uid or author_csid or student_csid or topic or date_from or date_to):
        raise BadRequestError('Invalid or empty search input')

    if date_from:
        try:
            datetime_from = util.localized_timestamp_to_utc(f'{date_from}T00:00:00')
        except ValueError:
            raise BadRequestError('Invalid dateFrom value')
    else:
        datetime_from = None

    if date_to:
        try:
            datetime_to = util.localized_timestamp_to_utc(f'{date_to}T00:00:00') + timedelta(days=1)
        except ValueError:
            raise BadRequestError('Invalid dateTo value')
    else:
        datetime_to = None

    if datetime_from and datetime_to and datetime_to <= datetime_from:
        raise BadRequestError('dateFrom must be less than dateTo')

    notes_results = search_advising_notes(
        search_phrase=search_phrase,
        author_csid=author_csid,
        author_uid=author_uid,
        student_csid=student_csid,
        topic=topic,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        offset=offset,
        limit=limit,
    )
    return {
        'notes': notes_results,
    }
