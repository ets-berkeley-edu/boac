/**
 * Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--

ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_alert_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_viewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.appointments DROP CONSTRAINT IF EXISTS appointments_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.appointments DROP CONSTRAINT IF EXISTS appointments_deleted_by_fkey;
ALTER TABLE IF EXISTS ONLY public.appointments DROP CONSTRAINT IF EXISTS appointments_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.appointment_availability DROP CONSTRAINT IF EXISTS appointment_availability_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.appointment_events DROP CONSTRAINT IF EXISTS appointment_events_advisor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.appointment_events DROP CONSTRAINT IF EXISTS appointment_events_appointment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.appointment_events DROP CONSTRAINT IF EXISTS appointment_events_user_id_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.appointment_topics DROP CONSTRAINT IF EXISTS appointment_topics_appointment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.appointment_topics DROP CONSTRAINT IF EXISTS appointment_topics_appointment_id_topic_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.appointments_read DROP CONSTRAINT IF EXISTS appointments_read_viewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filters DROP CONSTRAINT IF EXISTS cohort_filters_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_events DROP CONSTRAINT IF EXISTS cohort_filter_events_cohort_filter_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_cohort_filter_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_categories DROP CONSTRAINT IF EXISTS degree_progress_categories_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_categories DROP CONSTRAINT IF EXISTS degree_progress_categories_parent_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_category_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_category_unit_reqts_unit_requirement_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_category_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_category_unit_reqts_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_course_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_course_unit_reqts_unit_requirement_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_course_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_course_unit_reqts_course_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_courses DROP CONSTRAINT IF EXISTS degree_progress_courses_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_courses DROP CONSTRAINT IF EXISTS degree_progress_courses_degree_check_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_templates DROP CONSTRAINT IF EXISTS degree_progress_templates_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_templates DROP CONSTRAINT IF EXISTS degree_progress_templates_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_templates DROP CONSTRAINT IF EXISTS degree_progress_templates_parent_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_unit_requirements_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_unit_requirements_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_unit_requirements_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_unit_requirements_name_template_id_unique_const;
ALTER TABLE IF EXISTS ONLY public.degree_progress_notes DROP CONSTRAINT IF EXISTS degree_progress_notes_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_notes DROP CONSTRAINT IF EXISTS degree_progress_notes_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.drop_in_advisors DROP CONSTRAINT IF EXISTS drop_in_advisors_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.drop_in_advisors DROP CONSTRAINT IF EXISTS drop_in_advisors_dept_code_fkey;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_note_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_note_id_path_to_attachment_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.note_template_attachments DROP CONSTRAINT IF EXISTS note_template_attachments_note_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_template_topics DROP CONSTRAINT IF EXISTS note_template_topics_note_template_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_templates DROP CONSTRAINT IF EXISTS note_templates_creator_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_topics DROP CONSTRAINT IF EXISTS note_topics_author_uid_fkey;
ALTER TABLE IF EXISTS ONLY public.note_topics DROP CONSTRAINT IF EXISTS note_topics_note_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_topics DROP CONSTRAINT IF EXISTS note_topics_note_id_topic_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.notes DROP CONSTRAINT IF EXISTS notes_author_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notes_read DROP CONSTRAINT IF EXISTS notes_read_viewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.same_day_advisors DROP CONSTRAINT IF EXISTS same_day_advisors_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedulers DROP CONSTRAINT IF EXISTS schedulers_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_student_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_groups DROP CONSTRAINT IF EXISTS student_groups_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_groups DROP CONSTRAINT IF EXISTS student_groups_owner_id_name_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.university_dept_members DROP CONSTRAINT IF EXISTS university_dept_members_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.university_dept_members DROP CONSTRAINT IF EXISTS university_dept_members_university_dept_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_logins DROP CONSTRAINT IF EXISTS user_logins_uid_fkey;

--

DROP INDEX IF EXISTS public.idx_appointments_fts_index;
DROP INDEX IF EXISTS public.appointment_availability_authorized_user_id_dept_code_idx;
DROP INDEX IF EXISTS public.appointment_availability_weekday_idx;
DROP INDEX IF EXISTS public.appointment_availability_date_override_idx;
DROP INDEX IF EXISTS public.appointment_events_appointment_id_idx;
DROP INDEX IF EXISTS public.appointment_events_user_id_idx;
DROP INDEX IF EXISTS public.appointment_topics_appointment_id_idx;
DROP INDEX IF EXISTS public.appointment_topics_topic_idx;
DROP INDEX IF EXISTS public.appointments_created_by_idx;
DROP INDEX IF EXISTS public.appointments_advisor_uid_idx;
DROP INDEX IF EXISTS public.appointments_student_sid_idx;
DROP INDEX IF EXISTS public.appointments_read_appointment_id_idx;
DROP INDEX IF EXISTS public.appointments_read_viewer_id_idx;
DROP INDEX IF EXISTS public.alert_views_alert_id_idx;
DROP INDEX IF EXISTS public.alert_views_viewer_id_idx;
DROP INDEX IF EXISTS public.alerts_sid_idx;
DROP INDEX IF EXISTS public.cohort_filters_owner_id_idx;
DROP INDEX IF EXISTS public.cohort_filter_events_cohort_filter_id_idx;
DROP INDEX IF EXISTS public.cohort_filter_events_sid_idx;
DROP INDEX IF EXISTS public.cohort_filter_events_event_type_idx;
DROP INDEX IF EXISTS public.cohort_filter_events_created_at_idx;
DROP INDEX IF EXISTS public.degree_progress_categories_id_idx;
DROP INDEX IF EXISTS public.degree_progress_unit_requirements_template_id_idx;
DROP INDEX IF EXISTS public.idx_advisor_author_index;
DROP INDEX IF EXISTS public.idx_notes_fts_index;
DROP INDEX IF EXISTS public.note_attachments_note_id_idx;
DROP INDEX IF EXISTS public.note_template_attachments_note_template_id_idx;
DROP INDEX IF EXISTS public.note_template_topics_note_template_id_idx;
DROP INDEX IF EXISTS public.note_templates_creator_id_idx;
DROP INDEX IF EXISTS public.note_topics_note_id_idx;
DROP INDEX IF EXISTS public.note_topics_topic_idx;
DROP INDEX IF EXISTS public.notes_author_id_idx;
DROP INDEX IF EXISTS public.notes_read_note_id_idx;
DROP INDEX IF EXISTS public.notes_read_viewer_id_idx;
DROP INDEX IF EXISTS public.notes_sid_idx;
DROP INDEX IF EXISTS public.student_groups_owner_id_idx;
DROP INDEX IF EXISTS public.tool_settings_key_idx;
DROP INDEX IF EXISTS public.user_logins_uid_idx;

--

ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_pkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_pkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_alert_type_key_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_alert_type_key_created_at_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.appointment_availability DROP CONSTRAINT IF EXISTS appointment_availability_pkey;
ALTER TABLE IF EXISTS ONLY public.appointment_topics DROP CONSTRAINT IF EXISTS appointment_topics_pkey;
ALTER TABLE IF EXISTS ONLY public.appointments_read DROP CONSTRAINT IF EXISTS appointments_read_pkey;
ALTER TABLE IF EXISTS ONLY public.appointments DROP CONSTRAINT IF EXISTS appointments_pkey;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_pkey;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_uid_key;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_events DROP CONSTRAINT IF EXISTS cohort_filter_events_pkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_pkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filters DROP CONSTRAINT IF EXISTS cohort_filters_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_categories DROP CONSTRAINT IF EXISTS degree_progress_categories_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_category_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_category_unit_requirements_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_course_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_course_unit_requirements_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_courses DROP CONSTRAINT IF EXISTS degree_progress_courses_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_templates DROP CONSTRAINT IF EXISTS degree_progress_templates_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_notes DROP CONSTRAINT IF EXISTS degree_progress_notes_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_unit_requirements_pkey;
ALTER TABLE IF EXISTS ONLY public.drop_in_advisors DROP CONSTRAINT IF EXISTS drop_in_advisors;
ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_key_key;
ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_pkey;
ALTER TABLE IF EXISTS ONLY public.manually_added_advisees DROP CONSTRAINT IF EXISTS manually_added_advisees_pkey;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_pkey;
ALTER TABLE IF EXISTS ONLY public.note_template_attachments DROP CONSTRAINT IF EXISTS note_template_attachments_pkey;
ALTER TABLE IF EXISTS ONLY public.note_template_topics DROP CONSTRAINT IF EXISTS note_template_topics_pkey;
ALTER TABLE IF EXISTS ONLY public.note_templates DROP CONSTRAINT IF EXISTS note_templates_pkey;
ALTER TABLE IF EXISTS ONLY public.note_topics DROP CONSTRAINT IF EXISTS note_topics_pkey;
ALTER TABLE IF EXISTS ONLY public.notes DROP CONSTRAINT IF EXISTS notes_pkey;
ALTER TABLE IF EXISTS ONLY public.notes_read DROP CONSTRAINT IF EXISTS notes_read_pkey;
ALTER TABLE IF EXISTS ONLY public.same_day_advisors DROP CONSTRAINT IF EXISTS same_day_advisors_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.schedulers DROP CONSTRAINT IF EXISTS schedulers_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_pkey;
ALTER TABLE IF EXISTS ONLY public.student_groups DROP CONSTRAINT IF EXISTS student_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.tool_settings DROP CONSTRAINT IF EXISTS tool_settings_key_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.topics DROP CONSTRAINT IF EXISTS topics_id_pkey;
ALTER TABLE IF EXISTS ONLY public.topics DROP CONSTRAINT IF EXISTS topics_topic_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.university_dept_members DROP CONSTRAINT IF EXISTS university_dept_members_pkey;
ALTER TABLE IF EXISTS ONLY public.university_depts DROP CONSTRAINT IF EXISTS university_dept_members_pkey;
ALTER TABLE IF EXISTS ONLY public.user_logins DROP CONSTRAINT IF EXISTS user_logins_pkey;
ALTER TABLE IF EXISTS public.alerts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.authorized_users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cohort_filters ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.json_cache ALTER COLUMN id DROP DEFAULT;

--

DROP MATERIALIZED VIEW IF EXISTS public.advisor_author_index;
DROP MATERIALIZED VIEW IF EXISTS public.notes_fts_index;
DROP TABLE IF EXISTS public.notes;
DROP TABLE IF EXISTS public.note_attachments;
DROP SEQUENCE IF EXISTS public.note_attachments_id_seq;
DROP TABLE IF EXISTS public.note_template_attachments;
DROP SEQUENCE IF EXISTS public.note_template_attachments_id_seq;
DROP TABLE IF EXISTS public.note_template_topics;
DROP SEQUENCE IF EXISTS public.note_template_topics_id_seq;
DROP TABLE IF EXISTS public.note_templates;
DROP SEQUENCE IF EXISTS public.note_templates_id_seq;
DROP TABLE IF EXISTS public.note_topics;
DROP SEQUENCE IF EXISTS public.note_topics_id_seq;
DROP TABLE IF EXISTS public.notes_read;
DROP TABLE IF EXISTS public.manually_added_advisees;
DROP SEQUENCE IF EXISTS public.json_cache_id_seq;
DROP TABLE IF EXISTS public.json_cache;
DROP TABLE IF EXISTS public.drop_in_advisors;
DROP TABLE IF EXISTS public.degree_progress_templates;
DROP SEQUENCE IF EXISTS public.degree_progress_templates_id_seq;
DROP TABLE IF EXISTS public.degree_progress_unit_requirements;
DROP SEQUENCE IF EXISTS public.degree_progress_unit_requirements_id_seq;
DROP TABLE IF EXISTS public.degree_progress_notes;
DROP TABLE IF EXISTS public.cohort_filters;
DROP SEQUENCE IF EXISTS public.cohort_filters_id_seq;
DROP TABLE IF EXISTS public.cohort_filter_events;
DROP SEQUENCE IF EXISTS public.cohort_filter_events_id_seq;
DROP TABLE IF EXISTS public.cohort_filter_owners;
DROP SEQUENCE IF EXISTS public.authorized_users_id_seq;
DROP TABLE IF EXISTS public.authorized_users;
DROP MATERIALIZED VIEW IF EXISTS public.appointments_fts_index;
DROP TABLE IF EXISTS public.appointment_availability;
DROP SEQUENCE IF EXISTS public.appointment_availability_id_seq;
DROP TABLE IF EXISTS public.appointment_events;
DROP SEQUENCE IF EXISTS public.appointment_events_id_seq;
DROP TABLE IF EXISTS public.appointment_topics;
DROP SEQUENCE IF EXISTS public.appointment_topics_id_seq;
DROP TABLE IF EXISTS public.appointments;
DROP SEQUENCE IF EXISTS public.appointments_id_seq;
DROP TABLE IF EXISTS public.appointments_read;
DROP SEQUENCE IF EXISTS public.alerts_id_seq;
DROP TABLE IF EXISTS public.alerts;
DROP TABLE IF EXISTS public.alert_views;
DROP TABLE IF EXISTS public.alembic_version;
DROP TABLE IF EXISTS public.degree_progress_courses;
DROP SEQUENCE IF EXISTS public.degree_progress_courses_id_seq;
DROP TABLE IF EXISTS public.degree_progress_categories;
DROP SEQUENCE IF EXISTS public.degree_progress_categories_id_seq;
DROP TABLE IF EXISTS public.degree_progress_category_unit_requirements;
DROP TABLE IF EXISTS public.degree_progress_course_unit_requirements;
DROP TABLE IF EXISTS public.same_day_advisors;
DROP TABLE IF EXISTS public.schedulers;
DROP TABLE IF EXISTS public.student_group_members;
DROP TABLE IF EXISTS public.student_groups;
DROP SEQUENCE IF EXISTS public.student_groups_id_seq;
DROP TABLE IF EXISTS public.tool_settings;
DROP SEQUENCE IF EXISTS public.tool_settings_id_seq;
DROP TABLE IF EXISTS public.topics;
DROP SEQUENCE IF EXISTS public.topics_id_seq;
DROP TABLE IF EXISTS public.university_dept_members;
DROP TABLE IF EXISTS public.university_depts;
DROP SEQUENCE IF EXISTS public.university_depts_id_seq;
DROP TABLE IF EXISTS public.user_logins;
DROP SEQUENCE IF EXISTS public.user_logins_id_seq;

DROP TYPE IF EXISTS public.appointment_event_types;
DROP TYPE IF EXISTS public.appointment_student_contact_types;
DROP TYPE IF EXISTS public.appointment_types;
DROP TYPE IF EXISTS public.cohort_filter_event_types;
DROP TYPE IF EXISTS public.cohort_domain_types;
DROP TYPE IF EXISTS public.degree_progress_category_types;
DROP TYPE IF EXISTS public.drop_in_advisor_status_types;
DROP TYPE IF EXISTS public.generic_permission_types;
DROP TYPE IF EXISTS public.university_dept_member_role_types;
DROP TYPE IF EXISTS public.weekday_types;
