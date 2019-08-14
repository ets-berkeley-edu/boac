BEGIN;

CREATE TABLE note_templates (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body text NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX note_templates_creator_id_idx ON note_templates USING btree (creator_id);

ALTER TABLE ONLY note_templates
    ADD CONSTRAINT note_templates_creator_id_title_unique_constraint UNIQUE (creator_id, title);

ALTER TABLE ONLY note_templates
    ADD CONSTRAINT note_templates_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

--

CREATE TABLE note_template_attachments (
    id SERIAL PRIMARY KEY,
    note_template_id INTEGER NOT NULL,
    path_to_attachment character varying(255) NOT NULL,
    uploaded_by_uid character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);

-- Constraint name length is limited to 63 bytes in Postgres so we abbreviate the prefix.
ALTER TABLE ONLY note_template_attachments
    ADD CONSTRAINT nta_note_template_id_path_to_attachment_unique_constraint UNIQUE (note_template_id, path_to_attachment);

CREATE INDEX note_template_attachments_note_template_id_idx ON note_template_attachments USING btree (note_template_id);

ALTER TABLE ONLY note_template_attachments
    ADD CONSTRAINT note_template_attachments_note_template_id_fkey FOREIGN KEY (note_template_id) REFERENCES note_templates(id) ON DELETE CASCADE;

--

CREATE TABLE note_template_topics (
    id SERIAL PRIMARY KEY,
    note_template_id INTEGER NOT NULL,
    topic VARCHAR(50) NOT NULL
);

ALTER TABLE ONLY note_template_topics
    ADD CONSTRAINT note_template_topics_note_template_id_topic_unique_constraint UNIQUE (note_template_id, topic);

CREATE INDEX note_template_topics_note_template_id_idx ON note_template_topics (note_template_id);

ALTER TABLE ONLY note_template_topics
    ADD CONSTRAINT note_template_topics_note_template_id_fkey FOREIGN KEY (note_template_id) REFERENCES note_templates(id) ON DELETE CASCADE;

-- Done

COMMIT;
