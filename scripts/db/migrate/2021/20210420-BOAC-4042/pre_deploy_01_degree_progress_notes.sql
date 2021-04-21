BEGIN;

CREATE TABLE degree_progress_notes (
  template_id integer NOT NULL,
  body text NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL
);
ALTER TABLE degree_progress_notes OWNER TO app_boa;
ALTER TABLE ONLY degree_progress_notes
    ADD CONSTRAINT degree_progress_notes_pkey PRIMARY KEY (template_id);
ALTER TABLE ONLY degree_progress_notes
    ADD CONSTRAINT degree_progress_notes_template_id_fkey FOREIGN KEY (template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_notes
    ADD CONSTRAINT degree_progress_notes_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;