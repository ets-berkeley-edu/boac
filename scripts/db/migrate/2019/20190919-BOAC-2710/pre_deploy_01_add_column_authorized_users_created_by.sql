BEGIN;

ALTER TABLE authorized_users ADD COLUMN created_by varchar(255);

UPDATE authorized_users SET created_by = '2040';

ALTER TABLE ONLY authorized_users ALTER COLUMN created_by SET NOT NULL;

COMMIT;
