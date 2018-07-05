BEGIN;

ALTER TABLE IF EXISTS ONLY public.student_athletes DROP CONSTRAINT IF EXISTS student_athletes_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.student_athletes DROP CONSTRAINT IF EXISTS student_athletes_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_students DROP CONSTRAINT IF EXISTS normalized_cache_students_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_student_majors DROP CONSTRAINT IF EXISTS normalized_cache_student_majors_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_enrollments DROP CONSTRAINT IF EXISTS normalized_cache_enrollments_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.alerts DROP CONSTRAINT IF EXISTS alerts_sid_fkey;
ALTER TABLE IF EXISTS ONLY public.alert_views DROP CONSTRAINT IF EXISTS alert_views_alert_id_fkey;
ALTER TABLE IF EXISTS ONLY public.student_group_members DROP CONSTRAINT IF EXISTS student_group_members_sid_fkey;

DROP INDEX IF EXISTS public.normalized_cache_students_units_idx;
DROP INDEX IF EXISTS public.normalized_cache_students_level_idx;
DROP INDEX IF EXISTS public.normalized_cache_students_gpa_idx;
DROP INDEX IF EXISTS public.normalized_cache_student_majors_sid_idx;
DROP INDEX IF EXISTS public.normalized_cache_student_majors_major_idx;
DROP INDEX IF EXISTS public.normalized_cache_enrollments_term_id_idx;
DROP INDEX IF EXISTS public.normalized_cache_enrollments_section_id_idx;
DROP INDEX IF EXISTS public.normalized_cache_enrollments_sid_idx;

ALTER TABLE IF EXISTS ONLY public.students DROP CONSTRAINT IF EXISTS students_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_students DROP CONSTRAINT IF EXISTS normalized_cache_students_pkey;
ALTER TABLE IF EXISTS ONLY public.normalized_cache_student_majors DROP CONSTRAINT IF EXISTS normalized_cache_student_majors_pkey;
ALTER TABLE IF EXISTS ONLY public.athletics DROP CONSTRAINT IF EXISTS athletics_pkey;

DROP TABLE IF EXISTS public.students;
DROP TABLE IF EXISTS public.student_athletes;
DROP TABLE IF EXISTS public.normalized_cache_students;
DROP TABLE IF EXISTS public.normalized_cache_student_majors;
DROP TABLE IF EXISTS public.normalized_cache_enrollments;
DROP TABLE IF EXISTS public.athletics;

COMMIT;
