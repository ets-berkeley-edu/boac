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


import math
from statistics import mean
from boac.externals import canvas, data_loch
from boac.models.json_cache import stow
from flask import current_app as app
import pandas


def merge_analytics_for_user(user_courses, uid, sid, canvas_user_id, term_id):
    if user_courses:
        for course in user_courses:
            canvas_course_id = course['canvasCourseId']
            course_code = course['courseCode']
            student_summaries = canvas.get_student_summaries(canvas_course_id, term_id)
            if not student_summaries:
                analytics = {'error': 'Unable to retrieve analytics'}
            else:
                analytics = analytics_from_summary_feed(student_summaries, canvas_user_id, canvas_course_id)
                enrollments = canvas.get_course_enrollments(canvas_course_id, term_id)
                analytics.update(analytics_from_canvas_course_enrollments(enrollments, canvas_user_id))
                assignment_analytics = analytics_from_canvas_course_assignments(
                    course_id=canvas_course_id,
                    course_code=course_code,
                    uid=uid,
                    sid=sid,
                    term_id=term_id,
                )
                analytics.update(assignment_analytics)
                analytics.update({'loch': analytics_from_loch(uid, canvas_user_id, canvas_course_id, term_id)})
            course['analytics'] = analytics


def mean_course_analytics_for_user(user_courses, uid, sid, canvas_user_id, term_id):
    merge_analytics_for_user(user_courses, uid, sid, canvas_user_id, term_id)
    mean_values = {}
    # TODO Remove misleading assignmentsOnTime metric.
    for metric in ['assignmentsOnTime', 'pageViews', 'participations', 'courseCurrentScore']:
        percentiles = []
        for course in user_courses:
            if course['analytics'].get(metric):
                percentile = course['analytics'][metric]['student']['percentile']
                if percentile and not math.isnan(percentile):
                    percentiles.append(percentile)
        if len(percentiles):
            mean_percentile = mean(percentiles)
            mean_values[metric] = {'percentile': mean_percentile, 'displayPercentile': ordinal(mean_percentile)}
        else:
            mean_values[metric] = None
    return mean_values


@stow('average_student_per_course_{canvas_course_id}', for_term=True)
def get_student_averages(term_id, canvas_course_id):
    summary_feed = canvas.get_student_summaries(course_id=canvas_course_id, term_id=term_id)
    averages = None
    if summary_feed:
        average_student = {
            'id': 0,
            'max_page_views': summary_feed[0]['max_page_views'],
            'max_participations': summary_feed[0]['max_participations'],
            'tardiness_breakdown': {},
        }

        def _add(_student, _key, _average_student):
            _average_student[_key] = (_average_student.get(_key) or 0) + (_student.get(_key) or 0)
        for student in summary_feed:
            # Get sum totals
            _add(student, 'page_views', average_student)
            _add(student, 'participations', average_student)
            tardiness_breakdown = student.get('tardiness_breakdown')
            if tardiness_breakdown:
                target = average_student['tardiness_breakdown']
                _add(tardiness_breakdown, 'floating', target)
                _add(tardiness_breakdown, 'missing', target)
                _add(tardiness_breakdown, 'on_time', target)
                _add(tardiness_breakdown, 'total', target)
                _add(tardiness_breakdown, 'late', target)
        # Calculate averages
        count = len(summary_feed)

        def _average(_average_student, _key):
            if _key in _average_student:
                _average_student[_key] = round(_average_student[_key] / count)
        _average(average_student, 'page_views')
        _average(average_student, 'page_views_level')
        _average(average_student, 'participations')
        _average(average_student, 'participations_level')
        tb = average_student['tardiness_breakdown']
        _average(tb, 'floating')
        _average(tb, 'missing')
        _average(tb, 'on_time')
        _average(tb, 'total')
        _average(tb, 'late')
        averages = analytics_from_summary_feed([average_student], average_student['id'], canvas_course_id)
    return averages


def analytics_from_summary_feed(summary_feed, canvas_user_id, canvas_course_id):
    """Given a student summary feed for a Canvas course, return analytics for a given user."""
    # TODO Remove misleading tardiness_breakdown stats.
    df = pandas.DataFrame(summary_feed, columns=['id', 'page_views', 'participations', 'tardiness_breakdown'])
    df['on_time'] = [row['on_time'] for row in df['tardiness_breakdown']]
    student_row = df.loc[df['id'].values == canvas_user_id]
    if not len(student_row):
        app.logger.error('Canvas ID {} not found in student summaries for course site {}'.format(canvas_user_id, canvas_course_id))
        return {'error': 'Unable to retrieve analytics'}
    return {
        'assignmentsOnTime': analytics_for_column(df, student_row, 'on_time'),
        'pageViews': analytics_for_column(df, student_row, 'page_views'),
        'participations': analytics_for_column(df, student_row, 'participations'),
    }


