BEGIN;

--
-- Register UID as BOA admin user
--
-- USAGE:
--   psql ... -v uid=123456 -v created_by=987654 -f scripts/db/tools/add_admin_user.sql
--

-- Create admin user
INSERT INTO authorized_users (uid, created_by, is_admin, created_at, updated_at)
  SELECT :'uid', :'created_by', true, now(), now()
  WHERE NOT EXISTS (SELECT id FROM authorized_users WHERE uid = :'uid');

-- If the UID represents an existing user, ensure deleted_at is null and can_access_canvas_data is true.
UPDATE authorized_users SET deleted_at = NULL WHERE uid = :'uid';
UPDATE authorized_users SET can_access_canvas_data = true WHERE uid = :'uid';

-- Done

COMMIT;
