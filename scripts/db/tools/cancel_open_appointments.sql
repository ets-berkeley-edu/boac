UPDATE appointments
SET cancelled_at = now(), cancel_reason = 'Cancelled by system'
WHERE cancelled_at IS NULL AND checked_in_at IS NULL;
