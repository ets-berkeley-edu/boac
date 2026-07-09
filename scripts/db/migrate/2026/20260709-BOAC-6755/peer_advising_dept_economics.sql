BEGIN;

DELETE FROM peer_advising_departments WHERE name = 'Economics';

INSERT INTO peer_advising_departments (name, university_dept_id, created_at, updated_at)
    SELECT 'Economics', d.id, now(), now()
    FROM university_depts d
    WHERE d.dept_code = 'QCADVMAJ';

COMMIT;
