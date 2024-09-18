BEGIN;

ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_note_id_path_to_attachment_unique_constraint;

ALTER TABLE note_attachments
    ADD CONSTRAINT note_attachments_note_id_path_to_attachment_unique_constraint
        UNIQUE (note_id, path_to_attachment, deleted_at);

COMMIT;
