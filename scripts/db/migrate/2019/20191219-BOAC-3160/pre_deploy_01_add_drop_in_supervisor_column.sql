BEGIN;

ALTER TABLE drop_in_advisors ADD COLUMN is_supervisor_on_call boolean DEFAULT false;

UPDATE drop_in_advisors SET is_supervisor_on_call = false;

ALTER TABLE ONLY drop_in_advisors ALTER COLUMN is_supervisor_on_call SET NOT NULL;

DELETE FROM json_cache WHERE key LIKE 'boa_user_session_%';

COMMIT;
