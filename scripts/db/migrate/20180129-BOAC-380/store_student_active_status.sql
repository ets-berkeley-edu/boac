BEGIN;

  ALTER TABLE students ADD COLUMN is_active_asc boolean DEFAULT true NOT NULL;
  ALTER TABLE students ADD COLUMN status_asc character varying(80);

COMMIT;
