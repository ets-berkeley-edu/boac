BEGIN;

ALTER TABLE drop_in_advisors DROP COLUMN deleted_at;

COMMIT;