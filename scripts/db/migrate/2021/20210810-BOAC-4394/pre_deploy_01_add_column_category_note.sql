BEGIN;

ALTER TABLE degree_progress_categories ADD COLUMN note TEXT;

COMMIT;
