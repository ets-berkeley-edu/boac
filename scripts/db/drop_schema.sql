/**
 * Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.
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

ALTER TABLE IF EXISTS ONLY public.notes DROP CONSTRAINT IF EXISTS notes_author_id_fkey;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_note_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notes_read DROP CONSTRAINT IF EXISTS notes_read_viewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_cohort_filter_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_viewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_alert_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_student_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.student_groups DROP CONSTRAINT IF EXISTS student_groups_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_groups DROP CONSTRAINT IF EXISTS student_groups_owner_id_name_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.university_dept_members DROP CONSTRAINT IF EXISTS university_dept_members_authorized_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.university_dept_members DROP CONSTRAINT IF EXISTS university_dept_members_university_dept_id_fkey;

--

DROP INDEX IF EXISTS public.notes_author_id_idx;
DROP INDEX IF EXISTS public.notes_sid_idx;
DROP INDEX IF EXISTS public.note_attachments_note_id_idx;
DROP INDEX IF EXISTS public.notes_read_viewer_id_idx;
DROP INDEX IF EXISTS public.notes_read_note_id_idx;
DROP INDEX IF EXISTS public.alerts_sid_idx;
DROP INDEX IF EXISTS public.alert_views_viewer_id_idx;
DROP INDEX IF EXISTS public.alert_views_alert_id_idx;
DROP INDEX IF EXISTS public.student_groups_owner_id_idx;
DROP INDEX IF EXISTS public.idx_notes_fts_index;

--

ALTER TABLE IF EXISTS ONLY public.notes DROP CONSTRAINT IF EXISTS notes_pkey;
ALTER TABLE IF EXISTS ONLY public.note_attachments DROP CONSTRAINT IF EXISTS note_attachments_pkey;
ALTER TABLE IF EXISTS ONLY public.notes_read DROP CONSTRAINT IF EXISTS notes_read_pkey;
ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_pkey;
ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_key_key;
ALTER TABLE IF EXISTS ONLY public.cohort_filters DROP CONSTRAINT IF EXISTS cohort_filters_pkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_pkey;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_uid_key;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_pkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_alert_type_key_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_pkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_pkey;
ALTER TABLE IF EXISTS ONLY public.student_groups DROP CONSTRAINT IF EXISTS student_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.university_dept_members DROP CONSTRAINT IF EXISTS university_dept_members_pkey;
ALTER TABLE IF EXISTS ONLY public.university_depts DROP CONSTRAINT IF EXISTS university_dept_members_pkey;
ALTER TABLE IF EXISTS public.json_cache ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cohort_filters ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.authorized_users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.alerts ALTER COLUMN id DROP DEFAULT;

--

DROP MATERIALIZED VIEW IF EXISTS public.notes_fts_index;
DROP TABLE IF EXISTS public.notes;
DROP TABLE IF EXISTS public.note_attachments;
DROP TABLE IF EXISTS public.notes_read;
DROP SEQUENCE IF EXISTS public.json_cache_id_seq;
DROP TABLE IF EXISTS public.json_cache;
DROP SEQUENCE IF EXISTS public.cohort_filters_id_seq;
DROP TABLE IF EXISTS public.cohort_filters;
DROP TABLE IF EXISTS public.cohort_filter_owners;
DROP SEQUENCE IF EXISTS public.authorized_users_id_seq;
DROP TABLE IF EXISTS public.authorized_users;
DROP SEQUENCE IF EXISTS public.alerts_id_seq;
DROP TABLE IF EXISTS public.alerts;
DROP TABLE IF EXISTS public.alert_views;
DROP TABLE IF EXISTS public.alembic_version;
DROP TABLE IF EXISTS public.student_group_members;
DROP TABLE IF EXISTS public.student_groups;
DROP SEQUENCE IF EXISTS public.student_groups_id_seq;
DROP TABLE IF EXISTS public.university_dept_members;
DROP TABLE IF EXISTS public.university_depts;
DROP SEQUENCE IF EXISTS public.university_depts_id_seq
