"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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

from boac import db, std_commit
from boac.models.json_cache import JsonCache, update_jsonb_row
from flask import current_app as app


class JobProgress:
    # Key to track the progress of a very long-running job.
    REFRESH_TERM = 'refresh_term'

    def __init__(self, key=REFRESH_TERM):
        self.key_suffix = key

    def delete(self):
        row = JsonCache.query.filter_by(key=self.key()).first()
        job_state = row.json if row else None
        if row:
            db.session.query(JsonCache).filter(JsonCache.key == self.key()).delete()
        std_commit()
        return job_state

    def get(self):
        row = JsonCache.query.filter_by(key=self.key()).first()
        job_state = row.json if row else None
        std_commit()
        return job_state

    def key(self):
        return f'job_{self.key_suffix}'

    def start(self, properties={}):
        start_json = {
            'start': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end': None,
            'steps': [],
        }
        start_json.update(properties)
        row = JsonCache.query.filter_by(key=self.key()).first()
        if row:
            progress = row.json
            if progress['start'] and not progress['end']:
                app.logger.error(f'Cannot start job {self.key()} already in progress')
                return False
            row.json = start_json
            std_commit()
        else:
            row = JsonCache(key=self.key(), json=start_json)
            db.session.add(row)
            std_commit()
        return start_json

    def update(self, step_description, properties={}):
        row = JsonCache.query.filter_by(key=self.key()).first()
        if row is None:
            app.logger.error(f'No active progress record to append step "{step_description}" to {self.key()}')
            return False
        progress = row.json
        if (not progress.get('start')) or progress.get('end') or (progress.get('steps') is None):
            app.logger.error(f'Progress record {progress} not ready to append step {step_description} to {self.key()}')
            return False
        progress.update(properties)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        step = f'{now} : {step_description}'
        progress['steps'].append(step)
        update_jsonb_row(row)
        return progress

    def end(self):
        row = JsonCache.query.filter_by(key=self.key()).first()
        if row and row.json.get('start'):
            progress = row.json
            if progress.get('end'):
                app.logger.error(f'Job {self.key()} is already ended: {progress}')
                return False
            progress['end'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_jsonb_row(row)
            return progress
        else:
            app.logger.error(f'Job {self.key()} has not started')
            return False
