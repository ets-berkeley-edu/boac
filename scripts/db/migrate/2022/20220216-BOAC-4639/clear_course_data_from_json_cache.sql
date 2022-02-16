BEGIN;

DELETE FROM json_cache WHERE key LIKE '%-sis_section_%';

COMMIT;
