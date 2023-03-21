"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

import json

from boac import db
from boac.externals import data_loch
from boac.externals.data_loch import get_student_degrees_report
from boac.merged.sis_terms import current_term_id
from boac.models.note import Note
from flask import current_app as app


def low_assignment_scores(term_id=None):
    if not term_id:
        term_id = current_term_id()
    examined_sids = set()
    low_sids = set()
    multiple_low_sids = set()
    # Many students in a low percentile may have received a reasonably high score.
    # Since instructors rarely grade on a curve, it may be fine to receive a score of 85
    # even if all other students received 90 or above.
    sids_with_low_raw_scores = set()
    primary_sections = set()
    primary_sections_with_scored_assignments = set()
    primary_sections_with_plottable_assignments = set()

    enrollments_for_term = data_loch.get_enrollments_for_term(term_id)
    enrollments_by_sid = {row['sid']: json.loads(row['enrollment_term']) for row in enrollments_for_term}
    itr = iter(enrollments_by_sid.items())
    for (sid, term) in itr:
        examined_sids.add(sid)
        for enr in term['enrollments']:
            first_section = enr['sections'][0]
            if not first_section.get('primary'):
                continue
            ccn = first_section['ccn']
            primary_sections.add(ccn)
            for site in enr['canvasSites']:
                score_info = site['analytics']['currentScore']
                if score_info['courseDeciles']:
                    primary_sections_with_scored_assignments.add(ccn)
                    if score_info['boxPlottable']:
                        primary_sections_with_plottable_assignments.add(ccn)
                    pct = score_info['student']['roundedUpPercentile']
                    if pct is not None:
                        if pct <= 25:
                            if sid in low_sids:
                                multiple_low_sids.add(sid)
                            low_sids.add(sid)
                            max_score = score_info['courseDeciles'][9]
                            if score_info['student']['raw'] < (max_score * 0.7):
                                sids_with_low_raw_scores.add(sid)
    app.logger.warn(f'Total of {len(examined_sids)} students in classes. {len(low_sids)} with low scores in a class.')
    app.logger.warn(f'Low scorers: {sorted(low_sids)}')
    app.logger.warn(f'  {len(multiple_low_sids)} Low scorers in multiple sites: {sorted(multiple_low_sids)}')
    app.logger.warn(f'  {len(sids_with_low_raw_scores)} Low scorers with raw score < 70% of max: {sorted(sids_with_low_raw_scores)}')
    app.logger.warn(f'Total of {len(primary_sections)} primary sections. '
                    f'{len(primary_sections_with_scored_assignments)} have scores. '
                    f'{len(primary_sections_with_plottable_assignments)} have a reasonable range of scores.')
    return {
        'sids': sorted(examined_sids),
        'low_sids': sorted(low_sids),
        'multiple_low_sids': sorted(multiple_low_sids),
        'sids_with_low_raw_scores': sorted(sids_with_low_raw_scores),
        'primary_sections_count': len(primary_sections),
        'sections_scored_count': len(primary_sections_with_scored_assignments),
        'sections_with_range_of_scores_count': len(primary_sections_with_plottable_assignments),
    }


def get_note_author_count(dept_code=None):
    query = 'SELECT COUNT(DISTINCT author_uid) FROM notes WHERE deleted_at IS NULL'
    if dept_code:
        query += f" AND '{dept_code}' = ANY(author_dept_codes)"
    results = db.session.execute(query)
    return [row['count'] for row in results][0]


def get_note_count(dept_code=None):
    query = 'SELECT COUNT(id) FROM notes WHERE deleted_at IS NULL'
    if dept_code:
        query += f" AND '{dept_code}' = ANY(author_dept_codes)"
    results = db.session.execute(query)
    return [row['count'] for row in results][0]


def get_note_count_per_batch(dept_code=None):
    query = """
        SELECT COUNT(*) AS count
        FROM notes
        WHERE deleted_at IS NULL
    """
    if dept_code:
        query += f" AND '{dept_code}' = ANY(author_dept_codes)"
    query += ' GROUP BY created_at HAVING COUNT(*) > 1'
    results = db.session.execute(query)
    return [row['count'] for row in results]


def get_private_note_count():
    results = db.session.execute('SELECT COUNT(*) FROM notes WHERE deleted_at IS NULL AND is_private IS TRUE')
    return [row['count'] for row in results][0]


