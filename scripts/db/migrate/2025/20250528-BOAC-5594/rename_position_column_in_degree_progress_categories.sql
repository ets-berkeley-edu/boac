BEGIN;

ALTER TABLE degree_progress_categories RENAME COLUMN position TO ux_position_x;
ALTER TABLE degree_progress_categories ADD COLUMN IF NOT EXISTS ux_position_y INTEGER;

-- Existing (sub)categories are assigned order per order of creation, which is reflected in the primary-key (id).
UPDATE degree_progress_categories SET ux_position_y = id;

-- Next, add 'NOT NULL' constraint.
ALTER TABLE ONLY degree_progress_categories ALTER COLUMN ux_position_y SET NOT NULL;

COMMIT;
