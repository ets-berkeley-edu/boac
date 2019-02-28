BEGIN;

DROP INDEX IF EXISTS public.notes_author_id_idx;
DROP TABLE IF EXISTS notes;

COMMIT;
