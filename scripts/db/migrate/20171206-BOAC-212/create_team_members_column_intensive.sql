BEGIN;

ALTER TABLE team_members
  ADD in_intensive_cohort BOOLEAN NOT NULL
  DEFAULT FALSE;

COMMIT;
