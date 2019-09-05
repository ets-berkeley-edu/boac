BEGIN;

--
-- Per UID provided, set 'deleted_at' to now() and flush json_cache.
--
-- USAGE:
--   psql ... -v uid=123456 -f scripts/db/tools/delete_authorized_user.sql
--

UPDATE authorized_users SET deleted_at = now() WHERE uid = :'uid';

DELETE FROM json_cache WHERE key = 'calnet_user_for_uid_' || :'uid';

-- Done

COMMIT;
