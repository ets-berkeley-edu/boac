BEGIN;

UPDATE degree_progress_categories
SET course_units = FORMAT('%s,%s', 
    LEAST(LEFT(course_units,1), RIGHT(course_units,1)),
    GREATEST(LEFT(course_units,1), RIGHT(course_units,1))
)
WHERE course_units IS NOT NULL;

ALTER TABLE degree_progress_categories ALTER COLUMN course_units TYPE int4range USING NULLIF(FORMAT('[%s]', course_units), '[]')::int4range;

COMMIT;