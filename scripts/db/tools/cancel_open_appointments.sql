BEGIN;

INSERT INTO appointment_events
(appointment_id, user_id, event_type, cancel_reason, cancel_reason_explained, created_at)
SELECT
  appointments.id AS appointment_id,
  NULL AS user_id,
  'cancelled' AS event_type,
  'Cancelled by system' AS cancel_reason,
  NULL AS cancel_reason_explained,
  now() AS created_at
FROM appointments
WHERE (status = 'reserved' OR status = 'waiting') AND deleted_at IS NULL;

UPDATE appointments
SET status = 'cancelled', updated_at = now()
WHERE (status = 'reserved' OR status = 'waiting') AND deleted_at IS NULL;

COMMIT;
