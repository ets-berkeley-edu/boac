BEGIN;

ALTER TABLE ONLY degree_progress_courses ALTER COLUMN section_id DROP NOT NULL;
ALTER TABLE ONLY degree_progress_courses ALTER COLUMN term_id DROP NOT NULL;

ALTER TABLE degree_progress_courses ADD COLUMN accent_color VARCHAR(255);
ALTER TABLE degree_progress_courses ADD COLUMN manually_created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE degree_progress_courses ADD COLUMN manually_created_by INTEGER;

ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_manually_created_by_fkey
    FOREIGN KEY (manually_created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

ALTER TABLE IF EXISTS ONLY degree_progress_courses
  DROP CONSTRAINT IF EXISTS degree_progress_courses_category_id_course_unique_constraint;

ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_category_id_course_unique_constraint
    UNIQUE (category_id, degree_check_id, display_name, section_id, sid, term_id);

COMMIT;
