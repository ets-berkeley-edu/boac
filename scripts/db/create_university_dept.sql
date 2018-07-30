BEGIN;

--
-- Create university_dept with dept_code and dept_name. For example:
--
-- USAGE:
--   psql ... -v dept_code="'COE'" -v dept_name="'College of Engineering'" -f scripts/db/create_university_dept.sql
--

-- Create department, if not exists
INSERT INTO university_depts (dept_code, dept_name, created_at, updated_at)
  SELECT
    :dept_code::text, :dept_name::text, now(), now()
  WHERE
    NOT EXISTS (SELECT id FROM university_depts WHERE dept_code = :dept_code::text);

COMMIT;
