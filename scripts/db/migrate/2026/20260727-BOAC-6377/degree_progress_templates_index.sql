BEGIN;

CREATE INDEX IF NOT EXISTS degree_progress_templates_parent_template_id_student_sid_idx
    ON degree_progress_templates (parent_template_id, student_sid);

COMMIT;
