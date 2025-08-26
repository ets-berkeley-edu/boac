BEGIN;

CREATE UNIQUE INDEX idx_notes_fts_index_id_idx ON notes_fts_index(id);
CREATE UNIQUE INDEX idx_advisor_author_name_uid_idx ON advisor_author_index(advisor_name, advisor_uid);

COMMIT;
