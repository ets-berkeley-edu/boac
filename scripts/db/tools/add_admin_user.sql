BEGIN;

--
-- Register UID as BOA admin user
--
-- USAGE:
--   psql ... -v uid=123456 -f scripts/db/tools/add_admin_user.sql
--

-- Create admin user
INSERT INTO authorized_users (uid, is_admin, created_at, updated_at)
  SELECT :'uid', true, now(), now()
  WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = :'uid');

-- Let us be sure that deleted status is NULL.
UPDATE authorized_users SET deleted_at = NULL WHERE uid = :'uid';

-- Done

COMMIT;
