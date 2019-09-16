BEGIN;

UPDATE university_dept_members udm
SET automate_membership = ud.automate_memberships
FROM university_depts ud
WHERE udm.university_dept_id = ud.id
AND ud.automate_memberships IS FALSE;

ALTER TABLE university_depts DROP COLUMN automate_memberships;

COMMIT;
