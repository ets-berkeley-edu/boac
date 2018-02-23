BEGIN;

CREATE TABLE normalized_cache_course_sections (
  term_id INTEGER NOT NULL,
  section_id INTEGER NOT NULL,
  dept_name VARCHAR(255) NOT NULL,
  dept_code VARCHAR(10) NOT NULL,
  catalog_id VARCHAR(255) NOT NULL,
  display_name VARCHAR(255) NOT NULL,
  title VARCHAR(255) NOT NULL,
  instruction_format VARCHAR(10),
  section_num VARCHAR(255),
  units INTEGER,
  meeting_days VARCHAR(20)[],
  meeting_times VARCHAR(20)[],
  locations VARCHAR(255)[],
  instructors VARCHAR(255)[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (term_id, section_id)
);

CREATE INDEX normalized_cache_course_sections_term_id_idx ON normalized_cache_course_sections (term_id);
CREATE INDEX normalized_cache_course_sections_section_id_idx ON normalized_cache_course_sections (section_id);


-- Map students to course sections
CREATE TABLE normalized_cache_enrollments (
  term_id INTEGER NOT NULL,
  section_id INTEGER NOT NULL,
  sid VARCHAR(80) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (term_id, section_id, sid),
  FOREIGN KEY (term_id, section_id) REFERENCES normalized_cache_course_sections (term_id, section_id) ON DELETE CASCADE,
  FOREIGN KEY (sid) REFERENCES students (sid) ON DELETE CASCADE
);

CREATE INDEX normalized_cache_enrollments_term_id_idx ON normalized_cache_enrollments (term_id);
CREATE INDEX normalized_cache_enrollments_section_id_idx ON normalized_cache_enrollments (section_id);
CREATE INDEX normalized_cache_enrollments_sid_idx ON normalized_cache_enrollments (sid);

COMMIT;
