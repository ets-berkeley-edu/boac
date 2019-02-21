BEGIN;

CREATE TABLE notes (
  id SERIAL PRIMARY KEY,
  author_id INTEGER NOT NULL REFERENCES authorized_users (id) ON DELETE CASCADE,
  sid VARCHAR(80) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  body text NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX notes_author_id_idx ON notes USING btree (author_id);

-- Done

COMMIT;
