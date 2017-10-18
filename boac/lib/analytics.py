import math
from statistics import mean
from boac.externals import canvas
from flask import current_app as app
import pandas


def merge_analytics_for_user(user_courses, canvas_user_id):
    if user_courses:
        for course in user_courses:
            student_summaries = canvas.get_student_summaries(course['canvasCourseId'])
            if not student_summaries:
                course['analytics'] = {'error': 'Unable to retrieve analytics'}
            else:
                course['analytics'] = analytics_from_summary_feed(student_summaries, canvas_user_id, course)


def mean_course_analytics_for_user(user_courses, canvas_user_id):
    merge_analytics_for_user(user_courses, canvas_user_id)
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
        app.logger.error('Canvas ID {} not found in student summaries for course site {}'.format(canvas_user_id, canvas_course['id']))
        return {'error': 'Unable to retrieve analytics'}

    def analytics_for_column(column_name):
        column_zscore = zscore(df, student_row, column_name)
        return {
            'courseDeciles': quantiles(df[column_name], 10),
            'student': {
                'raw': student_row[column_name].values[0].item(),
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
    return [series.quantile(n / count) for n in range(0, count + 1)]


def zptile(z_score):
    """Derive percentile from zscore"""
    return 50 * (math.erf(z_score / 2 ** .5) + 1)


def zscore(dataframe, row, column_name):
    """Given a dataframe, an individual row, and column name, return a zscore for the value at that position"""
    return (row[column_name].values[0] - dataframe[column_name].mean()) / dataframe[column_name].std(ddof=0)
