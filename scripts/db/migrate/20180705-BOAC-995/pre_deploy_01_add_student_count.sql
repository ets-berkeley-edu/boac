BEGIN;

  ALTER TABLE cohort_filters ADD COLUMN student_count integer;

COMMIT;