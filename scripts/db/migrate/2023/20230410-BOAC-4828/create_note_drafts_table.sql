BEGIN;

CREATE TABLE note_drafts (
    id SERIAL PRIMARY KEY,
    body text NOT NULL,
    creator_id INTEGER NOT NULL,
    sids VARCHAR(80)[] NOT NULL,
    subject VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX note_drafts_creator_id_idx ON note_drafts USING btree (creator_id);

ALTER TABLE ONLY note_drafts
    ADD CONSTRAINT note_drafts_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

CREATE TABLE note_draft_attachments (
    id SERIAL PRIMARY KEY,
    note_draft_id INTEGER NOT NULL,
    path_to_attachment character varying(255) NOT NULL,
    uploaded_by_uid character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);

-- Constraint name length is limited to 63 bytes in Postgres so we abbreviate the prefix.
ALTER TABLE ONLY note_draft_attachments
    ADD CONSTRAINT nta_note_draft_id_path_to_attachment_unique_constraint UNIQUE (note_draft_id, path_to_attachment);

CREATE INDEX note_draft_attachments_note_draft_id_idx ON note_draft_attachments USING btree (note_draft_id);

ALTER TABLE ONLY note_draft_attachments
    ADD CONSTRAINT note_draft_attachments_note_draft_id_fkey FOREIGN KEY (note_draft_id) REFERENCES note_drafts(id) ON DELETE CASCADE;

--

CREATE TABLE note_draft_topics (
    id SERIAL PRIMARY KEY,
    note_draft_id INTEGER NOT NULL,
    topic VARCHAR(50) NOT NULL
);

ALTER TABLE ONLY note_draft_topics
    ADD CONSTRAINT note_draft_topics_note_draft_id_topic_unique_constraint UNIQUE (note_draft_id, topic);

CREATE INDEX note_draft_topics_note_draft_id_idx ON note_draft_topics (note_draft_id);

ALTER TABLE ONLY note_draft_topics
    ADD CONSTRAINT note_draft_topics_note_draft_id_fkey FOREIGN KEY (note_draft_id) REFERENCES note_drafts(id) ON DELETE CASCADE;

-- Done

COMMIT;
