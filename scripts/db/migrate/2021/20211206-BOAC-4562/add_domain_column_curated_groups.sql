BEGIN;

ALTER TABLE student_groups ADD COLUMN domain cohort_domain_types;

UPDATE student_groups SET domain='default';

ALTER TABLE student_groups ALTER COLUMN domain SET NOT NULL;

COMMIT;
