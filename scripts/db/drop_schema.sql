/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
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

ALTER TABLE IF EXISTS ONLY public.student_athletes DROP CONSTRAINT IF EXISTS student_athletes_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.student_athletes DROP CONSTRAINT IF EXISTS student_athletes_group_code_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_students DROP CONSTRAINT IF EXISTS normalized_cache_students_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_student_majors DROP CONSTRAINT IF EXISTS normalized_cache_student_majors_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_enrollments DROP CONSTRAINT IF EXISTS normalized_cache_enrollments_term_id_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_enrollments DROP CONSTRAINT IF EXISTS normalized_cache_enrollments_section_id_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_enrollments DROP CONSTRAINT IF EXISTS normalized_cache_enrollments_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_cohort_filter_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_viewer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_alert_id_fkey;
ALTER TABLE IF EXISTS ONLY public.advisor_watchlists DROP CONSTRAINT IF EXISTS advisor_watchlists_watchlist_owner_uid_fkey;
ALTER TABLE IF EXISTS ONLY public.advisor_watchlists DROP CONSTRAINT IF EXISTS advisor_watchlists_sid_fkey;
DROP INDEX IF EXISTS public.normalized_cache_students_units_idx;
DROP INDEX IF EXISTS public.normalized_cache_students_level_idx;
DROP INDEX IF EXISTS public.normalized_cache_students_gpa_idx;
DROP INDEX IF EXISTS public.normalized_cache_student_majors_sid_idx;
DROP INDEX IF EXISTS public.normalized_cache_student_majors_major_idx;
DROP INDEX IF EXISTS public.normalized_cache_course_sections_term_id_idx;
DROP INDEX IF EXISTS public.normalized_cache_course_sections_section_id_idx;
DROP INDEX IF EXISTS public.normalized_cache_enrollments_term_id_idx;
DROP INDEX IF EXISTS public.normalized_cache_enrollments_section_id_idx;
DROP INDEX IF EXISTS public.normalized_cache_enrollments_sid_idx;
DROP INDEX IF EXISTS public.alerts_sid_idx;
DROP INDEX IF EXISTS public.alert_views_viewer_id_idx;
DROP INDEX IF EXISTS public.alert_views_alert_id_idx;
ALTER TABLE IF EXISTS ONLY public.students DROP CONSTRAINT IF EXISTS students_pkey;
ALTER TABLE IF EXISTS ONLY public.student_athletes DROP CONSTRAINT IF EXISTS student_athletes_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_students DROP CONSTRAINT IF EXISTS normalized_cache_students_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_student_majors DROP CONSTRAINT IF EXISTS normalized_cache_student_majors_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_course_sections DROP CONSTRAINT IF EXISTS normalized_cache_course_sections_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_course_sections DROP CONSTRAINT IF EXISTS normalized_cache_course_sections_pkey;
ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_pkey;
ALTER TABLE IF EXISTS ONLY public.json_cache DROP CONSTRAINT IF EXISTS json_cache_key_key;
ALTER TABLE IF EXISTS ONLY public.cohort_filters DROP CONSTRAINT IF EXISTS cohort_filters_pkey;
ALTER TABLE IF EXISTS ONLY public.cohort_filter_owners DROP CONSTRAINT IF EXISTS cohort_filter_owners_pkey;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_uid_key;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_pkey;
ALTER TABLE IF EXISTS ONLY public.athletics DROP CONSTRAINT IF EXISTS athletics_pkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_alert_type_key_unique_constraint;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_pkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.advisor_watchlists DROP CONSTRAINT IF EXISTS advisor_watchlists_pkey;
ALTER TABLE IF EXISTS public.json_cache ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cohort_filters ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.authorized_users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.alerts ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS public.students;
DROP TABLE IF EXISTS public.student_athletes;
DROP TABLE IF EXISTS public.normalized_cache_students;
DROP TABLE IF EXISTS public.normalized_cache_student_majors;
DROP TABLE IF EXISTS public.normalized_cache_course_sections;
DROP TABLE IF EXISTS public.normalized_cache_enrollments;
DROP SEQUENCE IF EXISTS public.json_cache_id_seq;
DROP TABLE IF EXISTS public.json_cache;
DROP SEQUENCE IF EXISTS public.cohort_filters_id_seq;
DROP TABLE IF EXISTS public.cohort_filters;
DROP TABLE IF EXISTS public.cohort_filter_owners;
DROP SEQUENCE IF EXISTS public.authorized_users_id_seq;
DROP TABLE IF EXISTS public.authorized_users;
DROP TABLE IF EXISTS public.athletics;
DROP SEQUENCE IF EXISTS public.alerts_id_seq;
DROP TABLE IF EXISTS public.alerts;
DROP TABLE IF EXISTS public.alert_views;
DROP TABLE IF EXISTS public.alembic_version;
DROP TABLE IF EXISTS public.advisor_watchlists;
