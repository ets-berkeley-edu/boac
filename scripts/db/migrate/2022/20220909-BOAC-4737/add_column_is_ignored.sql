BEGIN;

ALTER TABLE degree_progress_categories ADD COLUMN is_ignored BOOLEAN DEFAULT FALSE NOT NULL;

COMMIT;
