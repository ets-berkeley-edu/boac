BEGIN;

ALTER TABLE appointment_events
    ADD COLUMN advisor_id INTEGER;

ALTER TABLE appointment_events
    ADD CONSTRAINT appointment_events_advisor_id_fkey FOREIGN KEY (advisor_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;