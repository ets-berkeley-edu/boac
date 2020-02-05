BEGIN;

CREATE TYPE cohort_domain_types AS ENUM ('default', 'admitted_students');

ALTER TABLE cohort_filters ADD COLUMN domain cohort_domain_types;

UPDATE cohort_filters SET domain='default';

ALTER TABLE cohort_filters ALTER COLUMN domain SET NOT NULL;

COMMIT;
