BEGIN;

    ALTER TABLE cohort_filters ADD COLUMN sids VARCHAR(80)[];

COMMIT;
