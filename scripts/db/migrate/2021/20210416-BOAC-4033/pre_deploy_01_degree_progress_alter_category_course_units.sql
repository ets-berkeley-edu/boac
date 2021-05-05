BEGIN;

ALTER TABLE degree_progress_categories ALTER COLUMN course_units TYPE int4range USING NULLIF(FORMAT('[%s]', course_units), '[]')::int4range;

COMMIT;