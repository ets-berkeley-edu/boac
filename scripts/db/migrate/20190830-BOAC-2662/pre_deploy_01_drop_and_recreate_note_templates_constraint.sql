BEGIN;

ALTER TABLE IF EXISTS ONLY public.note_templates
    DROP CONSTRAINT IF EXISTS note_templates_creator_id_title_unique_constraint;

ALTER TABLE ONLY note_templates
    ADD CONSTRAINT note_templates_creator_id_title_unique_constraint UNIQUE (creator_id, title, deleted_at);

-- Done

COMMIT;
