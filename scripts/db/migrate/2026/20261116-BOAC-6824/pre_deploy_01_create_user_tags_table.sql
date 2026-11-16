BEGIN;

CREATE TYPE user_tag_object_types AS ENUM ('note', 'comment');
ALTER TYPE user_tag_object_types OWNER TO app_boa;

-- One row per user tagged in a note or comment. The tagged text itself stays in notes or comments.
CREATE TABLE user_tags (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    object_id INTEGER NOT NULL,
    object_type user_tag_object_types NOT NULL,
    email_notification_sent BOOLEAN DEFAULT FALSE NOT NULL,
    read_by_user BOOLEAN DEFAULT FALSE NOT NULL,
    archived_by_user BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    -- object_id points at notes or comments depending on object_type, and Postgres can't declare a foreign key
    -- to two tables. These generated columns split object_id by type so that each can carry its own real foreign key.
    note_id INTEGER GENERATED ALWAYS AS (CASE WHEN object_type = 'note' THEN object_id END) STORED,
    comment_id INTEGER GENERATED ALWAYS AS (CASE WHEN object_type = 'comment' THEN object_id END) STORED
);
ALTER TABLE user_tags OWNER TO app_boa;
CREATE SEQUENCE user_tags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE user_tags_id_seq OWNER TO app_boa;
ALTER SEQUENCE user_tags_id_seq OWNED BY user_tags.id;
ALTER TABLE ONLY user_tags ALTER COLUMN id SET DEFAULT nextval('user_tags_id_seq'::regclass);
ALTER TABLE ONLY user_tags
    ADD CONSTRAINT user_tags_pkey PRIMARY KEY (id);
ALTER TABLE ONLY user_tags
    ADD CONSTRAINT user_tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY user_tags
    ADD CONSTRAINT user_tags_note_id_fkey FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE;
ALTER TABLE ONLY user_tags
    ADD CONSTRAINT user_tags_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE;
CREATE INDEX user_tags_user_id_idx ON user_tags USING btree (user_id);
CREATE INDEX user_tags_object_id_idx ON user_tags USING btree (object_id);
-- A user is tagged at most once per note or comment; a soft-deleted tag doesn't block tagging them again.
CREATE UNIQUE INDEX user_tags_user_id_object_type_object_id_idx
    ON user_tags (user_id, object_type, object_id)
    WHERE deleted_at IS NULL;

COMMIT;
