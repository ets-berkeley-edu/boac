BEGIN;

ALTER TABLE ONLY degree_progress_courses ALTER COLUMN grade DROP NOT NULL;

ALTER TABLE IF EXISTS ONLY degree_progress_courses
  DROP CONSTRAINT IF EXISTS degree_progress_courses_category_id_course_unique_constraint;

ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_category_id_course_unique_constraint
    UNIQUE (category_id, degree_check_id, manually_created_at, manually_created_by, section_id, sid, term_id);

COMMIT;
