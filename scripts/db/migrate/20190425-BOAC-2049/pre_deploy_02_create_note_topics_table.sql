BEGIN;

DROP INDEX IF EXISTS note_topics_topic_idx;
DROP INDEX IF EXISTS note_topics_note_id_idx;
DROP TABLE IF EXISTS note_topics;

CREATE TABLE note_topics (
  id SERIAL NOT NULL,
  note_id INTEGER NOT NULL REFERENCES notes (id) ON DELETE CASCADE,
  topic VARCHAR(255) NOT NULL,
  author_uid VARCHAR(255) NOT NULL REFERENCES authorized_users(uid) ON DELETE CASCADE,

  PRIMARY KEY (id)
);

ALTER TABLE note_topics
    ADD CONSTRAINT note_topics_note_id_topic_unique_constraint
        UNIQUE (note_id, topic);

CREATE INDEX note_topics_note_id_idx ON note_topics (note_id);

CREATE INDEX note_topics_topic_idx ON note_topics (topic);

COMMIT;
