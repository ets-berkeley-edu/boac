BEGIN;

DELETE FROM degree_progress_courses;

ALTER TABLE IF EXISTS ONLY degree_progress_courses
  DROP CONSTRAINT IF EXISTS degree_progress_courses_category_id_course_unique_constraint;

ALTER TABLE degree_progress_courses ADD COLUMN degree_check_id INTEGER NOT NULL;
ALTER TABLE ONLY degree_progress_courses
  ADD CONSTRAINT degree_progress_courses_degree_check_id_fkey
  FOREIGN KEY (degree_check_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;

ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_category_id_course_unique_constraint
    UNIQUE (category_id, degree_check_id, section_id, sid, term_id);

COMMIT;
