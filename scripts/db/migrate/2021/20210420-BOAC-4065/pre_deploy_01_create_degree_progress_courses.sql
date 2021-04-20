BEGIN;

CREATE TABLE degree_progress_courses (
  section_id INTEGER NOT NULL,
  sid VARCHAR(80) NOT NULL,
  term_id INTEGER NOT NULL,
  category_id INTEGER,
  grade VARCHAR(50) NOT NULL,
  display_name character varying(255) NOT NULL,
  note text,
  units INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE degree_progress_courses OWNER TO boac;
ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_pkey PRIMARY KEY (section_id, sid, term_id);

ALTER TABLE ONLY degree_progress_courses
    ADD CONSTRAINT degree_progress_courses_category_id_fkey
    FOREIGN KEY (category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;

COMMIT;
