BEGIN;

CREATE TYPE drop_in_advisor_status_types AS ENUM ('on_duty_advisor', 'on_duty_supervisor', 'off_duty_waitlist', 'off_duty_no_waitlist');

ALTER TABLE drop_in_advisors ADD COLUMN status drop_in_advisor_status_types DEFAULT 'off_duty_no_waitlist' NOT NULL;

UPDATE drop_in_advisors SET status = 'on_duty_advisor' WHERE is_available IS TRUE;

ALTER TABLE drop_in_advisors DROP COLUMN is_available;

COMMIT;