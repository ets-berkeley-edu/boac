BEGIN;

ALTER TABLE team_members DROP COLUMN IF EXISTS member_name;

ALTER TABLE team_members ALTER COLUMN first_name SET NOT NULL;
ALTER TABLE team_members ALTER COLUMN last_name SET NOT NULL;

COMMIT;
