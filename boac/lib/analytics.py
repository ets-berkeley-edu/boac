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
import time
from boac.externals import data_loch
from flask import current_app as app
import pandas


def merge_analytics_for_user(user_courses, canvas_user_id, term_id):
    if user_courses:
        for course in user_courses:
            canvas_course_id = course['canvasCourseId']
            course['analytics'] = {
                'assignmentsSubmitted': loch_assignments_submitted(canvas_user_id, canvas_course_id, term_id),
            }
            course['analytics'].update(loch_student_analytics(canvas_user_id, canvas_course_id, term_id))


def mean_course_analytics_for_user(user_courses, canvas_user_id, term_id):
    merge_analytics_for_user(user_courses, canvas_user_id, term_id)
    mean_values = {}
    for metric in ['assignmentsSubmitted', 'currentScore', 'lastActivity']:
        percentiles = []
        for course in user_courses:
            percentile = course['analytics'].get(metric, {}).get('student', {}).get('percentile')
            if percentile and not math.isnan(percentile):
                percentiles.append(percentile)
        if len(percentiles):
            mean_percentile = mean(percentiles)
            mean_values[metric] = {
                'displayPercentile': ordinal(mean_percentile),
                'percentile': mean_percentile,
            }
        else:
            mean_values[metric] = None
    return mean_values


def get_student_averages(term_id, canvas_course_id):
    """Average student metrics are disabled; when the time comes to re-implement, we'll take the loch as source."""
    return None


def _get_canvas_sites_dict(student):
    canvas_sites = student.get('enrollment', {}).get('canvasSites', [])
    return {str(canvas_site['canvasCourseId']): canvas_site for canvas_site in canvas_sites}


def loch_assignments_submitted(canvas_user_id, canvas_course_id, term_id):
    course_rows = data_loch.get_submissions_turned_in_relative_to_user(canvas_course_id, canvas_user_id, term_id)
    if course_rows is None:
        return {'error': 'Unable to retrieve from Data Loch'}
    df = pandas.DataFrame(course_rows, columns=['canvas_user_id', 'submissions_turned_in'])
    student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    if course_rows and student_row.empty:
        app.logger.warn(f'Canvas user id {canvas_user_id} not found in Data Loch assignments for course site {canvas_course_id}; will assume 0 score')
        student_row = pandas.DataFrame({'canvas_user_id': [int(canvas_user_id)], 'submissions_turned_in': [0]})
        df = df.append(student_row, ignore_index=True)
        # Fetch newly appended row, mostly for the sake of its properly set-up index.
        student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    return analytics_for_column(df, student_row, 'submissions_turned_in')


def loch_student_analytics(canvas_user_id, canvas_course_id, term_id):
    enrollments = data_loch.get_canvas_course_scores(canvas_course_id, term_id)
    if enrollments is None:
        _error = {'error': 'Unable to retrieve from Data Loch'}
        return {'currentScore': _error, 'lastActivity': _error}
    df = pandas.DataFrame(enrollments, columns=['canvas_user_id', 'current_score', 'last_activity_at'])
    student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    if enrollments and student_row.empty:
        app.logger.warn(f'Canvas user {canvas_user_id} not found in Data Loch for course site {canvas_course_id}')
        student_row = pandas.DataFrame({
            'canvas_user_id': [int(canvas_user_id)],
            'current_score': [None],
            'last_activity_at': [None],
        })
        df = df.append(student_row, ignore_index=True)
        # Fetch newly appended row, mostly for the sake of its properly set-up index.
        student_row = df.loc[df['canvas_user_id'].values == int(canvas_user_id)]
    last_activity = analytics_for_column(df, student_row, 'last_activity_at')
    if last_activity.get('student', {}).get('raw'):
        seconds_since_last_activity = int(time.time()) - last_activity['student']['raw']
        last_activity['student']['daysSinceLastActivity'] = seconds_since_last_activity // (24 * 3600)
    return {
        'currentScore': analytics_for_column(df, student_row, 'current_score'),
        'lastActivity': last_activity,
        'courseEnrollmentCount': len(enrollments),
    }


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

    # The intuitive percentile is our best option for display, whether or not the distribution is boxplottable.
    # Note, however, that if all students have the same score, then all students are in the "100th percentile."
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
    return f'{rounded}{suffix}'


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
