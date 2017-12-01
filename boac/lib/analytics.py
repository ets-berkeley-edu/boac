import math
from statistics import mean
from boac.externals import canvas
from boac.lib.berkeley import sis_term_id_for_name
from flask import current_app as app
import pandas


def merge_analytics_for_user(user_courses, canvas_user_id, term_name):
    term_id = sis_term_id_for_name(term_name)
    if user_courses:
        for course in user_courses:
            student_summaries = canvas.get_student_summaries(course['canvasCourseId'], term_id)
            if not student_summaries:
                course['analytics'] = {'error': 'Unable to retrieve analytics'}
            else:
                course['analytics'] = analytics_from_summary_feed(student_summaries, canvas_user_id, course)


def mean_course_analytics_for_user(user_courses, canvas_user_id, term_name):
    merge_analytics_for_user(user_courses, canvas_user_id, term_name)
    meanValues = {}
    for metric in ['assignmentsOnTime', 'pageViews', 'participations']:
        percentiles = []
        for course in user_courses:
            if course['analytics'].get(metric):
                percentile = course['analytics'][metric]['student']['percentile']
                if percentile and not math.isnan(percentile):
                    percentiles.append(percentile)
        if len(percentiles):
            meanValues[metric] = mean(percentiles)
        else:
            meanValues[metric] = None
    return meanValues


def analytics_from_summary_feed(summary_feed, canvas_user_id, canvas_course):
    """Given a student summary feed for a Canvas course, return analytics for a given user"""
    df = pandas.DataFrame(summary_feed, columns=['id', 'page_views', 'participations', 'tardiness_breakdown'])
    df.fillna(0, inplace=True)
    df['on_time'] = df['tardiness_breakdown'].map(lambda t: t['on_time'])

    student_row = df.loc[df['id'].values == canvas_user_id]
    if not len(student_row):
        canvas_course_id = canvas_course.get('canvasCourseId') or '[None]'
        app.logger.error('Canvas ID {} not found in student summaries for course site {}'.format(canvas_user_id, canvas_course_id))
        return {'error': 'Unable to retrieve analytics'}

    def analytics_for_column(column_name):
        dataframe = df[column_name]
        column_value = student_row[column_name].values[0]
        column_zscore = zscore(dataframe, column_value)
        column_quantiles = quantiles(dataframe, 10)
        insufficient_data = (column_quantiles[-1] < app.config['MEANINGFUL_STATS_MINIMUM'])
        return {
            'insufficientData': insufficient_data,
            'courseDeciles': column_quantiles,
            'student': {
                'raw': column_value.item(),
                'zscore': column_zscore,
                'percentile': zptile(column_zscore),
            },
        }

    return {
        'assignmentsOnTime': analytics_for_column('on_time'),
        'pageViews': analytics_for_column('page_views'),
        'participations': analytics_for_column('participations'),
    }


def quantiles(series, count):
    """Return a given number of evenly spaced quantiles for a given series"""
    return [round(series.quantile(n / count)) for n in range(0, count + 1)]


def zptile(z_score):
    """Derive percentile from zscore"""
    if z_score is None:
        return None
    else:
        return round(50 * (math.erf(z_score / 2 ** .5) + 1))


def zscore(dataframe, value):
    """Given a dataframe and an individual value, return a zscore"""
    if dataframe.std(ddof=0) == 0:
        return None
    else:
        return (value - dataframe.mean()) / dataframe.std(ddof=0)
