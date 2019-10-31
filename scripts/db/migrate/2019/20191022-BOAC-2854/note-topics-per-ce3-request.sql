BEGIN;

UPDATE topics SET topic='Other / Reason not listed' WHERE topic='Other';

INSERT INTO topics (topic, available_in_notes, available_in_appointments, created_at) VALUES
  ('Financial Aid/Budgeting', true, false, now()),
  ('Post-Graduation', true, false, now());

COMMIT;
