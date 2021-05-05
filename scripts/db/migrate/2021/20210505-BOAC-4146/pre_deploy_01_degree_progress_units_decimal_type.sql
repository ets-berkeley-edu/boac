BEGIN;

ALTER TABLE degree_progress_courses ALTER COLUMN units TYPE DECIMAL (4,1);
ALTER TABLE degree_progress_unit_requirements ALTER COLUMN min_units TYPE DECIMAL (4,1);

-- Converting from column type 'int4range' to type 'numrange'
ALTER TABLE degree_progress_categories ADD COLUMN course_units_numrange numrange;

UPDATE degree_progress_categories d1
  SET course_units_numrange = numrange(LOWER(d2.course_units), UPPER(d2.course_units))
  FROM degree_progress_categories d2
  WHERE  d1.id = d2.id AND d2.course_units IS NOT NULL;

ALTER TABLE degree_progress_categories DROP COLUMN course_units;
ALTER TABLE degree_progress_categories RENAME COLUMN course_units_numrange TO course_units;

COMMIT;
