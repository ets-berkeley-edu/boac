BEGIN;

ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_note_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_note_id_path_to_attachment_unique_constraint;
DROP INDEX IF EXISTS public.note_attachments_note_id_idx;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_pkey;
DROP TABLE IF EXISTS public.note_attachments;
DROP SEQUENCE IF EXISTS public.note_attachments_id_seq;

CREATE TABLE note_attachments (
    id SERIAL NOT NULL,
    note_id INTEGER NOT NULL,
    path_to_attachment character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);

ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_pkey PRIMARY KEY (id);

ALTER TABLE note_attachments
    ADD CONSTRAINT note_attachments_note_id_path_to_attachment_unique_constraint
        UNIQUE (note_id, path_to_attachment);

CREATE INDEX note_attachments_note_id_idx ON note_attachments USING btree (note_id);

ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_note_id_fkey FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE;

-- Done

COMMIT;
