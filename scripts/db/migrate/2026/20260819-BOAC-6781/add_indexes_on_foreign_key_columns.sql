
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_categories_parent_category_id_idx          ON degree_progress_categories(parent_category_id int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_category_unit_requirements_category_id_idx ON degree_progress_category_unit_requirements(category_id int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_notes_updated_by_idx                       ON degree_progress_notes(updated_by int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_templates_updated_by_idx                   ON degree_progress_templates(updated_by int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_templates_parent_template_id_idx           ON degree_progress_templates(parent_template_id int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_templates_created_by_idx                   ON degree_progress_templates(created_by int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_unit_requirements_updated_by_idx           ON degree_progress_unit_requirements(updated_by int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS degree_progress_unit_requirements_created_by_idx           ON degree_progress_unit_requirements(created_by int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS notes_peer_advising_department_id_idx                      ON notes(peer_advising_department_id int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS notes_note_template_id_idx                                 ON notes(note_template_id int4_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS notes_parent_note_id_idx                                   ON notes(parent_note_id int4_ops);