def get_note_count_per_user(dept_code):
    query = f"""
        SELECT n.author_uid AS uid, COUNT(n.id) AS count
        FROM notes n
        JOIN authorized_users a ON a.uid = n.author_uid
        JOIN university_dept_members m ON m.authorized_user_id = a.id
        JOIN university_depts d ON d.id = m.university_dept_id AND d.dept_code = '{dept_code}'
        WHERE n.deleted_at IS NULL
        GROUP BY author_uid
    """
    results = {}
    for row in db.session.execute(query):
        results[row['uid']] = row['count']
    return results


def get_note_with_attachments_count(dept_code=None):
    query = """
        SELECT COUNT(DISTINCT a.note_id)
        FROM note_attachments a
        JOIN notes n ON n.id = a.note_id
        WHERE a.deleted_at IS NULL AND n.deleted_at IS NULL
    """
    if dept_code:
        query += f" AND '{dept_code}' = ANY(n.author_dept_codes)"
    results = db.session.execute(query)
    return [row['count'] for row in results][0]


def get_note_with_topics_count(dept_code=None):
    query = """
        SELECT COUNT(DISTINCT t.note_id)
        FROM note_topics t
        JOIN notes n ON n.id = t.note_id
        WHERE t.deleted_at IS NULL AND n.deleted_at IS NULL
    """
    if dept_code:
        query += f" AND '{dept_code}' = ANY(n.author_dept_codes)"
    results = db.session.execute(query)
    return [row['count'] for row in results][0]


def get_summary_of_boa_notes():
    api_json = Note.get_notes_report()
    distinct_sids = list(set([row['sid'] for row in api_json]))
    students_by_sid = _get_students_report(sids=distinct_sids)
    cohorts_by_sid = _get_cohorts_by_sid()
    curated_groups_by_sid = _get_curated_groups_by_sid()

    for entry in api_json:
        def _names_csv(groups_by_sid):
            groups = groups_by_sid.get(sid, [])
            return ','.join([str(g['name']) for g in groups])
        sid = entry['sid']
        student = students_by_sid.get(sid)
        if student:
            entry['cohort_names'] = _names_csv(cohorts_by_sid)
            entry['curated_group_names'] = _names_csv(curated_groups_by_sid)
            for key in ('degree_awarded_dates', 'degree_awarded_names', 'student_first_name', 'student_last_name'):
                entry[key] = student[key]
    return api_json


def get_boa_note_count_by_month():
    query = """
        SELECT
          DATE_TRUNC('month', created_at) AS created_at_month,
          COUNT(id) AS count
        FROM notes
        GROUP BY DATE_TRUNC('month', created_at)
    """
    report = []
    for row in db.session.execute(query):
        month_date = row['created_at_month']
        year = next((r for r in report if r['year'] == month_date.year), None)
        if not year:
            year = {'year': month_date.year, 'months': []}
            report.append(year)
        year['months'].append({
            'month': month_date.month,
            'count': row['count'],
        })
    return report


def _get_cohorts_by_sid():
    sids = set()
    for row in db.session.execute('SELECT sids FROM cohort_filters'):
        sid_list = row['sids']
        if sid_list:
            sids.update(sid_list)
    cohorts_by_sid = dict((sid, []) for sid in sids)
    for row in db.session.execute('SELECT id, name, sids FROM cohort_filters ORDER BY id'):
        cohort = {'id': row['id'], 'name': row['name']}
        for sid in row['sids']:
            cohorts_by_sid[sid].append(cohort)
    return cohorts_by_sid


def _get_curated_groups_by_sid():
    query = 'SELECT DISTINCT sid FROM student_group_members'
    curated_groups_by_sid = dict((row['sid'], []) for row in db.session.execute(query))
    query = """
        SELECT g.id, g.name, m.sid FROM student_groups g
        JOIN student_group_members m ON m.student_group_id = g.id
        ORDER BY g.id
    """
    for row in db.session.execute(query):
        sid = row['sid']
        curated_groups_by_sid[sid].append({'id': row['id'], 'name': row['name']})
    return curated_groups_by_sid


def _get_students_report(sids):
    students = {}
    for student in get_student_degrees_report(sids):
        sid = student['sid']
        if sid not in students:
            students[sid] = {
                **{key: student[key] for key in ('sid', 'uid', 'student_first_name', 'student_last_name')},
                'degree_awarded_dates': [],
                'degree_awarded_names': [],
            }
        students[sid]['degree_awarded_dates'].append(student['degree_awarded_date'])
        students[sid]['degree_awarded_names'].append(student['degree_awarded_name'])
    return students
