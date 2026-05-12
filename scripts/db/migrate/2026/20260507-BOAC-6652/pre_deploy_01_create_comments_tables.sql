BEGIN;

CREATE TYPE comment_parent_types AS ENUM (
    'appointment',
    'course_load_eform',
    'cpp_change_eform',
    'late_drop_eform'
);
ALTER TYPE comment_parent_types OWNER TO app_boa;

CREATE TABLE comment_parents (
    id INTEGER NOT NULL,
    parent_id VARCHAR(255) NOT NULL,
    parent_type comment_parent_types NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE comment_parents OWNER TO app_boa;
CREATE SEQUENCE comment_parents_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE comment_parents_id_seq OWNER TO app_boa;
ALTER SEQUENCE comment_parents_id_seq OWNED BY comment_parents.id;
ALTER TABLE ONLY comment_parents ALTER COLUMN id SET DEFAULT nextval('comment_parents_id_seq'::regclass);
ALTER TABLE ONLY comment_parents
    ADD CONSTRAINT comment_parents_pkey PRIMARY KEY (id);
CREATE UNIQUE INDEX comment_parents_parent_id_parent_type_idx
    ON comment_parents (parent_id, parent_type)
    WHERE deleted_at IS NULL;

CREATE TABLE comments (
    id INTEGER NOT NULL,
    comment_parent_id INTEGER NOT NULL,
    author_uid VARCHAR(255) NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    author_role VARCHAR(255) NOT NULL,
    author_dept_codes VARCHAR[] NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE comments OWNER TO app_boa;
CREATE SEQUENCE comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE comments_id_seq OWNER TO app_boa;
ALTER SEQUENCE comments_id_seq OWNED BY comments.id;
ALTER TABLE ONLY comments ALTER COLUMN id SET DEFAULT nextval('comments_id_seq'::regclass);
ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);
CREATE INDEX comments_comment_parent_id_idx ON comments USING btree (comment_parent_id);
CREATE INDEX comments_author_uid_idx ON comments USING btree (author_uid);
CREATE INDEX comments_deleted_at_idx ON comments (deleted_at);

CREATE TABLE comment_attachments (
    id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    path_to_attachment VARCHAR(255) NOT NULL,
    uploaded_by_uid VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE comment_attachments OWNER TO app_boa;
CREATE SEQUENCE comment_attachments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE comment_attachments_id_seq OWNER TO app_boa;
ALTER SEQUENCE comment_attachments_id_seq OWNED BY comment_attachments.id;
ALTER TABLE ONLY comment_attachments ALTER COLUMN id SET DEFAULT nextval('comment_attachments_id_seq'::regclass);
ALTER TABLE ONLY comment_attachments
    ADD CONSTRAINT comment_attachments_pkey PRIMARY KEY (id);
ALTER TABLE ONLY comment_attachments
    ADD CONSTRAINT comment_attachments_comment_id_path_to_attachment_unique_constraint
    UNIQUE (comment_id, path_to_attachment, deleted_at);
CREATE INDEX comment_attachments_comment_id_idx ON comment_attachments USING btree (comment_id);

ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_comment_parent_id_fkey
    FOREIGN KEY (comment_parent_id) REFERENCES comment_parents(id) ON DELETE CASCADE;
ALTER TABLE ONLY comment_attachments
    ADD CONSTRAINT comment_attachments_comment_id_fkey
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE;

COMMIT;
