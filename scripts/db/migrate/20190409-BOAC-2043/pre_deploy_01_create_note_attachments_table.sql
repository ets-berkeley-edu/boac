BEGIN;

CREATE TABLE note_attachments (
    note_id INTEGER NOT NULL,
    path_to_attachment character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);

ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_pkey PRIMARY KEY (note_id, path_to_attachment);

CREATE INDEX note_attachments_note_id_idx ON note_attachments USING btree (note_id);

ALTER TABLE ONLY note_attachments
    ADD CONSTRAINT note_attachments_note_id_fkey FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE;

-- Done

COMMIT;
