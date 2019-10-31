BEGIN;

UPDATE note_topics SET topic = SUBSTRING(topic, 0, 50);
ALTER TABLE note_topics ALTER COLUMN topic TYPE VARCHAR(50);

UPDATE topics SET topic = SUBSTRING(topic, 0, 50);
ALTER TABLE topics ALTER COLUMN topic TYPE VARCHAR(50);

COMMIT;
