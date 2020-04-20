BEGIN;

ALTER TABLE appointments_read 
    DROP CONSTRAINT appointments_read_appointment_id_fkey;

ALTER TABLE appointments_read
    ALTER COLUMN appointment_id SET DATA TYPE character varying(255);

ALTER TABLE appointments_read
    ALTER COLUMN appointment_id SET NOT NULL;

COMMIT;