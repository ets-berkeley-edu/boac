BEGIN;

CREATE TABLE appointments_read (
    appointment_id INTEGER NOT NULL,
    viewer_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE ONLY appointments_read
    ADD CONSTRAINT appointments_read_pkey PRIMARY KEY (viewer_id, appointment_id);

CREATE INDEX appointments_read_appointment_id_idx ON appointments_read USING btree (appointment_id);
CREATE INDEX appointments_read_viewer_id_idx ON appointments_read USING btree (viewer_id);

ALTER TABLE ONLY appointments_read
    ADD CONSTRAINT appointments_read_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE;

ALTER TABLE ONLY appointments_read
    ADD CONSTRAINT appointments_read_viewer_id_fkey FOREIGN KEY (viewer_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;
