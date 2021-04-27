BEGIN;

UPDATE pg_enum SET enumlabel = 'Course Requirement'
WHERE enumlabel = 'Course' AND enumtypid = (
  SELECT oid FROM pg_type WHERE typname = 'degree_progress_category_types'
);

COMMIT;
