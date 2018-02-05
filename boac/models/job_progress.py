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
        if row:
            db.session.query(JsonCache).filter(JsonCache.key == self.key()).delete()
        return (row and row.json)

    def get(self):
        row = JsonCache.query.filter_by(key=self.key()).first()
        return (row and row.json)

    def key(self):
        return f'job_{self.key_suffix}'

    def start(self):
        start_json = {
            'start': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end': None,
            'steps': [],
        }
        row = JsonCache.query.filter_by(key=self.key()).first()
        if row:
            progress = row.json
            if progress['start'] and not progress['end']:
                app.logger.error('Cannot start job {} already in progress'.format(self.key()))
                return False
            row.json = start_json
            std_commit()
        else:
            row = JsonCache(key=self.key(), json=start_json)
            db.session.add(row)
            std_commit()
        return start_json

    def update(self, step_description):
        row = JsonCache.query.filter_by(key=self.key()).first()
        if row is None:
            app.logger.error(f'No active progress record to append step "{step_description}" to {self.key()}')
            return False
        progress = row.json
        if (not progress.get('start')) or progress.get('end') or (progress.get('steps') is None):
            app.logger.error(f'Progress record {progress} not ready to append step {step_description} to {self.key()}')
            return False
        step = '{} : {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            step_description,
        )
        progress['steps'].append(step)
        update_jsonb_row(row)
        return progress

    def end(self):
        row = JsonCache.query.filter_by(key=self.key()).first()
        if row and row.json.get('start'):
            progress = row.json
            if progress.get('end'):
                app.logger.error('Job {} is already ended: {}'.format(self.key(), progress))
                return False
            progress['end'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_jsonb_row(row)
            return progress
        else:
            app.logger.error('Job {} has not started'.format(self.key()))
            return False
