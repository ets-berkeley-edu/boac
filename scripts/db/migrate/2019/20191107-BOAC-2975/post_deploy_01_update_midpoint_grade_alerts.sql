BEGIN;

-- The WHERE clause is included so as to return an accurate count of records updated.
UPDATE alerts
SET message = replace(message, ' midterm grade of ', ' midpoint deficient grade of ')
WHERE message LIKE '% midterm grade of %';

COMMIT;
