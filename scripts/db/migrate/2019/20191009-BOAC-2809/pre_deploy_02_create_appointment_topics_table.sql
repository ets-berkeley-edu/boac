BEGIN;

DROP TABLE IF EXISTS appointment_topics;

CREATE TABLE appointment_topics (
  id SERIAL NOT NULL,
  appointment_id INTEGER NOT NULL,
  topic VARCHAR(255) NOT NULL,
  deleted_at timestamp with time zone,

  PRIMARY KEY (id)
);

ALTER TABLE appointment_topics
    ADD CONSTRAINT appointment_topics_appointment_id_topic_unique_constraint
        UNIQUE (appointment_id, topic);

CREATE INDEX appointment_topics_appointment_id_idx ON appointment_topics (appointment_id);
CREATE INDEX appointment_topics_topic_idx ON appointment_topics (topic);

COMMIT;
