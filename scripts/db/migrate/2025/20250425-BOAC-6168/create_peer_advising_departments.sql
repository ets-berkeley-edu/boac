BEGIN;

-- Centers for Educational Equity and Excellence (ZCEEE)
INSERT INTO peer_advising_departments
  (name, university_dept_id, created_at, updated_at)
VALUES
 ('Educational Opportunity Program', 12, now(), now()),
 ('NAVCAL', 12, now(), now()),
 ('Transfer Student Center', 12, now(), now());

-- College of Engineering (COENG)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('College of Engineering', 2, now(), now());

-- College of Natural Resources (MANRD)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('Office of Instruction & Student Affairs', 8, now(), now());

-- L&S College Advising (QCADV)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('L&S College Advising', 4, now(), now());

-- L&S Major Advisors (QCADVMAJ)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('Psychology', 9, now(), now()),
('Global Poverty & Practice Minor', 9, now(), now());

-- Athletic Study Center (UWASC)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('Athletic Study Center', 1, now(), now());

-- School of Public Health (KTPUB)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('School of Public Health', 14, now(), now());

-- College of Computing, Data Science, and Society (DSDDO)
INSERT INTO peer_advising_departments
 (name, university_dept_id, created_at, updated_at)
VALUES
('College of Computing, Data Science, and Society', 13, now(), now());

COMMIT;
