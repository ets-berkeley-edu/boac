BEGIN;

CREATE TABLE drop_in_advisors (
    authorized_user_id INTEGER NOT NULL,
    dept_code character varying(255) NOT NULL,
    is_available BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE drop_in_advisors OWNER TO boac;
ALTER TABLE drop_in_advisors
    ADD CONSTRAINT drop_in_advisors_pkey PRIMARY KEY (authorized_user_id, dept_code);

ALTER TABLE ONLY drop_in_advisors
    ADD CONSTRAINT drop_in_advisors_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;
