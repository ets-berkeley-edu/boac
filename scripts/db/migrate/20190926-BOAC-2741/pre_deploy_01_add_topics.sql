BEGIN;

INSERT INTO topics (topic, created_at) VALUES
  ('Academic Difficulty', now()),
  ('Academic Interests', now()),
  ('Academic Plan', now()),
  ('Academic Support', now()),
  ('Career/Internship', now()),
  ('Change Grading Option', now()),
  ('Change of Major', now()),
  ('Course Selection', now()),
  ('Currently Dismissed/Planning', now()),
  ('Educational Goals', now()),
  ('Eligibility', now()),
  ('Enrolling At Another School', now()),
  ('Evaluation of course(s) taken elsewhere', now()),
  ('Graduation Check', now()),
  ('Graduation Plan', now()),
  ('Graduation Progress', now()),
  ('Joint Major', now()),
  ('Other', now()),
  ('Personal', now()),
  ('Petition', now()),
  ('Proctoring', now()),
  ('Requirements', now()),
  ('Research', now()),
  ('Scheduling', now()),
  ('Transition Support', now()),
  ('Travel Conflicts', now());

COMMIT;
