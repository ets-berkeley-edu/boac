BEGIN;

--
-- Map UID to the specified department.
--
-- USAGE:
--   psql ... -v dept_code='QCADV' -v uid=123456 -f scripts/db/add_advisor_per_dept.sql
--

-- Create user if not exists
INSERT INTO authorized_users (uid, is_admin, created_at, updated_at)
  SELECT :'uid', false, now(), now()
  WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = :'uid');

-- Add advisor access
INSERT INTO university_dept_members (university_dept_id, authorized_user_id, is_advisor, created_at, updated_at)
  SELECT dep.id, usr.id, true, now(), now()
  FROM authorized_users usr, university_depts dep
  WHERE usr.uid = :'uid' AND dep.dept_code = :'dept_code';

-- Done

COMMIT;
