BEGIN;

DROP INDEX idx_notes_fts_index;
DROP MATERIALIZED VIEW notes_fts_index;

CREATE MATERIALIZED VIEW notes_fts_index AS (
  SELECT
    id,
    CASE WHEN (body IS NULL OR is_private) THEN to_tsvector('english', subject)
         ELSE to_tsvector('english', subject || ' ' || body)
         END AS fts_index
  FROM notes
  WHERE deleted_at IS NULL AND is_draft_for_sids IS NULL
);

CREATE INDEX idx_notes_fts_index ON notes_fts_index USING gin(fts_index);

COMMIT;
