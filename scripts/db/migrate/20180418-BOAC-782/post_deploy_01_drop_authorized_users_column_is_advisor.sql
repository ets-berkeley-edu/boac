BEGIN;

ALTER TABLE authorized_users DROP COLUMN IF EXISTS is_advisor;
ALTER TABLE authorized_users DROP COLUMN IF EXISTS is_director;

COMMIT;
