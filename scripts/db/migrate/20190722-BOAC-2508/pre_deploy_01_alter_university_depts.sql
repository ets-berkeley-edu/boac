BEGIN;

ALTER TABLE university_depts ADD COLUMN automate_memberships BOOLEAN DEFAULT false NOT NULL;

UPDATE university_depts SET automate_memberships = true WHERE dept_code = 'COENG';
UPDATE university_depts SET automate_memberships = true WHERE dept_code = 'QCADV';

INSERT INTO university_depts
(dept_code, dept_name, created_at, updated_at, automate_memberships)
VALUES
('BAHSB', 'Haas School of Business', now(), now(), true),
('CDCDN', 'College of Chemistry', now(), now(), true),
('DACED', 'College of Environmental Design', now(), now(), true),
('MANRD', 'College of Natural Resources', now(), now(), true),
('QCADVMAJ', 'Letters & Science Major Advisors', now(), now(), true),
('ZZZZZ', 'Other', now(), now(), true);

COMMIT;
