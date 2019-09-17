BEGIN;

ALTER TABLE tool_settings ALTER COLUMN value TYPE text;

COMMIT;
