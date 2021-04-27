BEGIN;

ALTER TABLE degree_progress_courses DROP CONSTRAINT degree_progress_courses_pkey;

ALTER TABLE degree_progress_courses ADD COLUMN id SERIAL PRIMARY KEY;

ALTER TABLE degree_progress_courses
  ADD CONSTRAINT degree_progress_courses_category_id_course_unique_constraint
    UNIQUE (category_id, section_id, sid, term_id);

COMMIT;
