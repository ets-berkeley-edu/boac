BEGIN;

CREATE TABLE degree_progress_unit_requirements (
  id integer NOT NULL,
  template_id integer NOT NULL,
  name character varying(255) NOT NULL,
  min_units integer NOT NULL,
  created_at timestamp with time zone NOT NULL,
  created_by integer NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL
);
ALTER TABLE degree_progress_unit_requirements OWNER TO app_boa;
CREATE SEQUENCE degree_progress_unit_requirements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE degree_progress_unit_requirements_id_seq OWNER TO app_boa;
ALTER SEQUENCE degree_progress_unit_requirements_id_seq OWNED BY degree_progress_unit_requirements.id;
ALTER TABLE ONLY degree_progress_unit_requirements ALTER COLUMN id SET DEFAULT nextval('degree_progress_unit_requirements_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_template_id_fkey FOREIGN KEY (template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_created_by_fkey FOREIGN KEY (created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_unit_requirements
    ADD CONSTRAINT degree_progress_unit_requirements_name_template_id_unique_const UNIQUE (name, template_id);
CREATE INDEX degree_progress_unit_requirements_template_id_idx ON degree_progress_unit_requirements (template_id);

COMMIT;
