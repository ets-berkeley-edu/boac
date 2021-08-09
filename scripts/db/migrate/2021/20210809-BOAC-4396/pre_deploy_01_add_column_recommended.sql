BEGIN;

ALTER TABLE degree_progress_categories ADD COLUMN is_recommended BOOLEAN DEFAULT FALSE NOT NULL;

COMMIT;
