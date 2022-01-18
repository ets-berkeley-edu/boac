BEGIN;

ALTER TABLE authorized_users
ADD COLUMN IF NOT EXISTS automate_degree_progress_permission BOOLEAN DEFAULT FALSE;

UPDATE authorized_users u SET automate_degree_progress_permission = TRUE
WHERE u.id IN (
  SELECT DISTINCT u.id FROM authorized_users u
  JOIN university_dept_members m ON m.authorized_user_id = u.id
  JOIN university_depts d ON d.id = m.university_dept_id
  WHERE d.dept_code = 'COENG'
);

-- Column is not nullable.
ALTER TABLE ONLY authorized_users ALTER COLUMN automate_degree_progress_permission SET NOT NULL;

-- Empty cache
DELETE FROM json_cache WHERE key LIKE 'boa_user_session_%';

COMMIT;
