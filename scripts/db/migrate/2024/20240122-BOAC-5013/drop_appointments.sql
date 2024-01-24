BEGIN;

DELETE FROM topics WHERE available_in_notes = FALSE;
ALTER TABLE IF EXISTS ONLY topics DROP COLUMN available_in_appointments, DROP COLUMN available_in_notes;

DROP INDEX IF EXISTS idx_advisor_author_index;
DROP MATERIALIZED VIEW IF EXISTS advisor_author_index;

CREATE MATERIALIZED VIEW advisor_author_index AS (
  SELECT DISTINCT author_name AS advisor_name, author_uid AS advisor_uid
  FROM notes
  ORDER BY advisor_name
);

CREATE INDEX idx_advisor_author_index ON advisor_author_index USING btree(advisor_name);

ALTER TABLE IF EXISTS ONLY appointments DROP CONSTRAINT IF EXISTS appointments_created_by_fkey;
ALTER TABLE IF EXISTS ONLY appointments DROP CONSTRAINT IF EXISTS appointments_deleted_by_fkey;
ALTER TABLE IF EXISTS ONLY appointments DROP CONSTRAINT IF EXISTS appointments_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY appointment_availability DROP CONSTRAINT IF EXISTS appointment_availability_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY appointment_events DROP CONSTRAINT IF EXISTS appointment_events_advisor_id_fkey;
ALTER TABLE IF EXISTS ONLY appointment_events DROP CONSTRAINT IF EXISTS appointment_events_appointment_id_fkey;
ALTER TABLE IF EXISTS ONLY appointment_events DROP CONSTRAINT IF EXISTS appointment_events_user_id_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY appointment_topics DROP CONSTRAINT IF EXISTS appointment_topics_appointment_id_fkey;
ALTER TABLE IF EXISTS ONLY appointment_topics DROP CONSTRAINT IF EXISTS appointment_topics_appointment_id_topic_unique_constraint;
ALTER TABLE IF EXISTS ONLY drop_in_advisors DROP CONSTRAINT IF EXISTS drop_in_advisors_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY drop_in_advisors DROP CONSTRAINT IF EXISTS drop_in_advisors_dept_code_fkey;
ALTER TABLE IF EXISTS ONLY same_day_advisors DROP CONSTRAINT IF EXISTS same_day_advisors_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY schedulers DROP CONSTRAINT IF EXISTS schedulers_authorized_user_id_fkey;

DROP INDEX IF EXISTS idx_appointments_fts_index;
DROP INDEX IF EXISTS appointment_availability_authorized_user_id_dept_code_idx;
DROP INDEX IF EXISTS appointment_availability_weekday_idx;
DROP INDEX IF EXISTS appointment_availability_date_override_idx;
DROP INDEX IF EXISTS appointment_events_appointment_id_idx;
DROP INDEX IF EXISTS appointment_events_user_id_idx;
DROP INDEX IF EXISTS appointment_topics_appointment_id_idx;
DROP INDEX IF EXISTS appointment_topics_topic_idx;
DROP INDEX IF EXISTS appointments_created_by_idx;
DROP INDEX IF EXISTS appointments_advisor_uid_idx;
DROP INDEX IF EXISTS appointments_scheduled_time_idx;
DROP INDEX IF EXISTS appointments_student_sid_idx;

ALTER TABLE IF EXISTS ONLY appointment_availability DROP CONSTRAINT IF EXISTS appointment_availability_pkey;
ALTER TABLE IF EXISTS ONLY appointment_topics DROP CONSTRAINT IF EXISTS appointment_topics_pkey;
ALTER TABLE IF EXISTS ONLY appointments DROP CONSTRAINT IF EXISTS appointments_pkey;
ALTER TABLE IF EXISTS ONLY drop_in_advisors DROP CONSTRAINT IF EXISTS drop_in_advisors_pkey;
ALTER TABLE IF EXISTS ONLY same_day_advisors DROP CONSTRAINT IF EXISTS same_day_advisors_pkey;

DROP MATERIALIZED VIEW IF EXISTS appointments_fts_index;
DROP TABLE IF EXISTS appointment_availability;
DROP SEQUENCE IF EXISTS appointment_availability_id_seq;
DROP TABLE IF EXISTS appointment_events;
DROP SEQUENCE IF EXISTS appointment_events_id_seq;
DROP TABLE IF EXISTS appointment_topics;
DROP SEQUENCE IF EXISTS appointment_topics_id_seq;
DROP TABLE IF EXISTS appointments;
DROP SEQUENCE IF EXISTS appointments_id_seq;
DROP TABLE IF EXISTS drop_in_advisors;
DROP TABLE IF EXISTS same_day_advisors;
DROP TABLE IF EXISTS schedulers;

DROP TYPE IF EXISTS appointment_event_types;
DROP TYPE IF EXISTS appointment_student_contact_types;
DROP TYPE IF EXISTS appointment_types;
DROP TYPE IF EXISTS drop_in_advisor_status_types;
DROP TYPE IF EXISTS weekday_types;

COMMIT;
