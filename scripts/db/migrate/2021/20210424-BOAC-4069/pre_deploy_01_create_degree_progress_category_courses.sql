BEGIN;

-- Many-to-many relationship between categories and courses.
-- The 'courses' tables (degree_progress_category_courses) has a composite key (section_id, sid, term_id).

CREATE TABLE degree_progress_category_courses (
  category_id INTEGER NOT NULL,
  section_id INTEGER NOT NULL,
  sid VARCHAR(80) NOT NULL,
  term_id INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (category_id, section_id, sid, term_id)
);

-- Foreign keys
ALTER TABLE ONLY degree_progress_category_courses
  ADD CONSTRAINT degree_progress_category_courses_category_id_fkey
  FOREIGN KEY (category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_category_courses
  ADD CONSTRAINT degree_progress_category_courses_course_id_fkey
  FOREIGN KEY (section_id, sid, term_id) REFERENCES degree_progress_courses(section_id, sid, term_id) ON DELETE CASCADE;

-- app_boa is the owner
ALTER TABLE degree_progress_category_courses OWNER TO app_boa;
ALTER TABLE degree_progress_category_courses_category_id_fkey OWNER TO app_boa;
ALTER TABLE degree_progress_category_courses_course_id_fkey OWNER TO app_boa;

-- Migrate existing data
INSERT INTO degree_progress_category_courses (category_id, section_id, sid, term_id, created_at)
  SELECT c.category_id, c.section_id, c.sid, c.term_id, now()
  FROM degree_progress_courses c
  WHERE category_id IS NOT NULL;

-- Drop the old column
ALTER TABLE ONLY degree_progress_courses DROP COLUMN category_id;

COMMIT;
