BEGIN;

ALTER TABLE alerts ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

UPDATE alerts SET deleted_at = updated_at WHERE active IS FALSE;

ALTER TABLE alerts DROP COLUMN active;

COMMIT;
