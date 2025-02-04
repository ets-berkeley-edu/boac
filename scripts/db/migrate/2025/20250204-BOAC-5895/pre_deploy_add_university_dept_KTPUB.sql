BEGIN;

INSERT INTO university_depts
  (dept_code, dept_name, created_at, updated_at)
VALUES
  ('KTPUB', 'School of Public Health', now(), now());

COMMIT;
