BEGIN;

INSERT INTO topics (topic, available_in_notes, available_in_appointments, created_at)
  VALUES ('Pre-Med/Pre-Health', false, true, now());
INSERT INTO topics (topic, available_in_notes, available_in_appointments, created_at)
  VALUES ('Readmission, Withdrawal', false, true, now());
INSERT INTO topics (topic, available_in_notes, available_in_appointments, created_at)
  VALUES ('Schedule Planning, Late Action', false, true, now());
INSERT INTO topics (topic, available_in_notes, available_in_appointments, created_at)
  VALUES ('SAP', false, true, now());

UPDATE topics SET available_in_appointments=true
  WHERE topic IN ('Advising Holds', 'Majors', 'Study Abroad');

DELETE FROM topics
  WHERE topic IN ('Appeal Procedures', 'Career Planning', 'Crisis Advising', 'Graduate Advising', 'Student/Faculty mediation');

COMMIT;
