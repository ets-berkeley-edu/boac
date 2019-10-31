BEGIN;

  ALTER TABLE cohort_filters ADD COLUMN alert_count integer;

COMMIT;
