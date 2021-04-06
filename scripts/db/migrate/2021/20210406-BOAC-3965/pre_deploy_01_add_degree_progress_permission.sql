BEGIN;

CREATE TYPE generic_permission_types AS ENUM ('read', 'read_write');

ALTER TABLE authorized_users ADD COLUMN degree_progress_permission generic_permission_types;

COMMIT;
