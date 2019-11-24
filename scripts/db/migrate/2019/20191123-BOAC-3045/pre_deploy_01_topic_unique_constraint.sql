BEGIN;

ALTER TABLE IF EXISTS ONLY public.appointment_topics
    DROP CONSTRAINT IF EXISTS appointment_topics_appointment_id_topic_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.note_topics
    DROP CONSTRAINT IF EXISTS note_topics_note_id_topic_unique_constraint;

ALTER TABLE ONLY appointment_topics
    ADD CONSTRAINT appointment_topics_appointment_id_topic_unique_constraint UNIQUE (appointment_id, topic, deleted_at);
ALTER TABLE ONLY note_topics
    ADD CONSTRAINT note_topics_note_id_topic_unique_constraint UNIQUE (note_id, topic, deleted_at);

COMMIT;
