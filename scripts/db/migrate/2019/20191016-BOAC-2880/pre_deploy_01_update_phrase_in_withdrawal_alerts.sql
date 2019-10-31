BEGIN;

-- The WHERE clause is not essential. I include it because it'll give us an accurate count of records updated.
UPDATE alerts
SET message = replace(message, 'Withdrawal! Student has withdrawn from the', 'Student is no longer enrolled in the')
WHERE message LIKE 'Withdrawal! Student has withdrawn from the%';

COMMIT;
