BEGIN;

CREATE TYPE university_dept_member_role_type AS ENUM('advisor', 'director', 'scheduler');

ALTER TABLE university_dept_members ADD COLUMN role university_dept_member_role_type;

UPDATE university_dept_members SET role = CASE 
  WHEN is_director = TRUE THEN 'director'::university_dept_member_role_type
  WHEN is_advisor = TRUE THEN 'advisor'::university_dept_member_role_type
  WHEN is_scheduler = TRUE THEN 'scheduler'::university_dept_member_role_type
  ELSE NULL
END;

ALTER TABLE university_dept_members
  DROP COLUMN is_advisor,
  DROP COLUMN is_director,
  DROP COLUMN is_scheduler;

COMMIT;