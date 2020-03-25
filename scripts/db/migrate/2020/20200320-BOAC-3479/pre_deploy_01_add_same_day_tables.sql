BEGIN;

DELETE FROM university_dept_members WHERE role = 'scheduler';

CREATE TABLE same_day_advisors (
    authorized_user_id INTEGER NOT NULL,
    dept_code character varying(255) NOT NULL,
    is_available BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE same_day_advisors OWNER TO app_boa;
ALTER TABLE same_day_advisors
    ADD CONSTRAINT same_day_advisors_pkey PRIMARY KEY (authorized_user_id, dept_code);

CREATE TABLE schedulers (
    authorized_user_id INTEGER NOT NULL,
    dept_code character varying(255) NOT NULL,
    drop_in BOOLEAN DEFAULT false NOT NULL,
    same_day BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE schedulers OWNER TO app_boa;
ALTER TABLE schedulers
    ADD CONSTRAINT schedulers_pkey PRIMARY KEY (authorized_user_id, dept_code);

ALTER TABLE ONLY same_day_advisors
    ADD CONSTRAINT same_day_advisors_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

ALTER TABLE ONLY schedulers
    ADD CONSTRAINT schedulers_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;
