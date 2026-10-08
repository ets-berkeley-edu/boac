BEGIN;

DROP INDEX idx_notes_fts_index;
DROP INDEX IF EXISTS idx_notes_fts_index_id_idx;
DROP MATERIALIZED VIEW notes_fts_index;

DROP INDEX idx_advisor_author_index;
DROP INDEX IF EXISTS idx_advisor_author_name_uid_idx;
DROP MATERIALIZED VIEW advisor_author_index;

COMMIT;
