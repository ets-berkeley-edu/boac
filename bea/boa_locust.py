"""
BOA load test script for use with the Locust tool (https://locust.io).

Usage:

Start Locust with this file.

    locust -f [path_to_file]/boa_locust.py

In your browser, go to localhost:8089 to start tests and view charts.

Visit https://locust.io for more information.
"""

from itertools import groupby
import os
import random

from bea.test_utils import boa_utils
from bea.test_utils import utils
from boac import db, std_commit
from boac.externals import data_loch
from boac.factory import create_app
from locust import between, HttpUser, task, TaskSet
from pyquery import PyQuery
from sqlalchemy import text

os.environ['BOAC_ENV'] = 'bea'

_app = create_app()
ctx = _app.app_context()
ctx.push()
config = _app.config

"""
Load test data.
"""


def _row_to_note_draft(row):
    return {
        'id': row['note_id'],
        'subject': row['subject'],
        'body': row['body'],
        'sid': row['sid'],
    }


def _row_to_cohort(row):
    return {
        'id': row['cohort_id'],
        'student_count': row['student_count'],
        'filter_criteria': row['filter_criteria'],
    }


class TestData:
    students = data_loch.safe_execute_rds(
        f"""SELECT sid,
                   uid
              FROM student.student_profile_index
          ORDER BY last_name
            OFFSET {random.randint(0, 30000)}
             LIMIT 50""")

    search_phrases = ['meet', 'Angh', 'Sandeep', 'June', 'Math', 'Appointment', 'PUB', ',', 'History']

    users = []
    user_draft_note_sql = """SELECT au.uid AS uid,
                                    notes.id AS note_id,
                                    notes.body,
                                    notes.subject,
                                    notes.sid
                               FROM authorized_users au
                               JOIN notes on notes.author_uid = au.uid
                              WHERE au.deleted_at IS NULL
                                AND au.can_access_canvas_data IS TRUE
                                AND notes.is_draft IS TRUE
                                AND notes.deleted_at IS NULL"""
    user_draft_note_results = db.session.execute(text(user_draft_note_sql))
    std_commit(allow_test_environment=True)
    for uid, rows in groupby(user_draft_note_results, lambda x: x['uid']):
        users.append({
            'uid': uid,
            'note_drafts': [_row_to_note_draft(r) for r in rows],
        })

    cohort_users = []
    uids = utils.in_op([u['uid'] for u in users])
    user_cohort_results = db.session.execute(
        text(f"""SELECT au.uid AS uid,
                        cf.id AS cohort_id,
                        cf.student_count,
                        cf.filter_criteria
                   FROM authorized_users au
                   JOIN cohort_filters cf on cf.owner_id = au.id
                  WHERE au.deleted_at IS NULL
                    AND au.uid IN ({uids})
               ORDER BY uid"""))
    std_commit(allow_test_environment=True)
    for uid, rows in groupby(user_cohort_results, lambda x: x['uid']):
        cohort_users.append({
            'uid': uid,
            'cohorts': [_row_to_cohort(r) for r in rows],
        })

    for u in users:
        for c in cohort_users:
            if u['uid'] == c['uid']:
                u.update(c)


"""
Define user tasks.
"""


def sample(_list):
    return _list[random.randint(0, len(_list) - 1)]


class BoaTaskSet(TaskSet):

    def on_start(self):
        self.user.user_data = sample(TestData.users)
        self.load_front_end()
        self.login()

    def on_stop(self):
        self.logout()

    def load_front_end(self):
        html_response = self.client.get('/login')
        pq = PyQuery(html_response.content)
        asset_paths = []
        asset_paths += [e.attrib.get('href') for e in pq('link')]
        asset_paths += [e.attrib.get('src') for e in pq('script')]
        for path in asset_paths:
            if path:
                self.client.get(path)

    def login(self, uid=None):
        if uid is None:
            uid = self.user.user_data['uid']
        self.client.post(
            '/api/auth/dev_auth_login',
            json={
                'uid': uid,
                'password': config['DEVELOPER_AUTH_PASSWORD'],
            },
        )

    def logout(self):
        self.client.get('/api/auth/logout')

    @task(1)
    def load_home_page(self):
        self.client.get('/api/cohorts/by_dept_code/coeng')
        self.client.get('/api/cohorts/by_dept_code/qcadv')
        self.client.get('/api/cohorts/by_dept_code/zceee')
        self.client.get('/api/curated_groups/by_dept_code/coeng')
        self.client.get('/api/curated_groups/by_dept_code/qcadv')
        self.client.get('/api/curated_groups/by_dept_code/zceee')
        self.client.get('/api/service_announcement')
        self.client.get('/api/note_templates/my')
        self.client.get('/api/topics/all?includeDeleted=false')
        self.client.get('/api/notes/my_drafts')

    @task(2)
    def search(self):
        self.client.post(
            '/api/search',
            json={
                'searchPhrase': sample(TestData.search_phrases),
                'students': 'True',
                'courses': 'True',
                'notes': 'True',
            },
        )

    @task(3)
    def load_cohort_page(self):
        try:
            cohort = sample(self.user.user_data['cohorts'])
            self.client.get(f"/api/cohort/{cohort['id']}", name='/api/cohort/[id]')
            self.client.post('/api/cohort/filter_options/me', json={'existingFilters': []})
            self.client.post('/api/cohort/translate_to_filter_options/me',
                             json={'filterCriteria': cohort['filter_criteria']})
        except KeyError:
            pass

    @task(4)
    def load_student_page(self):
        student = sample(TestData.students)
        self.client.get(f"/api/student/by_uid/{student['uid']}", name='/api/student/by_uid/[uid]')

    @task(5)
    def update_drafts(self):
        note = sample(self.user.user_data['note_drafts'])
        self.client.post(
            '/api/notes/update',
            data={
                'id': str(note['id']),
                'body': (note['body'] or ''),
                'cohortIds': [],
                'curatedGroupIds': [],
                'isDraft': 'True',
                'isPrivate': 'False',
                'sids': (note['sid'] or ''),
                'subject': (note['subject'] or ''),
            },
            files={},
        )


"""
Hatch a locust.
"""


class BoaUser(HttpUser):
    tasks = [BoaTaskSet]
    host = boa_utils.get_boa_base_url()
    wait_time = between(1, 3)
    user_data = {}

    def __init__(self, parent):
        super().__init__(parent)
