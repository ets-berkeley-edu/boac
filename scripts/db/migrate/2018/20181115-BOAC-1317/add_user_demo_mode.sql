BEGIN;

  ALTER TABLE authorized_users ADD COLUMN in_demo_mode boolean DEFAULT false NOT NULL;

COMMIT;
