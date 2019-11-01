BEGIN;

-- Clear ALL data in appointments table
DELETE FROM appointments;

-- Create enum
CREATE TYPE appointment_event_types AS ENUM ('canceled', 'checked_in', 'reserved', 'waiting');

-- Dropped columns are effectively moving to the new 'appointment_events' table. The created_by column will be
-- restored with a foreign key constraint (authorized_users).
DROP INDEX appointments_created_by_idx;

-- Drop search index, in prep for changes below
DROP MATERIALIZED VIEW IF EXISTS appointments_fts_index;
DROP INDEX IF EXISTS idx_appointments_fts_index;

ALTER TABLE appointments
    DROP COLUMN checked_in_at,
    DROP COLUMN checked_in_by,
    DROP COLUMN cancel_reason,
    DROP COLUMN cancel_reason_explained,
    DROP COLUMN canceled_at,
    DROP COLUMN canceled_by,
    DROP COLUMN created_by,
    DROP COLUMN updated_by,
    DROP COLUMN deleted_by;

-- New column!
ALTER TABLE appointments ADD COLUMN status appointment_event_types NOT NULL;

-- created_by foreign-key constraint
ALTER TABLE appointments ADD COLUMN created_by INTEGER;
ALTER TABLE ONLY appointments
    ADD CONSTRAINT appointments_created_by_fkey FOREIGN KEY (created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
CREATE INDEX appointments_created_by_idx ON appointments USING btree (created_by);

-- updated_by foreign-key constraint
ALTER TABLE appointments ADD COLUMN updated_by INTEGER;
ALTER TABLE ONLY appointments
    ADD CONSTRAINT appointments_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

-- deleted_by foreign-key constraint
ALTER TABLE appointments ADD COLUMN deleted_by INTEGER;
ALTER TABLE ONLY appointments
    ADD CONSTRAINT appointments_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

-- This new table is sort of like an audit log.
CREATE TABLE appointment_events (
  id SERIAL PRIMARY KEY,
  appointment_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  event_type appointment_event_types NOT NULL,
  cancel_reason VARCHAR(255),
  cancel_reason_explained VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,

  FOREIGN KEY (appointment_id) REFERENCES appointments (id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES authorized_users (id) ON DELETE CASCADE
);

CREATE INDEX appointment_events_appointment_id_idx ON appointment_events (appointment_id);
CREATE INDEX appointment_events_user_id_idx ON appointment_events (user_id);

-- Recreate search index, based on changes above
CREATE MATERIALIZED VIEW appointments_fts_index AS (
  SELECT
    a.id,
    to_tsvector('english', trim(concat(a.details, ' ', e.cancel_reason, ' ', e.cancel_reason_explained))) AS fts_index
  FROM appointments a
    JOIN appointment_events e ON e.appointment_id = a.id
  WHERE
    details IS NOT NULL
    AND deleted_at IS NULL
);
CREATE INDEX idx_appointments_fts_index ON appointments_fts_index USING gin(fts_index);

COMMIT;
