/**
 * Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.
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

BEGIN;

ALTER TABLE athletics ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE athletics ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE authorized_users ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE authorized_users ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE cohort_filters ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE cohort_filters ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE ONLY cohort_filter_owners
    DROP CONSTRAINT cohort_filter_owners_cohort_filter_id_fkey,
    ADD CONSTRAINT cohort_filter_owners_cohort_filter_id_fkey FOREIGN KEY (cohort_filter_id) REFERENCES cohort_filters(id) ON DELETE CASCADE;
ALTER TABLE ONLY cohort_filter_owners
    DROP CONSTRAINT cohort_filter_owners_user_id_fkey,
    ADD CONSTRAINT cohort_filter_owners_user_id_fkey FOREIGN KEY (user_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

ALTER TABLE json_cache ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE json_cache ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE normalized_cache_student_majors ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE normalized_cache_student_majors ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE ONLY normalized_cache_student_majors
    ADD CONSTRAINT normalized_cache_student_majors_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;

ALTER TABLE normalized_cache_students ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE normalized_cache_students ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE ONLY normalized_cache_students
    ADD CONSTRAINT normalized_cache_students_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;

ALTER TABLE ONLY student_athletes
    DROP CONSTRAINT student_athletes_group_code_fkey,
    ADD CONSTRAINT student_athletes_group_code_fkey FOREIGN KEY (group_code) REFERENCES athletics(group_code) ON DELETE CASCADE;
ALTER TABLE ONLY student_athletes
    DROP CONSTRAINT student_athletes_sid_fkey,
    ADD CONSTRAINT student_athletes_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;

ALTER TABLE students ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE students ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMIT;