def analytics_from_canvas_course_enrollments(feed, canvas_user_id):
    filtered_feed = [enr for enr in feed if enr.get('enrollment_state') == 'active']
    df = pandas.DataFrame(filtered_feed, columns=['user_id', 'grades'])
    df['current_score'] = [row['current_score'] for row in df['grades']]
    student_row = df.loc[df['user_id'].values == canvas_user_id]
    if student_row.empty:
        canvas_course_id = feed[0]['course_id']
        app.logger.error('Canvas ID {} not found in enrollments for course site {}'.format(canvas_user_id, canvas_course_id))
        return {'error': 'Unable to retrieve analytics'}
    return {
        'courseCurrentScore': analytics_for_column(df, student_row, 'current_score'),
    }


@stow('analytics_from_canvas_course_assignments_{course_id}_{uid}', for_term=True)
def analytics_from_canvas_course_assignments(course_id, course_code, uid, sid, term_id):
    assignments = canvas.get_assignments_analytics(course_id, uid, term_id)
    if not assignments:
        return {}
    data = {
        'assignmentTotals': {
            'floating': 0,
            'missing': 0,
            'onTime': 0,
            'pastDue': 0,
            'all': 0,
        },
        'assignments': [],
    }
    for assignment in assignments:
        data['assignmentTotals']['all'] += 1
        total_type = assignment['status']
        if total_type == 'on_time':
            total_type = 'onTime'
        elif total_type == 'late':
            total_type = 'pastDue'
        data['assignmentTotals'][total_type] += 1

        # If there is no submission, the Canvas API may return a nil-valued 'submission' property or may leave it out.
        submission = assignment.get(
            'submission',
            {
                'score': None,
                'submitted_at': None,
            },
        )

        assignment_data = {
            'id': assignment['assignment_id'],
            'name': assignment['title'],
            'dueDate': assignment['due_at'],
            'pointsPossible': assignment['points_possible'],
            'status': assignment['status'],
            'score': submission['score'],
            'submittedDate': submission['submitted_at'],
            'maxScore': assignment['max_score'],
            'firstQuartile': assignment['first_quartile'],
            'median': assignment['median'],
            'thirdQuartile': assignment['third_quartile'],
            'minScore': assignment['min_score'],
        }
        data['assignments'].append(assignment_data)
    return data


def _get_canvas_sites_dict(student):
    canvas_sites = student.get('enrollment', {}).get('canvasSites', [])
    return {str(canvas_site['canvasCourseId']): canvas_site for canvas_site in canvas_sites}


def analytics_from_loch(uid, canvas_user_id, canvas_course_id, term_id):
    return {
        'assignmentsOnTime': loch_assignments_on_time(canvas_user_id, canvas_course_id, term_id),
        'currentScores': loch_current_scores(canvas_user_id, canvas_course_id, term_id),
        'pageViews': loch_page_views(uid, canvas_course_id, term_id),
    }


def loch_assignments_on_time(canvas_user_id, canvas_course_id, term_id):
    course_rows = data_loch.get_on_time_submissions_relative_to_user(canvas_course_id, canvas_user_id, term_id)
    if course_rows is None:
        return {'error': 'Unable to retrieve from Data Loch'}
    df = pandas.DataFrame(course_rows, columns=['canvas_user_id', 'on_time_submissions'])
    student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    if course_rows and student_row.empty:
        app.logger.warn(f'Canvas user id {canvas_user_id} not found in Data Loch assignments for course site {canvas_course_id}; will assume 0 score')
        student_row = pandas.DataFrame({'canvas_user_id': [int(canvas_user_id)], 'on_time_submissions': [0]})
        df = df.append(student_row, ignore_index=True)
        # Fetch newly appended row, mostly for the sake of its properly set-up index.
        student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    return analytics_for_column(df, student_row, 'on_time_submissions')


def loch_current_scores(canvas_user_id, canvas_course_id, term_id):
    course_rows = data_loch.get_course_scores(canvas_course_id, term_id)
    if course_rows is None:
        return {'error': 'Unable to retrieve from Data Loch'}
    df = pandas.DataFrame(course_rows, columns=['canvas_user_id', 'current_score'])
    student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    if course_rows and student_row.empty:
        app.logger.warn(f'Canvas id {canvas_user_id} not found in Data Loch current scores for course site {canvas_course_id}; will assume 0 score')
        student_row = pandas.DataFrame({'canvas_user_id': [int(canvas_user_id)], 'current_score': [0]})
        df = df.append(student_row, ignore_index=True)
        # Fetch newly appended row, mostly for the sake of its properly set-up index.
        student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    return analytics_for_column(df, student_row, 'current_score')


