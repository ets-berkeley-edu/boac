BEGIN;

-- Groups have a name and an owner

CREATE TABLE student_groups (
  id SERIAL PRIMARY KEY,
  owner_id INTEGER NOT NULL REFERENCES authorized_users (id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX student_groups_owner_id_idx ON student_groups (owner_id);

ALTER TABLE student_groups ADD CONSTRAINT student_groups_owner_id_name_unique_constraint UNIQUE (owner_id, name);

-- Create linking table

CREATE TABLE student_group_members (
  student_group_id INTEGER NOT NULL REFERENCES student_groups (id) ON DELETE CASCADE,
  sid VARCHAR(80) NOT NULL REFERENCES students (sid) ON DELETE CASCADE,

  PRIMARY KEY (student_group_id, sid)
);

-- Export legacy data prior to step 02

\copy advisor_watchlists TO '/tmp/advisor_watchlists.csv' DELIMITER ',' CSV HEADER;

-- Done

COMMIT;
