BEGIN;

--
-- Remove user from BOA authorized_users and json_cache.
--
-- USAGE:
--   psql ... -v uid=123456 -f scripts/db/tools/delete_authorized_user.sql
--

DELETE FROM authorized_users WHERE uid = :'uid';

DELETE FROM json_cache WHERE key = 'calnet_user_for_uid_' || :'uid';

-- Done

COMMIT;
