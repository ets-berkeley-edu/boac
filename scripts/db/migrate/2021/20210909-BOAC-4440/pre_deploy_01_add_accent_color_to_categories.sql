BEGIN;

ALTER TABLE degree_progress_categories ADD COLUMN accent_color VARCHAR(255);

COMMIT;
