BEGIN;

CREATE TABLE degree_progress_course_unit_requirements (
  category_id INTEGER,
  unit_requirement_id INTEGER
);
ALTER TABLE degree_progress_course_unit_requirements OWNER TO app_boa;
ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_requirements_pkey PRIMARY KEY (category_id, unit_requirement_id);

ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_reqts_category_id_fkey
    FOREIGN KEY (category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_course_unit_requirements
    ADD CONSTRAINT degree_progress_course_unit_reqts_unit_requirement_id_fkey
    FOREIGN KEY (unit_requirement_id) REFERENCES degree_progress_unit_requirements(id) ON DELETE CASCADE;

COMMIT;
