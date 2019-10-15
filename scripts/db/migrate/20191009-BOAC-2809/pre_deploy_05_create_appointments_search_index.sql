BEGIN;

CREATE MATERIALIZED VIEW appointments_fts_index AS (
  SELECT 
    id, to_tsvector('english', details) AS fts_index
  FROM appointments
  WHERE details IS NOT NULL
    AND deleted_at IS NULL
);

CREATE INDEX idx_appointments_fts_index
ON appointments_fts_index
USING gin(fts_index);

COMMIT;
