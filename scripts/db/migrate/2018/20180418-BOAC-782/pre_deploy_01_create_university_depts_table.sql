BEGIN;

-- College of Engineering advisors are mapped to dept_code COENG and ASC advisors to UWASC.

CREATE TABLE university_depts (
  id SERIAL PRIMARY KEY,
  dept_code character varying(80) NOT NULL UNIQUE,
  dept_name character varying(255) NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE university_depts ADD CONSTRAINT university_depts_code_unique_constraint UNIQUE (dept_code, dept_name);

-- An authorized_user can belong to zero or more departments

CREATE TABLE university_dept_members (
  university_dept_id INTEGER NOT NULL REFERENCES university_depts (id) ON DELETE CASCADE,
  authorized_user_id INTEGER NOT NULL REFERENCES authorized_users (id) ON DELETE CASCADE,
  is_advisor BOOLEAN DEFAULT false NOT NULL,
  is_director BOOLEAN DEFAULT false NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (university_dept_id, authorized_user_id)
);

-- Done

COMMIT;
