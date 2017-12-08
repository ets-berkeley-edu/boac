BEGIN;

  -- We will add NOT NULL constraint after data migration
  ALTER TABLE team_members ADD COLUMN first_name VARCHAR(255);
  ALTER TABLE team_members ADD COLUMN last_name VARCHAR(255);

COMMIT;
