BEGIN;

CREATE TABLE normalized_cache_students (
  sid VARCHAR(80) PRIMARY KEY REFERENCES students (sid) ON DELETE CASCADE,
  gpa DECIMAL,
  level VARCHAR(9),
  units DECIMAL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX normalized_cache_students_gpa_idx ON normalized_cache_students (gpa);
CREATE INDEX normalized_cache_students_level_idx ON normalized_cache_students (level);
CREATE INDEX normalized_cache_students_units_idx ON normalized_cache_students (units);

CREATE TABLE normalized_cache_student_majors (
  sid VARCHAR(80) NOT NULL REFERENCES students (sid) ON DELETE CASCADE,
  major VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (sid, major)
);

CREATE INDEX normalized_cache_student_majors_sid_idx ON normalized_cache_student_majors (sid);
CREATE INDEX normalized_cache_student_majors_major_idx ON normalized_cache_student_majors (major);

COMMIT;
