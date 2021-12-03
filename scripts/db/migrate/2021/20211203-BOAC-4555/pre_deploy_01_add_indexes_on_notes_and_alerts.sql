BEGIN;

CREATE INDEX alerts_deleted_at_idx ON alerts (deleted_at);
CREATE INDEX alert_views_dismissed_at_idx ON alert_views (dismissed_at);
CREATE INDEX notes_deleted_at_idx ON notes (deleted_at);
CREATE INDEX notes_is_private_idx ON notes (is_private);

DROP INDEX IF EXISTS alert_views_alert_id_idx;

COMMIT;