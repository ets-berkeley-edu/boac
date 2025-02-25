BEGIN;

-- Add columns to already existing tables
ALTER TABLE notes ADD COLUMN IF NOT EXISTS peer_advising_department_id INTEGER;

ALTER TABLE notes ADD COLUMN IF NOT EXISTS note_template_id INTEGER;

ALTER TABLE note_templates ADD COLUMN IF NOT EXISTS peer_advising_department_id INTEGER;

-- Create *peer_advising_departments* table
CREATE TABLE IF NOT EXISTS peer_advising_departments (
  id integer NOT NULL,
  name character varying(255) NOT NULL,
  university_dept_id integer NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL
);

-- Create *peer_advising_department_members* table
-- a DO block here for the role_type_enum since it already exists in dev
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_type
    WHERE typname = 'role_type_enum'
  ) THEN
    CREATE TYPE role_type_enum AS ENUM ('peer_advisor', 'peer_advisor_manager');
  END IF;
END
$$;

CREATE TABLE IF NOT EXISTS peer_advising_department_members (
  peer_advising_department_id integer NOT NULL,
  authorized_user_id integer NOT NULL,
  role_type role_type_enum NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  deleted_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS peer_advising_topics (
  id INTEGER NOT NULL,
  topic VARCHAR(50) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE SEQUENCE IF NOT EXISTS peer_advising_topics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE peer_advising_topics_id_seq OWNER TO app_boa;
ALTER SEQUENCE peer_advising_topics_id_seq OWNED BY peer_advising_topics.id;
ALTER TABLE ONLY peer_advising_topics ALTER COLUMN id SET DEFAULT nextval('peer_advising_topics_id_seq'::regclass);

-- Drop all foreign keys if they exist
ALTER TABLE ONLY peer_advising_departments
    DROP CONSTRAINT IF EXISTS peer_advising_departments_university_dept_id_fkey;
ALTER TABLE ONLY peer_advising_department_members
    DROP CONSTRAINT IF EXISTS peer_advising_department_members_peer_advising_department_fkey;
ALTER TABLE ONLY peer_advising_department_members
    DROP CONSTRAINT IF EXISTS peer_advising_department_members_authorized_user_id_fkey;

ALTER TABLE ONLY notes
    DROP CONSTRAINT IF EXISTS notes_peer_advising_department_id_fkey;
ALTER TABLE ONLY notes
    DROP CONSTRAINT IF EXISTS notes_note_template_id_fkey;
ALTER TABLE ONLY note_templates
    DROP CONSTRAINT IF EXISTS note_templates_peer_advising_department_id_fkey;

-- Drop all primary keys if they exist
ALTER TABLE ONLY peer_advising_department_members
    DROP CONSTRAINT IF EXISTS peer_advising_department_members_pkey;
ALTER TABLE ONLY peer_advising_topics
    DROP CONSTRAINT IF EXISTS peer_advising_topics_id_pkey;
ALTER TABLE ONLY peer_advising_departments
    DROP CONSTRAINT IF EXISTS peer_advising_departments_pkey;

-- peer_advising_departments table
ALTER TABLE peer_advising_departments OWNER TO app_boa;

CREATE SEQUENCE IF NOT EXISTS peer_advising_departments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE peer_advising_departments_id_seq OWNER TO app_boa;
ALTER SEQUENCE peer_advising_departments_id_seq OWNED BY peer_advising_departments.id;
ALTER TABLE ONLY peer_advising_departments ALTER COLUMN id SET DEFAULT nextval('peer_advising_departments_id_seq'::regclass);

ALTER TABLE ONLY peer_advising_departments
    ADD CONSTRAINT peer_advising_departments_pkey PRIMARY KEY (id);

ALTER TABLE ONLY peer_advising_departments
    ADD CONSTRAINT peer_advising_departments_university_dept_id_fkey FOREIGN KEY (university_dept_id) REFERENCES university_depts(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS peer_advising_departments_university_dept_id_idx ON peer_advising_departments(university_dept_id);

-- peer_advising_department_members table
ALTER TABLE peer_advising_department_members OWNER TO app_boa;

ALTER TABLE peer_advising_department_members
    ADD CONSTRAINT peer_advising_department_members_pkey PRIMARY KEY (peer_advising_department_id, authorized_user_id);

ALTER TABLE ONLY peer_advising_department_members
    ADD CONSTRAINT peer_advising_department_members_peer_advising_department_fkey FOREIGN KEY (peer_advising_department_id) REFERENCES peer_advising_departments(id) ON DELETE CASCADE;

ALTER TABLE ONLY peer_advising_department_members
    ADD CONSTRAINT peer_advising_department_members_authorized_user_id_fkey FOREIGN KEY (authorized_user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

-- peer_advising_topics table
ALTER TABLE peer_advising_topics OWNER TO app_boa;

ALTER TABLE peer_advising_topics
    ADD CONSTRAINT peer_advising_topics_id_pkey PRIMARY KEY (id);

-- notes table
ALTER TABLE notes
    ADD CONSTRAINT notes_peer_advising_department_id_fkey
    FOREIGN KEY (peer_advising_department_id)
    REFERENCES peer_advising_departments(id);

ALTER TABLE notes
    ADD CONSTRAINT notes_note_template_id_fkey
    FOREIGN KEY (note_template_id)
    REFERENCES note_templates(id);

-- note_templates table
ALTER TABLE note_templates
    ADD CONSTRAINT note_templates_peer_advising_department_id_fkey
    FOREIGN KEY (peer_advising_department_id)
    REFERENCES peer_advising_departments(id);

COMMIT;
