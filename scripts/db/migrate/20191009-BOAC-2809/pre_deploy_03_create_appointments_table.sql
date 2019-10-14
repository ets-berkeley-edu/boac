BEGIN;

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    advisor_uid character varying(255),
    advisor_name character varying(255),
    advisor_role character varying(255),
    advisor_dept_codes character varying[],
    student_sid character varying(80) NOT NULL,
    details text,
    dept_code character varying(80) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    created_by character varying(255) NOT NULL,
    checked_in_at timestamp with time zone,
    checked_in_by character varying(255),
    cancel_reason character varying(255),
    cancel_reason_explained character varying(255),
    canceled_at timestamp with time zone,
    canceled_by character varying(255),
    updated_at timestamp with time zone NOT NULL,
    updated_by character varying(255) NOT NULL,
    deleted_at timestamp with time zone,
    deleted_by character varying(255)
);


CREATE INDEX appointments_created_by_idx ON appointments USING btree (created_by);
CREATE INDEX appointments_advisor_uid_idx ON appointments USING btree (advisor_uid);
CREATE INDEX appointments_student_sid_idx ON appointments USING btree (student_sid);

ALTER TABLE ONLY appointment_topics
    ADD CONSTRAINT appointment_topics_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE;

COMMIT;
