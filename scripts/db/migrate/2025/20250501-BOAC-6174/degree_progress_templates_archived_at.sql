BEGIN;

ALTER TABLE degree_progress_templates ADD COLUMN archived_at TIMESTAMP WITH TIME ZONE;

COMMIT;
