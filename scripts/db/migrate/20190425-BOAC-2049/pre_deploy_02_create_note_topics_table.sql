BEGIN;

CREATE TABLE note_topics (
  note_id INTEGER NOT NULL REFERENCES notes (id) ON DELETE CASCADE,
  topic VARCHAR(255) NOT NULL,
  author_uid VARCHAR(255) NOT NULL REFERENCES authorized_users(uid) ON DELETE CASCADE,

  PRIMARY KEY (note_id, topic)
);

CREATE INDEX note_topics_note_id_idx ON note_topics (note_id);

CREATE INDEX note_topics_topic_idx ON note_topics (topic);

COMMIT;
