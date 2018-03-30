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

from boac.lib.mockingdata import fixture
from boac.models.json_cache import stow
from flask import current_app as app
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text


# Lazy init to support testing.
data_loch_db = None


def safe_execute(string):
    global data_loch_db
    if data_loch_db is None:
        data_loch_db = create_engine(app.config['DATA_LOCH_URI'])
    try:
        s = text(string)
        dbresp = data_loch_db.execute(s)
    except sqlalchemy.exc.SQLAlchemyError as err:
        app.logger.error(f'SQL {s} threw {err}')
        return None
    rows = dbresp.fetchall()
    return [dict(r) for r in rows]


@stow('loch_page_views_{course_id}', for_term=True)
def get_course_page_views(course_id, term_id):
    return _get_course_page_views(course_id)


@fixture('loch_page_views_{course_id}.csv')
def _get_course_page_views(course_id):
    sql = f"""SELECT
            sis_login_id AS uid, canvas_user_id, user_page_views AS loch_page_views
              FROM boac_analytics.page_views_zscore
              WHERE canvas_course_id={course_id}
              ORDER BY sis_login_id
        """
    return safe_execute(sql)


@stow('loch_scores_{course_id}', for_term=True)
def get_course_scores(course_id, term_id):
    return _get_course_scores(course_id)


@fixture('loch_scores_{course_id}.csv')
def _get_course_scores(course_id):
    sql = f"""SELECT
              user_id as canvas_user_id, current_score
              FROM boac_analytics.user_course_scores
              WHERE course_id={course_id}
              ORDER BY canvas_user_id
        """
    return safe_execute(sql)


@stow('loch_on_time_submissions_relative_to_user_{course_id}_{user_id}', for_term=True)
def get_on_time_submissions_relative_to_user(course_id, user_id, term_id):
    return _get_on_time_submissions_relative_to_user(course_id, user_id)


@fixture('loch_on_time_submissions_relative_to_user_{course_id}_{user_id}.csv')
def _get_on_time_submissions_relative_to_user(course_id, user_id):
    sql = f"""SELECT user_id as canvas_user_id,
        COUNT(CASE WHEN assignment_status = 'on_time' THEN 1 ELSE NULL END) AS on_time_submissions
        FROM boac_analytics.assignment_submissions_scores
        WHERE assignment_id IN
        (
          SELECT DISTINCT assignment_id FROM boac_analytics.assignment_submissions_scores
          WHERE user_id = {user_id} AND course_id = {course_id}
        )
        GROUP BY user_id
        HAVING count(*) = (
          SELECT count(*) FROM boac_analytics.assignment_submissions_scores
          WHERE user_id = {user_id} AND course_id = {course_id}
        )
        """
    return safe_execute(sql)


@stow('loch_submissions_turned_in_relative_to_user_{course_id}_{user_id}', for_term=True)
def get_submissions_turned_in_relative_to_user(course_id, user_id, term_id):
    return _get_submissions_turned_in_relative_to_user(course_id, user_id)


@fixture('loch_submissions_turned_in_relative_to_user_{course_id}_{user_id}.csv')
def _get_submissions_turned_in_relative_to_user(course_id, user_id):
    sql = f"""SELECT user_id as canvas_user_id,
        COUNT(CASE WHEN assignment_status IN ('on_time', 'late', 'submitted') THEN 1 ELSE NULL END) AS submissions_turned_in
        FROM boac_analytics.assignment_submissions_scores
        WHERE assignment_id IN
        (
          SELECT DISTINCT assignment_id FROM boac_analytics.assignment_submissions_scores
          WHERE user_id = {user_id} AND course_id = {course_id}
        )
        GROUP BY user_id
        HAVING count(*) = (
          SELECT count(*) FROM boac_analytics.assignment_submissions_scores
          WHERE user_id = {user_id} AND course_id = {course_id}
        )
        """
    return safe_execute(sql)
