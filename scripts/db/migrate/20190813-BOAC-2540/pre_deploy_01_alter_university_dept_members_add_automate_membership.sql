BEGIN;

ALTER TABLE university_dept_members ADD COLUMN automate_membership boolean DEFAULT true NOT NULL;

COMMIT;
