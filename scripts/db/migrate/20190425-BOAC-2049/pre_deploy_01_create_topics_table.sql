BEGIN;

CREATE TABLE topics (
  id SERIAL PRIMARY KEY,
  topic VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE topics ADD CONSTRAINT topics_topic_unique_constraint UNIQUE (topic);

INSERT INTO topics (topic, created_at) VALUES 
  ('Academic Progress', now()),
  ('Academic Progress Report (APR)', now()),
  ('Change of College', now()),
  ('Concurrent Enrollment', now()),
  ('Continued After Dismissal', now()),
  ('Course Add', now()),
  ('Course Drop', now()),
  ('Course Grade Option', now()),
  ('Course Unit Change', now()),
  ('Dean Appointment', now()),
  ('Degree Check', now()),
  ('Degree Check Preparation', now()),
  ('Degree Requirements', now()),
  ('Dismissal', now()),
  ('Double Major', now()),
  ('Education Abroad Program (EAP)', now()),
  ('Education Abroad Program (EAP) Reciprocity', now()),
  ('Excess Units', now()),
  ('Incompletes', now()),
  ('Late Enrollment', now()),
  ('Majors', now()),
  ('Minimum Unit Program', now()),
  ('Pass / Not Pass (PNP)', now()),
  ('Pre-Med Advising', now()),
  ('Probation', now()),
  ('Program Planning', now()),
  ('Reading & Composition', now()),
  ('Readmission', now()),
  ('Refer to Academic Department', now()),
  ('Refer to Career Center', now()),
  ('Refer to Resources', now()),
  ('Refer to The Tang Center', now()),
  ('Retroactive Addition', now()),
  ('Retroactive Drop', now()),
  ('Retroactive Grading Option', now()),
  ('Retroactive Unit Change', now()),
  ('Retroactive Withdrawal', now()),
  ('Satisfactory Academic Progress (SAP) Appeal', now()),
  ('Semester Out Rule', now()),
  ('Senior Residency', now()),
  ('Simultaneous Degree', now()),
  ('Special Studies', now()),
  ('Student Conduct', now()),
  ('Study Abroad', now()),
  ('Transfer Coursework', now()),
  ('Waive College Requirement', now()),
  ('Withdrawal', now());

COMMIT;
