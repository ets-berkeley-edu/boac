BEGIN;

ALTER TABLE authorized_users ADD COLUMN can_access_canvas_data boolean DEFAULT true NOT NULL;

COMMIT;
