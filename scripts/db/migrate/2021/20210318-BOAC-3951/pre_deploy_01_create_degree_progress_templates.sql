BEGIN;

CREATE TABLE degree_progress_templates (
  id integer NOT NULL,
  degree_name character varying(255) NOT NULL,
  advisor_dept_codes character varying[] NOT NULL,
  student_sid character varying(80),
  created_at timestamp with time zone NOT NULL,
  created_by integer NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL,
  deleted_at timestamp with time zone
);
ALTER TABLE degree_progress_templates OWNER TO app_boa;
CREATE SEQUENCE degree_progress_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE degree_progress_templates_id_seq OWNER TO app_boa;
ALTER SEQUENCE degree_progress_templates_id_seq OWNED BY degree_progress_templates.id;
ALTER TABLE ONLY degree_progress_templates ALTER COLUMN id SET DEFAULT nextval('degree_progress_templates_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_templates
    ADD CONSTRAINT degree_progress_templates_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_templates
    ADD CONSTRAINT degree_progress_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_templates
    ADD CONSTRAINT degree_progress_templates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS ONLY degrees DROP CONSTRAINT IF EXISTS degrees_deleted_by_fkey;
ALTER TABLE IF EXISTS ONLY degrees DROP CONSTRAINT IF EXISTS degrees_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY degrees DROP CONSTRAINT IF EXISTS degrees_created_by_fkey;
ALTER TABLE IF EXISTS ONLY degrees DROP CONSTRAINT IF EXISTS degrees_pkey;
DROP TABLE IF EXISTS degrees;
DROP SEQUENCE IF EXISTS degrees_id_seq;

COMMIT;