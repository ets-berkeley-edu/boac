BEGIN;

INSERT INTO peer_advising_topics
  (topic, created_at)
VALUES
  ('Academic Difficulty or Probation', now()),
  ('Change of College', now()),
  ('Change of Major', now()),
  ('Degree Check', now()),
  ('Degree Requirements', now()),
  ('Double Major / Simultaneous Degree', now()),
  ('Enrollment: Waitlist, Swaps, etc.', now()),
  ('Grading Options (e.g., Pass/No Pass)', now()),
  ('Incompletes', now()),
  ('Late Change of Class Schedule', now()),
  ('Major Declaration', now()),
  ('Other', now()),
  ('Petitions (e.g., support with a petition process)', now()),
  ('Program Planning, Semester or Longer Term', now()),
  ('Reduced Course Load', now()),
  ('Transfer Coursework', now()),
  ('Unit Ceiling / Expected Graduation Term (EGT)', now()),
  ('Withdrawal / Readmission', now());

COMMIT;
