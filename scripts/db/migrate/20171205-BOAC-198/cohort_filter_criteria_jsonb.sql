BEGIN;

ALTER TABLE cohort_filters ALTER COLUMN filter_criteria SET DATA TYPE jsonb USING filter_criteria::jsonb;

COMMIT;
