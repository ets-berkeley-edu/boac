BEGIN;

CREATE TYPE appointment_student_contact_types AS ENUM ('email', 'phone');
CREATE TYPE appointment_types AS ENUM ('Drop-in', 'Scheduled');

ALTER TABLE appointments ADD COLUMN scheduled_time TIMESTAMP with time zone;
ALTER TABLE appointments ADD COLUMN student_contact_info character varying(80);
ALTER TABLE appointments ADD COLUMN student_contact_type appointment_student_contact_types;

ALTER TABLE appointments ALTER COLUMN appointment_type
  TYPE appointment_types
  USING appointment_type::appointment_types;

CREATE INDEX appointments_scheduled_time_idx ON appointments USING btree (scheduled_time);

COMMIT;
