BEGIN;

ALTER TABLE degree_progress_courses ADD COLUMN ignore BOOLEAN DEFAULT FALSE;

UPDATE degree_progress_courses SET ignore = FALSE;

ALTER TABLE ONLY degree_progress_courses ALTER COLUMN ignore SET NOT NULL;

COMMIT;
