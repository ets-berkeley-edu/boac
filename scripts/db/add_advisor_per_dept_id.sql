BEGIN;

--
-- Map UID to the specified department.
--
-- USAGE:
--   psql ... -v dept_id=2 -v uid=123456 -f scripts/db/add_advisor_per_dept_id.sql
--

CREATE OR REPLACE FUNCTION create_authorized_user(varchar) RETURNS VOID AS '
DECLARE
  ldap_uid ALIAS FOR $1;
BEGIN
  INSERT INTO authorized_users (uid, is_admin, created_at, updated_at) VALUES (ldap_uid, false, now(), now());
END;
' LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION give_user_advisor_privileges(int, varchar) RETURNS VOID AS '
DECLARE
  dept_id ALIAS FOR $1;
  ldap_uid ALIAS FOR $2;
  user_id int;
BEGIN
  SELECT id INTO user_id FROM authorized_users WHERE uid = ldap_uid;
  INSERT INTO university_dept_members (university_dept_id, authorized_user_id, is_advisor, created_at, updated_at) VALUES (dept_id, user_id, true, now(), now());
END;
' LANGUAGE 'plpgsql';

-- Create user if not exists
SELECT create_authorized_user(:uid::text)
  WHERE
    NOT EXISTS (SELECT id FROM authorized_users WHERE uid = :uid::text);

-- Add advisor if not exists
SELECT give_user_advisor_privileges(:dept_id::int, :uid::text);

-- Drop functions
DROP FUNCTION create_authorized_user(varchar);
DROP FUNCTION give_user_advisor_privileges(int, varchar);

-- Done

COMMIT;
