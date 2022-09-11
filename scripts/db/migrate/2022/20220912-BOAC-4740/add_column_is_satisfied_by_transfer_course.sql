BEGIN;

ALTER TABLE degree_progress_categories
  ADD COLUMN is_satisfied_by_transfer_course BOOLEAN DEFAULT FALSE NOT NULL;

COMMIT;
