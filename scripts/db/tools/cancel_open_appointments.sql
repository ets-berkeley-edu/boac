UPDATE appointments
SET canceled_at = now(), cancel_reason = 'Canceled by system'
WHERE canceled_at IS NULL AND checked_in_at IS NULL;
