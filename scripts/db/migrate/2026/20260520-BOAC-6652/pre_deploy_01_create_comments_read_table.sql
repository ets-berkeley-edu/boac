BEGIN;

CREATE TABLE comments_read (
    comment_id INTEGER NOT NULL,
    viewer_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE comments_read OWNER TO app_boa;

ALTER TABLE ONLY comments_read
    ADD CONSTRAINT comments_read_pkey PRIMARY KEY (viewer_id, comment_id);

CREATE INDEX comments_read_comment_id_idx ON comments_read USING btree (comment_id);
CREATE INDEX comments_read_viewer_id_idx ON comments_read USING btree (viewer_id);

ALTER TABLE ONLY comments_read
    ADD CONSTRAINT comments_read_comment_id_fkey
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE;

ALTER TABLE ONLY comments_read
    ADD CONSTRAINT comments_read_viewer_id_fkey
    FOREIGN KEY (viewer_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;