def loch_page_views(uid, canvas_course_id, term_id):
    course_rows = data_loch.get_course_page_views(canvas_course_id, term_id)
    if course_rows is None:
        return {'error': 'Unable to retrieve from Data Loch'}
    df = pandas.DataFrame(course_rows, columns=['uid', 'loch_page_views'])
    student_row = df.loc[df['uid'].values == uid]
    if course_rows and student_row.empty:
        app.logger.warn(f'UID {uid} not found in Data Loch page views for course site {canvas_course_id}; will assume 0 score')
        student_row = pandas.DataFrame({'uid': [uid], 'loch_page_views': [0]})
        df = df.append(student_row, ignore_index=True)
        # Fetch newly appended row, mostly for the sake of its properly set-up index.
        student_row = df.loc[df['uid'].values == uid]
    return analytics_for_column(df, student_row, 'loch_page_views')


def analytics_for_column(df, student_row, column_name):
    dfcol = df[column_name]

    # If no data exists for a column, the Pandas 'nunique' function reports zero unique values.
    # However, some feeds (such as Canvas student summaries) return (mostly) zero values rather than empty lists,
    # and we've also seen some Canvas feeds which mix nulls and zeroes.
    # Setting non-numbers to zero works acceptably for the current analyzed feeds.
    dfcol.fillna(0, inplace=True)
    student_row = student_row.fillna(0)

    nunique = dfcol.nunique()
    if nunique == 0 or (nunique == 1 and dfcol.max() == 0.0):
        return {
            'boxPlottable': False,
            'student': {
                'percentile': None,
                'raw': None,
                'roundedUpPercentile': None,
            },
            'courseDeciles': None,
            'displayPercentile': None,
        }

    column_value = student_row[column_name].values[0]
    intuitive_percentile = rounded_up_percentile(dfcol, student_row)
    raw_value = round(column_value.item())
    column_quantiles = quantiles(dfcol, 10)
    column_zscore = zscore(dfcol, column_value)
    comparative_percentile = zptile(column_zscore)

    # If only ten or fewer values are shared across the student population, the 'universal' percentile figure and the
    # box-and-whisker graph will usually look odd. With such sparse data sets, a text summary and an (optional)
    # histogram are more readable.
    box_plottable = (nunique > 10)

    # If all students have the same score, we have no basis for comparison.
    if nunique == 1:
        display_percentile = None
    # Otherwise the intuitive percentile is our best option for display, whether or not the distribution is boxplottable.
    else:
        display_percentile = ordinal(intuitive_percentile)

    return {
        'boxPlottable': box_plottable,
        'student': {
            'percentile': comparative_percentile,
            'raw': raw_value,
            'roundedUpPercentile': intuitive_percentile,
        },
        'courseDeciles': column_quantiles,
        'displayPercentile': display_percentile,
    }


def ordinal(nbr):
    rounded = round(nbr)
    mod_ten = rounded % 10
    if (mod_ten == 1) and (rounded != 11):
        suffix = 'st'
    elif (mod_ten == 2) and (rounded != 12):
        suffix = 'nd'
    elif (mod_ten == 3) and (rounded != 13):
        suffix = 'rd'
    else:
        suffix = 'th'
    return '{}{}'.format(rounded, suffix)


def quantiles(series, count):
    """Return a given number of evenly spaced quantiles for a given series."""
    return [round(series.quantile(n / count)) for n in range(0, count + 1)]


def rounded_up_percentile(dataframe, student_row):
    """Given a dataframe and an individual student row, return a more easily understood meaning of percentile.

    Z-score percentile is useful in a scatterplot to spot outliers in the overall population across contexts.
    (If 90% of the course's students received a score of '5', then one student with a '5' is not called out.)
    Rounded-up matches what non-statisticians would expect when viewing one particular student in one
    particular course context. (If only 10% of the course's students did better than '5', then this student
    with a '5' is in the 90th percentile.)
    """
    percentile = dataframe.rank(pct=True, method='max')[student_row.index].values[0]
    percentile = int(percentile * 100)
    return percentile


def zptile(z_score):
    """Derive percentile from zscore."""
    if z_score is None:
        return None
    else:
        return round(50 * (math.erf(z_score / 2 ** .5) + 1))


def zscore(dataframe, value):
    """Given a dataframe and an individual value, return a zscore."""
    if dataframe.std(ddof=0) == 0:
        return None
    else:
        return (value - dataframe.mean()) / dataframe.std(ddof=0)
