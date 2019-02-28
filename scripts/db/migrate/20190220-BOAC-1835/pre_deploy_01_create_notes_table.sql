BEGIN;

CREATE TABLE notes (
  id SERIAL PRIMARY KEY,
  author_uid VARCHAR(255) NOT NULL,
  author_name VARCHAR(255) NOT NULL,
  author_role VARCHAR(255) NOT NULL,
  author_dept_codes VARCHAR[] NOT NULL,
  sid VARCHAR(80) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  body text NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX notes_author_uid_idx ON notes USING btree (author_uid);

-- Done

COMMIT;
