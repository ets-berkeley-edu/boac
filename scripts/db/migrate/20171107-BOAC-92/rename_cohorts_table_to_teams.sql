BEGIN;

ALTER TABLE IF EXISTS cohorts RENAME TO teams;

ALTER INDEX IF EXISTS cohorts_pkey RENAME TO teams_pkey;

ALTER SEQUENCE IF EXISTS cohorts_id_seq RENAME TO teams_id_seq;

COMMIT;
