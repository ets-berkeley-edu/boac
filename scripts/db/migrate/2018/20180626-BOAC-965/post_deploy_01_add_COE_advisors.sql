BEGIN;

--
-- Create authorized_user and then map his/her UID to the College of Engineering.
--
-- USAGE:
--   psql ... -U boac -v coe_ldap_uid=123456 -f scripts/db/migrate/20180626-BOAC-965/pre_deploy_01_add_COE_advisors.sql
--

CREATE OR REPLACE FUNCTION create_coe_advisor(varchar, varchar) RETURNS VOID AS '
DECLARE
  ldap_uid ALIAS FOR $1;
  coe_dept_code ALIAS FOR $2;
  user_id int;
  coe_dept_id int;
BEGIN
  INSERT INTO authorized_users (uid, is_admin, created_at, updated_at) VALUES (ldap_uid, false, now(), now());
  SELECT id INTO user_id FROM authorized_users WHERE uid = ldap_uid;
  SELECT id INTO coe_dept_id FROM university_depts WHERE dept_code = coe_dept_code;
  INSERT INTO university_dept_members (university_dept_id, authorized_user_id, is_advisor, created_at, updated_at) VALUES (coe_dept_id, user_id, true, now(), now());
END;
' LANGUAGE 'plpgsql';

-- Create 'College of Engineering' if not exists
INSERT INTO university_depts (dept_code, dept_name, created_at, updated_at)
  SELECT
    'COENG', 'College of Engineering', now(), now()
  WHERE
    NOT EXISTS (SELECT id FROM university_depts WHERE dept_code = 'COENG');

-- Add COE advisor if not exists
SELECT create_coe_advisor(:coe_ldap_uid::text, 'COENG')
  WHERE
    NOT EXISTS (SELECT id FROM authorized_users WHERE uid = :coe_ldap_uid::text);

DROP FUNCTION create_coe_advisor(varchar, varchar);

-- Done

COMMIT;
