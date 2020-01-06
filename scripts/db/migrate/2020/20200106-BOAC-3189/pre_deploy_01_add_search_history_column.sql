BEGIN;

ALTER TABLE authorized_users ADD COLUMN search_history CHARACTER VARYING[];

COMMIT;
