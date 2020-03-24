BEGIN TRANSACTION;

CREATE TYPE weekday_types AS ENUM ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');

CREATE TABLE appointment_availability (
    id INTEGER NOT NULL,
    authorized_user_id INTEGER NOT NULL,
    dept_code VARCHAR NOT NULL,
    weekday weekday_types NOT NULL,
    date_override DATE,
    start_time TIME,
    end_time TIME,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE appointment_availability OWNER TO boac;
CREATE SEQUENCE appointment_availability_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE appointment_availability_id_seq OWNER TO boac;
ALTER SEQUENCE appointment_availability_id_seq OWNED BY appointment_availability.id;
ALTER TABLE ONLY appointment_availability ALTER COLUMN id SET DEFAULT nextval('appointment_availability_id_seq'::regclass);
ALTER TABLE ONLY appointment_availability
    ADD CONSTRAINT appointment_availability_pkey PRIMARY KEY (id);

CREATE INDEX appointment_availability_authorized_user_id_dept_code_idx ON appointment_availability USING btree (authorized_user_id, dept_code);
CREATE INDEX appointment_availability_weekday_idx ON appointment_availability USING btree (weekday);
CREATE INDEX appointment_availability_date_override_idx ON appointment_availability USING btree (date_override);

ALTER TABLE ONLY appointment_availability
    ADD CONSTRAINT appointment_availability_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;