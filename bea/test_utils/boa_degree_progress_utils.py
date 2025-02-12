"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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
from datetime import datetime
import time

from bea.models.degree_progress.degree_check import DegreeCheck
from bea.models.degree_progress.degree_check_template import DegreeCheckTemplate
from bea.test_utils import utils
from boac import db, std_commit
from flask import current_app as app
from sqlalchemy import text


def get_degree_templates():
    sql = """SELECT degree_progress_templates.id,
                    degree_progress_templates.degree_name,
                    degree_progress_templates.created_at
               FROM degree_progress_templates
              WHERE degree_progress_templates.deleted_at IS NULL
                AND degree_progress_templates.student_sid IS NULL
           ORDER BY degree_progress_templates.id ASC"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    templates = []
    for row in results:
        templates.append(DegreeCheckTemplate({
            'template_id': row['id'],
            'name': row['degree_name'],
            'created_date': utils.date_to_local_tz(row['created_at']),
        }))
    return templates


def set_new_template_id(template):
    sql = f"""SELECT id
                FROM degree_progress_templates
               WHERE degree_name = '{template.name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    template.template_id = result['id']
    template.created_date = datetime.today().date()
    app.logger.info(f'Template id is {template.template_id}')


def get_student_degrees(student):
    sql = f"""SELECT degree_progress_templates.id,
                     degree_progress_templates.degree_name,
                     degree_progress_templates.updated_at,
                     authorized_users.uid
                FROM degree_progress_templates
                JOIN authorized_users
                  ON authorized_users.id = degree_progress_templates.updated_by
               WHERE student_sid = '{student.sid}'
            ORDER BY degree_progress_templates.updated_at DESC"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    degrees = []
    for row in results:
        degrees.append(DegreeCheckTemplate({
            'template_id': row['id'],
            'name': row['degree_name'],
            'updated_date': utils.date_to_local_tz(row['updated_at']),
        }))
    return degrees


def get_degree_sids_by_degree_name(degree_name):
    sql = f"""SELECT student_sid
                FROM degree_progress_templates
               WHERE degree_name = '{degree_name}'
                 AND student_sid IS NOT NULL
            ORDER BY student_sid ASC"""
    app.logger.info(sql)
    results = db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    sids = []
    for row in results:
        sids.append(str(row['student_sid']))
    app.logger.info(f'Degree SIDs are {sids}')
    return sids


def get_degree_id_by_name(degree, student):
    sql = f"""SELECT id
                FROM degree_progress_templates
               WHERE degree_name = '{degree.name}'
                 AND student_sid = '{student.sis_id}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return result['id']


def degree_id(degree):
    return degree.check_id if isinstance(degree, DegreeCheck) else degree.template_id


def set_unit_reqt_id(degree, unit_reqt):
    sql = f"""SELECT id
                FROM degree_progress_unit_requirements
               WHERE name = '{unit_reqt.name}' AND template_id = '{degree_id(degree)}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    unit_reqt.reqt_id = result['id']
    app.logger.info(f'Unit reqt id is {unit_reqt.reqt_id}')


def set_course_reqt_id(degree, course_reqt):
    sql = f"""SELECT id
                FROM degree_progress_categories
               WHERE name = '{course_reqt.name}'
                 AND template_id = '{degree_id(degree)}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    course_reqt.course_id = result['id']
    app.logger.info(f'Course reqt id is {course_reqt.course_id}')


def set_dummy_course_reqt_id(course_reqt):
    sql = f"""SELECT id
                FROM degree_progress_categories
               WHERE category_type = 'Placeholder: Course Copy'
                 AND parent_category_id = '{course_reqt.parent.category_id}'
                 AND name = '{course_reqt.completed_course.name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    course_reqt.course_id = result['id']
    app.logger.info(f'Course reqt id is {course_reqt.course_id}')


def set_category_id(degree, category):
    sql = f"""SELECT id
                FROM degree_progress_categories
               WHERE name = '{category.name}'
                 AND template_id = '{degree_id(degree)}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    category.category_id = result['id']
    app.logger.info(f'Reqt category id is {category.category_id}')


def set_degree_manual_course_id(degree, course):
    course.degree_check = degree
    sql = f"""SELECT max(id) AS id
                FROM degree_progress_courses
               WHERE degree_check_id = '{degree.check_id}'
                 AND display_name = '{course.name}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    app.logger.info(f"Manual course {course.name} id is {result['id']}")
    course.course_id = result['id']


def set_degree_sis_course_id(degree, course):
    sql = f"""SELECT id
                FROM degree_progress_courses
               WHERE degree_check_id = '{degree.check_id}'
                 AND term_id = '{course.term_id}'
                 AND section_id = '{course.ccn}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    app.logger.info(f"Completed course {course.name} id is {result['id']}")
    course.course_id = result['id']


def set_degree_sis_course_copy_id(degree, course):
    sql = f"""SELECT max(id) AS id
                FROM degree_progress_courses
               WHERE degree_check_id = '{degree.check_id}'
                 AND term_id = '{course.course_orig.term_id}'
                 AND section_id = '{course.course_orig.ccn}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    app.logger.info(f"Course copy {course.name} id is {result['id']}")
    course.course_id = result['id']


def update_degree_course_grade(degree, course, student, grade):
    sql = f"""UPDATE degree_progress_courses
                 SET grade = '{grade}'
               WHERE section_id = {course.ccn}
                 AND sid = '{student.sid}'
                 AND term_id = '{course.term_id}'
                 AND degree_check_id = '{degree.check_id}'"""
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)
    course.grade = grade
    time.sleep(utils.get_short_timeout())


def set_degree_check_ids(degree_check):
    sql = f"""SELECT id
                FROM degree_progress_templates
               WHERE degree_name = '{degree_check.name}'
                 AND student_sid = '{degree_check.student.sid}'"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    app.logger.info(f"Degree check id is {result['id']}")
    degree_check.check_id = result['id']
    degree_check.created_date = datetime.today()
    for units in degree_check.unit_reqts:
        set_unit_reqt_id(degree_check, units)
    for cat in degree_check.categories:
        set_category_id(degree_check, cat)
        for course in cat.course_reqts:
            set_course_reqt_id(degree_check, course)
        for sub_cat in cat.sub_categories:
            set_category_id(degree_check, sub_cat)
            for sub_course in sub_cat.course_reqts:
                set_course_reqt_id(degree_check, sub_course)
