BEGIN;

ALTER TABLE university_dept_members ADD COLUMN is_scheduler boolean DEFAULT false;

UPDATE university_dept_members SET is_scheduler = false;

ALTER TABLE ONLY university_dept_members ALTER COLUMN is_scheduler SET NOT NULL;

DELETE FROM json_cache WHERE key LIKE 'boa_user_session_%';

COMMIT;
