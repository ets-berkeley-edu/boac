BEGIN;

ALTER TABLE authorized_users ADD COLUMN automate_degree_progress_permission BOOLEAN DEFAULT FALSE;

UPDATE authorized_users
SET automate_degree_progress_permission = CASE
    WHEN degree_progress_permission IS NOT NULL THEN TRUE
    ELSE FALSE
END;

-- Column is not nullable.
ALTER TABLE ONLY authorized_users ALTER COLUMN automate_degree_progress_permission SET NOT NULL;

-- Empty cache
DELETE FROM json_cache WHERE key LIKE 'boa_user_session_%';

COMMIT;
