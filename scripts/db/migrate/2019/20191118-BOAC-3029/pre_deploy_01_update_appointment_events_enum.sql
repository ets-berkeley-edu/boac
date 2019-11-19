BEGIN;

DELETE FROM appointments;
DELETE FROM appointment_events;

-- Rename existing TYPE
ALTER TYPE appointment_event_types RENAME TO appointment_event_types_OLD;

-- Create new TYPE
CREATE TYPE appointment_event_types AS ENUM ('cancelled', 'checked_in', 'reserved', 'waiting');

-- Update tables to use the new TYPE
ALTER TABLE appointments ALTER COLUMN status TYPE appointment_event_types USING status::text::appointment_event_types;
ALTER TABLE appointment_events ALTER COLUMN event_type TYPE appointment_event_types USING event_type::text::appointment_event_types;

-- Remove old TYPE
DROP TYPE appointment_event_types_OLD;

COMMIT;
