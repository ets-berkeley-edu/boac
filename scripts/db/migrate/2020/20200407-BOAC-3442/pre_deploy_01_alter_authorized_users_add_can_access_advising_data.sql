BEGIN;

ALTER TABLE authorized_users ADD COLUMN can_access_advising_data boolean DEFAULT true NOT NULL;

COMMIT;