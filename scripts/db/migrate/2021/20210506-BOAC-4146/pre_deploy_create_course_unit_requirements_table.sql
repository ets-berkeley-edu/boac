BEGIN;

ALTER TABLE IF EXISTS ONLY public.degree_progress_course_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_course_unit_requirements_pkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_course_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_course_unit_reqts_unit_requirement_id_fkey;
ALTER TABLE IF EXISTS ONLY public.degree_progress_course_unit_requirements DROP CONSTRAINT IF EXISTS degree_progress_course_unit_reqts_course_id_fkey;
ALTER TABLE degree_progress_course_unit_requirements RENAME TO degree_progress_category_unit_requirements;

--

CREATE TABLE degree_progress_course_unit_requirements (
  course_id INTEGER,
  unit_requirement_id INTEGER
);
ALTER TABLE degree_progress_course_unit_requirements OWNER TO app_boac;
ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_requirements_pkey PRIMARY KEY (course_id, unit_requirement_id);

ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_reqts_course_id_fkey
    FOREIGN KEY (course_id) REFERENCES degree_progress_courses(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_reqts_unit_requirement_id_fkey
    FOREIGN KEY (unit_requirement_id) REFERENCES degree_progress_unit_requirements(id) ON DELETE CASCADE;

COMMIT;
