BEGIN;

--
-- Map UID to the specified department.
--
-- USAGE:
--   psql ... -v uid=123456 -v created_by=987654 -v dept_code='QCADV' -f scripts/db/tools/add_advisor_per_dept.sql
--

-- Create user if not exists
INSERT INTO authorized_users (uid, created_by, is_admin, created_at, updated_at)
  SELECT :'uid', :'created_by', false, now(), now()
  WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = :'uid');

-- If the UID represents an existing user, ensure deleted_at is null and can_access_canvas_data is true.
UPDATE authorized_users SET deleted_at = NULL WHERE uid = :'uid';
UPDATE authorized_users SET can_access_canvas_data = true WHERE uid = :'uid';

-- Add advisor access
INSERT INTO university_dept_members (university_dept_id, authorized_user_id, is_advisor, automate_membership, created_at, updated_at)
  SELECT dep.id, usr.id, true, false, now(), now()
  FROM authorized_users usr, university_depts dep
  WHERE usr.uid = :'uid' AND dep.dept_code = :'dept_code';

-- Done

COMMIT;
