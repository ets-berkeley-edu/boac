BEGIN;

CREATE MATERIALIZED VIEW notes_fts_index AS (
  SELECT id, to_tsvector('english', subject || ' ' || body) AS fts_index
  FROM notes
  WHERE deleted_at IS NULL
);

CREATE INDEX idx_notes_fts_index
ON notes_fts_index
USING gin(fts_index);

COMMIT;
