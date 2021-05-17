BEGIN;

ALTER TABLE degree_progress_templates ADD COLUMN parent_template_id INTEGER;

ALTER TABLE ONLY degree_progress_templates
  ADD CONSTRAINT degree_progress_templates_parent_template_id_fkey
  FOREIGN KEY (parent_template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;

COMMIT;