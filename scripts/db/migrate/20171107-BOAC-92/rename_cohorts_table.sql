BEGIN;

ALTER TABLE IF EXISTS cohorts RENAME TO team_members;

ALTER INDEX IF EXISTS cohorts_pkey RENAME TO team_members_pkey;

ALTER SEQUENCE IF EXISTS cohorts_id_seq RENAME TO team_members_id_seq;

COMMIT;
