BEGIN;

-- Map students to course sections
CREATE TABLE normalized_cache_enrollments (
  term_id INTEGER NOT NULL,
  section_id INTEGER NOT NULL,
  sid VARCHAR(80) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (term_id, section_id, sid),
  FOREIGN KEY (sid) REFERENCES students (sid) ON DELETE CASCADE
);

CREATE INDEX normalized_cache_enrollments_term_id_idx ON normalized_cache_enrollments (term_id);
CREATE INDEX normalized_cache_enrollments_section_id_idx ON normalized_cache_enrollments (section_id);
CREATE INDEX normalized_cache_enrollments_sid_idx ON normalized_cache_enrollments (sid);

COMMIT;
