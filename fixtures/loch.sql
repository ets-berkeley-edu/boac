DROP SCHEMA IF EXISTS asc_advising_notes cascade;
DROP SCHEMA IF EXISTS boac_advising_asc cascade;
DROP SCHEMA IF EXISTS boac_advising_coe cascade;
DROP SCHEMA IF EXISTS boac_advising_l_s cascade;
DROP SCHEMA IF EXISTS boac_advising_notes cascade;
DROP SCHEMA IF EXISTS boac_advisor cascade;
DROP SCHEMA IF EXISTS boac_analytics cascade;
DROP SCHEMA IF EXISTS sis_data cascade;
DROP SCHEMA IF EXISTS student cascade;

CREATE SCHEMA asc_advising_notes;
CREATE SCHEMA boac_advising_asc;
CREATE SCHEMA boac_advising_coe;
CREATE SCHEMA boac_advising_l_s;
CREATE SCHEMA boac_advising_notes;
CREATE SCHEMA boac_advisor;
CREATE SCHEMA boac_analytics;
CREATE SCHEMA sis_data;
CREATE SCHEMA student;

CREATE TABLE asc_advising_notes.advising_notes
(
    id VARCHAR NOT NULL,
    asc_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    student_first_name VARCHAR,
    student_last_name VARCHAR,
    meeting_date VARCHAR,
    advisor_uid VARCHAR,
    advisor_first_name VARCHAR,
    advisor_last_name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE asc_advising_notes.advising_note_topics (
    id VARCHAR NOT NULL,
    asc_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    topic VARCHAR
);

CREATE TABLE boac_advising_asc.students
(
    sid VARCHAR NOT NULL,
    intensive BOOLEAN NOT NULL,
    active BOOLEAN NOT NULL,
    status_asc VARCHAR,
    group_code VARCHAR,
    group_name VARCHAR,
    team_code VARCHAR,
    team_name VARCHAR
);

CREATE TABLE boac_advising_asc.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
);

CREATE TABLE boac_advising_coe.students
(
    sid VARCHAR NOT NULL,
    advisor_ldap_uid VARCHAR,
    gender VARCHAR,
    ethnicity VARCHAR,
    minority BOOLEAN NOT NULL,
    did_prep BOOLEAN NOT NULL,
    prep_eligible BOOLEAN NOT NULL,
    did_tprep BOOLEAN NOT NULL,
    tprep_eligible BOOLEAN NOT NULL,
    sat1read INT,
    sat1math INT,
    sat2math INT,
    in_met BOOLEAN NOT NULL,
    grad_term VARCHAR,
    grad_year VARCHAR,
    probation BOOLEAN NOT NULL,
    status VARCHAR
);

CREATE TABLE boac_advising_coe.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
);

CREATE TABLE boac_advising_l_s.students
(
    sid VARCHAR NOT NULL,
    acadplan_code VARCHAR,
    acadplan_descr VARCHAR,
    acadplan_type_code VARCHAR,
    acadplan_ownedby_code VARCHAR,
    ldap_uid VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email_address VARCHAR,
    affiliations VARCHAR
);

CREATE TABLE boac_advising_notes.advising_notes
(
    id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    student_note_nr VARCHAR NOT NULL,
    advisor_sid VARCHAR,
    appointment_id VARCHAR,
    note_category VARCHAR NOT NULL,
    note_subcategory VARCHAR,
    note_body VARCHAR NOT NULL,
    created_by VARCHAR,
    updated_by VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_advising_notes.advising_note_authors
(
    uid VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL
);

CREATE TABLE boac_advising_notes.advising_note_author_names
(
    uid VARCHAR NOT NULL,
    name VARCHAR NOT NULL
);

CREATE TABLE boac_advising_notes.advising_note_topics
(
    advising_note_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    note_topic VARCHAR NOT NULL
);

CREATE TABLE boac_advising_notes.advising_note_attachments
(
    advising_note_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    attachment_seq_nr INT,
    attachment_date DATE,
    created_by VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sis_file_name VARCHAR NOT NULL,
    user_file_name VARCHAR NOT NULL
);

CREATE TABLE boac_advising_notes.advising_note_topic_mappings (
  boa_topic VARCHAR NOT NULL,
  sis_topic VARCHAR NOT NULL
);

CREATE TABLE boac_advisor.advisor_roles
(
   sid VARCHAR NOT NULL,
   uid VARCHAR NOT NULL,
   advisor_type_code VARCHAR NOT NULL,
   advisor_type VARCHAR NOT NULL,
   instructor_type_code VARCHAR NOT NULL,
   instructor_type VARCHAR NOT NULL,
   academic_program_code VARCHAR NOT NULL,
   academic_program VARCHAR NOT NULL,
   cs_permissions VARCHAR NOT NULL
);

CREATE TABLE boac_advisor.advisor_students
(
   advisor_sid VARCHAR NOT NULL,
   student_sid VARCHAR NOT NULL,
   student_uid VARCHAR NOT NULL,
   advisor_type_code VARCHAR NOT NULL,
   advisor_type VARCHAR NOT NULL,
   academic_program_code VARCHAR NOT NULL,
   academic_program VARCHAR NOT NULL,
   academic_plan_code VARCHAR NOT NULL,
   academic_plan VARCHAR NOT NULL
);

CREATE TABLE boac_analytics.section_mean_gpas
(
    sis_term_id VARCHAR NOT NULL,
    sis_section_id VARCHAR NOT NULL,
    gpa_term_id VARCHAR NOT NULL,
    avg_gpa DOUBLE PRECISION NOT NULL
);

CREATE TABLE sis_data.enrolled_primary_sections
(
    term_id VARCHAR NOT NULL,
    sis_section_id VARCHAR NOT NULL,
    sis_course_name VARCHAR NOT NULL,
    sis_course_name_compressed VARCHAR NOT NULL,
    sis_subject_area_compressed VARCHAR NOT NULL,
    sis_catalog_id VARCHAR NOT NULL,
    sis_course_title VARCHAR NOT NULL,
    sis_instruction_format VARCHAR NOT NULL,
    sis_section_num VARCHAR NOT NULL,
    instructors VARCHAR
);

CREATE TABLE sis_data.sis_terms
(
    term_id VARCHAR NOT NULL,
    term_name VARCHAR NOT NULL,
    academic_career VARCHAR NOT NULL,
    term_begins DATE NOT NULL,
    term_ends DATE NOT NULL,
    session_id VARCHAR NOT NULL,
    session_name VARCHAR NOT NULL,
    session_begins DATE NOT NULL,
    session_ends DATE NOT NULL
);

CREATE TABLE student.demographics
(
    sid VARCHAR NOT NULL,
    gender VARCHAR NOT NULL,
    minority BOOLEAN NOT NULL
);

CREATE TABLE student.ethnicities
(
    sid VARCHAR NOT NULL,
    ethnicity VARCHAR NOT NULL
);

CREATE TABLE student.student_holds
(
    sid VARCHAR NOT NULL,
    feed TEXT NOT NULL
);

CREATE TABLE student.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
);

CREATE TABLE student.student_academic_status
(
    sid VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    level VARCHAR(2),
    gpa DECIMAL(4,3),
    units DECIMAL (4,1),
    transfer BOOLEAN,
    expected_grad_term VARCHAR(4)
);

CREATE TABLE student.student_majors
(
    sid VARCHAR NOT NULL,
    major VARCHAR NOT NULL
);

CREATE TABLE student.student_names
(
    sid VARCHAR NOT NULL,
    name VARCHAR NOT NULL
);

CREATE TABLE student.student_enrollment_terms
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    enrollment_term TEXT NOT NULL
);

CREATE TABLE student.student_term_gpas
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    gpa DECIMAL(4,3),
    units_taken_for_gpa DECIMAL(4,1)
);

INSERT INTO asc_advising_notes.advising_notes
(id, asc_id, sid, student_first_name, student_last_name, meeting_date, advisor_uid, advisor_first_name, advisor_last_name, created_at, updated_at)
VALUES
('11667051-139362', '139362', '11667051', 'Deborah', 'Davies', '2014-01-03', '1133399', 'Lemmy', 'Kilmister', '2014-01-03 20:30:00+00', '2014-01-03 20:30:00+00'),
('11667051-139379', '139379', '11667051', 'Deborah', 'Davies', '2014-01-16', '90412', 'Ginger', 'Baker', '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00'),
('8901234567-139379', '139379', '8901234567', 'John David', 'Crossman', '2014-01-16', '90412', 'Ginger', 'Baker', '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00'),
('2345678901-139379', '139379', '2345678901', 'Dave', 'Doolittle', '2014-01-16', '90412', 'Ginger', 'Baker', '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00');

INSERT INTO asc_advising_notes.advising_note_topics
(id, asc_id, sid, topic)
VALUES
('11667051-139362', '139362', '11667051', 'Academic'),
('11667051-139362', '139362', '11667051', 'Other');

CREATE TABLE boac_advising_asc.advising_notes AS (
    SELECT id, asc_id, sid, student_first_name, student_last_name, meeting_date,
        advisor_uid, advisor_first_name, advisor_last_name, created_at, updated_at
    FROM asc_advising_notes.advising_notes
);

CREATE TABLE boac_advising_asc.advising_note_topics AS (
    SELECT id, asc_id, sid, topic
    FROM asc_advising_notes.advising_note_topics
);

CREATE MATERIALIZED VIEW boac_advising_asc.advising_notes_search_index AS (
  SELECT n.id, to_tsvector('english', COALESCE(topic || ' ', '') || advisor_first_name || ' ' || advisor_last_name) AS fts_index
  FROM asc_advising_notes.advising_notes n
  LEFT OUTER JOIN asc_advising_notes.advising_note_topics t
  ON n.id = t.id
);

INSERT INTO boac_advising_asc.students
(sid, intensive, active, status_asc, group_code, group_name, team_code, team_name)
VALUES
('11667051', TRUE, TRUE, 'Compete', 'WFH', 'Women''s Field Hockey', 'FHW', 'Women''s Field Hockey'),
('11667051', TRUE, TRUE, 'Compete', 'WTE', 'Women''s Tennis', 'TNW', 'Women''s Tennis'),
('8901234567', TRUE, TRUE, 'Compete', NULL, NULL, NULL, NULL),
('2345678901', FALSE, TRUE, 'Compete', 'MFB-DB', 'Football, Defensive Backs', 'FBM', 'Football'),
('2345678901', FALSE, TRUE, 'Compete', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('3456789012', TRUE, TRUE, 'Compete', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('5678901234', FALSE, TRUE, 'Compete', 'MFB-DB', 'Football, Defensive Backs', 'FBM', 'Football'),
('5678901234', FALSE, TRUE, 'Compete', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('5678901234', FALSE, TRUE, 'Compete', 'MTE', 'Men''s Tennis', 'TNM', 'Men''s Tennis'),
('7890123456', TRUE, TRUE, 'Compete', 'MBB', 'Men''s Baseball', 'BAM', 'Men''s Baseball'),
('3456789012', TRUE, TRUE, 'Compete', 'MBB-AA', 'Men''s Baseball', 'BAM', 'Men''s Baseball'),
-- 'A mug is a mug in everything.' - Colonel Harrington
('890127492', TRUE, FALSE, 'Trouble', 'MFB-DB', 'Football, Defensive Backs', 'FBM', 'Football'),
('890127492', TRUE, FALSE, 'Trouble', 'MFB-DL', 'Football, Defensive Line', 'FBM', 'Football'),
('890127492', TRUE, FALSE, 'Trouble', 'MTE', 'Men''s Tennis', 'TNM', 'Men''s Tennis'),
('890127492', TRUE, FALSE, 'Trouble', 'WFH', 'Women''s Field Hockey', 'FHW', 'Women''s Field Hockey'),
('890127492', TRUE, FALSE, 'Trouble', 'WTE', 'Women''s Tennis', 'TNW', 'Women''s Tennis');

INSERT INTO boac_advising_asc.student_profiles
(sid, profile)
VALUES
('11667051', :athletics_profile_11667051),
('2345678901', :athletics_profile_2345678901),
('3456789012', :athletics_profile_3456789012),
('5678901234', :athletics_profile_5678901234),
('7890123456', :athletics_profile_7890123456),
('8901234567', :athletics_profile_8901234567),
('890127492', :athletics_profile_890127492);

INSERT INTO boac_advising_coe.students
(sid, advisor_ldap_uid, gender, ethnicity, minority, did_prep, prep_eligible, did_tprep, tprep_eligible,
  sat1read, sat1math, sat2math, in_met, grad_term, grad_year, probation, status)
VALUES
('11667051', '90412', 'M', 'H', FALSE, TRUE, FALSE, FALSE, FALSE, NULL, NULL, NULL, FALSE, NULL, NULL, FALSE, 'C'),
('7890123456', '1133399', 'F', 'B', TRUE, FALSE, TRUE, FALSE, FALSE, 510, 520, 620, FALSE, 'sp', '2020', FALSE, 'C'),
('9000000000', '1133399', 'F', 'B', TRUE, FALSE, TRUE, FALSE, FALSE, NULL, NULL, 720, FALSE, NULL, NULL, FALSE, 'Z'),
('9100000000', '90412', 'M', 'X', FALSE, FALSE, FALSE, FALSE, TRUE, 720, 760, 770, TRUE, 'fa', '2018', TRUE, 'N');

INSERT INTO boac_advising_coe.student_profiles
(sid, profile)
VALUES
('11667051', :coe_profile_11667051),
('7890123456', :coe_profile_7890123456),
('9000000000', :coe_profile_9000000000),
('9100000000', :coe_profile_9100000000);

INSERT INTO boac_advising_l_s.students
(sid, acadplan_code, acadplan_descr, acadplan_type_code, acadplan_ownedby_code, ldap_uid, first_name, last_name, email_address, affiliations)
VALUES
('3456789012', '252B2U', 'Political Economy BA', 'MAJ', 'ISSP', '242881', 'Paul', 'Kerschen', 'atem@example.edu', 'STUDENT-TYPE-REGISTERED'),
('5678901234', '25000U', 'Letters & Sci Undeclared UG', 'MAJ', 'CLS', '9933311', 'Sandeep', 'Jayaprakash', 'sj@example.edu', 'STUDENT-TYPE-NOT REGISTERED');

INSERT INTO boac_advising_notes.advising_notes
(id, sid, student_note_nr, advisor_sid, appointment_id, note_category, note_subcategory, note_body, created_by, updated_by, created_at, updated_at)
VALUES
('11667051-00001', '11667051', '00001', '800700600', NULL, 'Quick Question', 'Hangouts', 'Brigitte is making athletic and moral progress', NULL, NULL, '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00'),
('11667051-00002', '11667051', '00002', '700600500', NULL, 'Evaluation', '', 'Brigitte demonstrates a cavalier attitude toward university requirements', NULL, NULL, '2017-11-01T12:00:00+00', '2017-11-01T12:00:00+00'),
('11667051-00003', '11667051', '00003', '600500400', NULL, 'Appointment', '', 'But the iniquity of oblivion blindely scattereth her poppy, and deals with the memory of men without distinction to merit of perpetuity. Who can but pity the founder of the Pyramids? Herostratus lives that burnt the Temple of Diana, he is almost lost that built it; Time hath spared the Epitaph of Adrians horse, confounded that of himself. In vain we compute our felicities by the advantage of our good names, since bad have equall durations; and Thersites is like to live as long as Agamenon, without the favour of the everlasting Register: Who knows whether the best of men be known? or whether there be not more remarkable persons forgot, then any that stand remembred in the known account of time? the first man had been as unknown as the last, and Methuselahs long life had been his only Chronicle.', NULL, NULL, '2017-11-05T12:00:00+00', '2017-11-06T12:00:00+00'),
('11667051-00004', '11667051', '00004', '600500400', NULL, 'Quick Question', 'Unanswered', ' ', NULL, NULL, '2017-11-05T12:00:00+00', '2017-11-06T12:00:00+00'),
('9000000000-00001', '9000000000', '00001', '600500400', NULL, 'Appointment', '', 'Is this student even on campus?', NULL, NULL, '2017-11-02T12:00:00+00', '2017-11-02T13:00:00+00'),
('9000000000-00002', '9000000000', '00002', '700600500', NULL, 'Evaluation', '', 'I am confounded by this confounding student', 'UCBCONVERSION', NULL, '2017-11-02T12:00:00+00', '2017-11-02T12:00:00+00'),
('9100000000-00001', '9100000000', '00001', '600500400', NULL, 'Evaluation', '', 'Met w/ stu; scheduled next appt. 2/1/2019 @ 1:30. Student continued on 2.0 prob (COP) until Sp ''19. E-mailed test@berkeley.edu: told her she''ll need to drop Eng. 123 by 1-24-19', 'UCBCONVERSION', NULL, '2017-11-02T12:00:00+00', '2017-11-02T12:00:00+00');

INSERT INTO boac_advising_notes.advising_note_authors
(uid, sid, first_name, last_name)
VALUES
('1133397', '600500400', 'Robert', 'Johnson'),
('1133398', '700600500', 'Charlie', 'Christian'),
('1133399', '800700600', 'Joni', 'Mitchell');

INSERT INTO boac_advising_notes.advising_note_author_names
(uid, name)
VALUES
('1133397', 'ROBERT'),
('1133397', 'JOHNSON'),
('1133398', 'CHARLIE'),
('1133398', 'CHRISTIAN'),
('1133399', 'JONI'),
('1133399', 'MITCHELL');

CREATE MATERIALIZED VIEW boac_advising_notes.advising_notes_search_index AS (
  SELECT id, to_tsvector(
    'english',
    CASE
      WHEN note_body IS NOT NULL and TRIM(note_body) != '' THEN note_body
      WHEN note_subcategory IS NOT NULL THEN note_category || ' ' || note_subcategory
      ELSE note_category
    END
  ) AS fts_index
  FROM boac_advising_notes.advising_notes
);

INSERT INTO boac_advising_notes.advising_note_topics
(advising_note_id, sid, note_topic)
VALUES
('11667051-00001', '11667051', 'God Scéaw'),
('11667051-00002', '11667051', 'Earg Scéaw'),
('11667051-00003', '11667051', 'Scéaw Tima'),
('11667051-00002', '11667051', 'Ofscéaw'),
('9000000000-00001', '9000000000', 'Ne Scéaw');

INSERT INTO boac_advising_notes.advising_note_topic_mappings
(boa_topic, sis_topic)
VALUES
('Good Show', 'God Scéaw'),
('Bad Show', 'Earg Scéaw'),
('Show Time', 'Scéaw Tima'),
('Show Off', 'Ofscéaw'),
('No Show', 'Ne Scéaw');

INSERT INTO boac_advising_notes.advising_note_attachments
(advising_note_id, sid, attachment_seq_nr, attachment_date, created_by, created_at, updated_at, sis_file_name, user_file_name)
VALUES
('11667051-00001', '11667051', 1, '2017-10-31', 'UCBCONVERSION', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '11667051_00001_1.pdf', 'efac7b10-c3f2-11e4-9bbd-ab6a6597d26f.pdf'),
('11667051-00002', '11667051', 2, '2017-10-31', '1234', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '11667051_00002_2.jpeg', 'brigitte_photo.jpeg'),
('9000000000-00002', '9000000000', 1, '2017-10-31', '4567', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '9000000000_00002_1.pdf', 'dog_eaten_homework.pdf');

INSERT INTO boac_advisor.advisor_roles
(sid, uid, advisor_type_code, advisor_type, instructor_type_code, instructor_type, academic_program_code, academic_program, cs_permissions)
VALUES
('100000000', '13', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('100100100', '90412', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('100100300', '1022796', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('800700600', '1133399', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('100100600', '242881', 'MAJ', 'Major Advisor', 'ADV', 'Advisor Only', 'UCLS', 'Undergrad Letters & Science', 'UC_CS_AA_CURRICULAR_ADVISOR');

INSERT INTO boac_advisor.advisor_students
(advisor_sid, student_sid, student_uid, advisor_type_code, advisor_type, academic_program_code, academic_program, academic_plan_code, academic_plan)
VALUES
('800700600', '9100000000', '300848', 'COLL', 'College Advisor', 'UCOE', 'Undergrad Engineering', '16288U', 'Bioengineering BS'),
('800700600', '9000000000', '300847', 'COLL', 'College Advisor', 'UCOE', 'Undergrad Engineering', '162B0U', 'Engineering Undeclared UG'),
('800700600', '7890123456', '1049291', 'COLL', 'College Advisor', 'UCOE', 'Undergrad Engineering', '162B3U', 'BioE/MSE Joint Major BS'),
('800700600', '9100000000', '300848', 'MAJ', 'Major Advisor', 'UCOE', 'Undergrad Engineering', '16288U', 'Bioengineering BS'),
('800700600', '11667051', '61889', 'MIN', 'Minor Advisor', 'UCOE', 'Undergrad Engineering', '16I010U', 'Bioengineering UG'),
('100200300', '11667051', '61889', 'MAJ', 'Major Advisor', 'UCLS', 'Undergrad Letters & Science', '25345U', 'English BA'),
('100200300', '2345678901', '98765', 'MAJ', 'Major Advisor', 'UCLS', 'Undergrad Letters & Science', '25345U', 'English BA'),
('100200300', '3456789012', '242881', 'MAJ', 'Major Advisor', 'UCLS', 'Undergrad Letters & Science', '25345U', 'English BA'),
('100200300', '7890123456', '1049291', 'MAJ', 'Major Advisor', 'UCLS', 'Undergrad Letters & Science', '25345U', 'English BA'),
('100200300', '11667051', '61889', 'MIN', 'Minor Advisor', 'UCLS', 'Undergrad Letters & Science', '25I039U', 'English UG'),
('100200300', '9100000000', '300848', 'MIN', 'Minor Advisor', 'UCOE', 'Undergrad Engineering', '25I039U', 'English UG'),
('100200300', '5678901234', '9933311', 'MIN', 'Minor Advisor', 'UCLS', 'Undergrad Letters & Science', '25I054U', 'Medieval Studies UG');

INSERT INTO boac_analytics.section_mean_gpas
(sis_term_id, sis_section_id, gpa_term_id, avg_gpa)
VALUES
('2178','90100','cumulative',3.302),
('2178','90100','2175',3.12),
('2178','90100','2172',3.445),
('2178','90200','cumulative',3.131),
('2178','90200','2175',3.055),
('2178','90200','2172',3.23);

INSERT INTO sis_data.enrolled_primary_sections
(term_id, sis_section_id, sis_course_name, sis_course_name_compressed, sis_subject_area_compressed, sis_catalog_id, sis_course_title, sis_instruction_format, sis_section_num, instructors)
VALUES
('2172', '22100', 'MATH 1A', 'MATH1A', 'MATH', '1A', 'Calculus', 'LEC', '001', 'Gottfried Wilhelm Leibniz'),
('2178', '21057', 'DANISH 1A', 'DANISH1A', 'DANISH', '1A', 'Beginning Danish', 'LEC', '001', 'Karen Blixen'),
('2178', '22140', 'MATH 1A', 'MATH1A', 'MATH', '1A', 'Calculus', 'LEC', '001', 'Gottfried Wilhelm Leibniz'),
('2178', '22141', 'MATH 1A', 'MATH1A', 'MATH', '1A', 'Calculus', 'LEC', '002', 'Sir Isaac Newton'),
('2178', '22172', 'MATH 16A', 'MATH16A', 'MATH', '16A', 'Analytic Geometry and Calculus', 'LEC', '001', 'Gottfried Wilhelm Leibniz, Sir Isaac Newton'),
('2178', '22173', 'MATH 16A', 'MATH16A', 'MATH', '16A', 'Analytic Geometry and Calculus', 'LEC', '002', 'Gottfried Wilhelm Leibniz'),
('2178', '22174', 'MATH 16B', 'MATH16B', 'MATH', '16B', 'Analytic Geometry and Calculus', 'LEC', '001', 'Sir Isaac Newton'),
('2178', '22460', 'MATH 185', 'MATH185', 'MATH', '185', 'Introduction to Complex Analysis', 'LEC', '001', 'Leonhard Euler'),
('2178', '22114', 'MATH 55', 'MATH55', 'MATH', '55', 'Discrete Mathematics', 'LEC', '001', 'David Hilbert');

INSERT INTO sis_data.sis_terms
(term_id, term_name, academic_career, term_begins, term_ends, session_id, session_name, session_begins, session_ends)
VALUES
('2188', '2018 Fall', 'LAW', '2018-08-13', '2018-12-17', '1', 'Regular Academic Session', '2018-08-20', '2018-12-05'),
('2188', '2018 Fall', 'GRAD', '2018-08-15', '2018-12-14', '1', 'Regular Academic Session', '2018-08-22', '2018-12-07'),
('2188', '2018 Fall', 'UCBX', '2018-08-15', '2018-12-14', '1', 'Regular Academic Session', '2018-08-22', '2018-12-07'),
('2188', '2018 Fall', 'UGRD', '2018-08-15', '2018-12-14', '1', 'Regular Academic Session', '2018-08-22', '2018-12-07'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', '10W', '10 Week', '2018-05-15', '2018-07-19'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q1', 'Summer LLM First Quarter', '2018-05-15', '2018-06-04'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q2', 'Summer LLM Second Quarter', '2018-06-06', '2018-06-22'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q3', 'Summer LLM Third Quarter', '2018-06-27', '2018-07-19'),
('2185', '2018 Summer', 'LAW', '2018-05-14', '2018-08-13', 'Q4', 'Summer LLM Fourth Quarter', '2018-07-24', '2018-08-13'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '1', 'Regular Academic Session', '2018-05-21', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '10W', '10 Week', '2018-06-04', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '3W', 'Session E', '2018-07-23', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '6W1', 'Six Week - First', '2018-05-21', '2018-06-29'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '6W2', 'Six Week - Second', '2018-07-02', '2018-08-10'),
('2185', '2018 Summer', 'GRAD', '2018-05-21', '2018-08-10', '8W', 'Session C', '2018-06-18', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '1', 'Regular Academic Session', '2018-05-21', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '10W', '10 Week', '2018-06-04', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '3W', 'Session E', '2018-07-23', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '6W1', 'Six Week - First', '2018-05-21', '2018-06-29'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '6W2', 'Six Week - Second', '2018-07-02', '2018-08-10'),
('2185', '2018 Summer', 'UGRD', '2018-05-21', '2018-08-10', '8W', 'Session C', '2018-06-18', '2018-08-10'),
('2182', '2018 Spring', 'LAW', '2018-01-01', '2018-05-09', '1', 'Regular Academic Session', '2018-01-08', '2018-04-20'),
('2182', '2018 Spring', 'GRAD', '2018-01-09', '2018-05-11', '1', 'Regular Academic Session', '2018-01-16', '2018-05-04'),
('2182', '2018 Spring', 'UCBX', '2018-01-09', '2018-05-11', '1', 'Regular Academic Session', '2018-01-16', '2018-05-04'),
('2182', '2018 Spring', 'UGRD', '2018-01-09', '2018-05-11', '1', 'Regular Academic Session', '2018-01-16', '2018-05-04'),
('2178', '2017 Fall', 'LAW', '2017-08-14', '2017-12-15', '1', 'Regular Academic Session', '2017-08-21', '2017-12-05'),
('2178', '2017 Fall', 'GRAD', '2017-08-16', '2017-12-15', '1', 'Regular Academic Session', '2017-08-23', '2017-12-08'),
('2178', '2017 Fall', 'UCBX', '2017-08-16', '2017-12-15', '1', 'Regular Academic Session', '2017-08-23', '2017-12-08'),
('2178', '2017 Fall', 'UGRD', '2017-08-16', '2017-12-15', '1', 'Regular Academic Session', '2017-08-23', '2017-12-08'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '1', 'Regular Academic Session', '2017-05-22', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '10W', '10 Week', '2017-06-05', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '3W', 'Session E', '2017-07-17', '2017-08-04'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '6W1', 'Six Week - First', '2017-05-22', '2017-06-30'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '6W2', 'Six Week - Second', '2017-07-03', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', '8W', 'Session C', '2017-06-19', '2017-08-11'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q1', 'Summer LLM First Quarter', '2017-05-22', '2017-06-13'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q2', 'Summer LLM Second Quarter', '2017-06-14', '2017-07-04'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q3', 'Summer LLM Third Quarter', '2017-07-05', '2017-07-25'),
('2175', '2017 Summer', 'LAW', '2017-05-17', '2017-08-17', 'Q4', 'Summer LLM Fourth Quarter', '2017-07-26', '2017-08-15'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '1', 'Regular Academic Session', '2017-05-22', '2017-08-11'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '10W', '10 Week', '2017-06-05', '2017-08-11'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '3W', 'Session E', '2017-07-17', '2017-08-04'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '6W1', 'Six Week - First', '2017-05-22', '2017-06-30'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '6W2', 'Six Week - Second', '2017-07-03', '2017-08-11'),
('2175', '2017 Summer', 'GRAD', '2017-05-22', '2017-08-11', '8W', 'Session C', '2017-06-19', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '1', 'Regular Academic Session', '2017-05-22', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '10W', '10 Week', '2017-06-05', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '3W', 'Session E', '2017-07-17', '2017-08-04'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '6W1', 'Six Week - First', '2017-05-22', '2017-06-30'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '6W2', 'Six Week - Second', '2017-07-03', '2017-08-11'),
('2175', '2017 Summer', 'UGRD', '2017-05-22', '2017-08-11', '8W', 'Session C', '2017-06-19', '2017-08-11'),
('2172', '2017 Spring', 'LAW', '2017-01-02', '2017-05-10', '1', 'Regular Academic Session', '2017-01-09', '2017-04-25'),
('2172', '2017 Spring', 'GRAD', '2017-01-10', '2017-05-12', '1', 'Regular Academic Session', '2017-01-17', '2017-05-05'),
('2172', '2017 Spring', 'UCBX', '2017-01-10', '2017-05-12', '1', 'Regular Academic Session', '2017-01-17', '2017-05-05'),
('2172', '2017 Spring', 'UGRD', '2017-01-10', '2017-05-12', '1', 'Regular Academic Session', '2017-01-17', '2017-05-05'),
('2168', '2016 Fall', 'LAW', '2016-08-15', '2016-12-15', '1', 'Regular Academic Session', '2016-08-22', '2016-12-15'),
('2168', '2016 Fall', 'GRAD', '2016-08-17', '2016-12-16', '1', 'Regular Academic Session', '2016-08-24', '2016-12-09'),
('2168', '2016 Fall', 'UCBX', '2016-08-17', '2016-12-16', '1', 'Regular Academic Session', '2016-08-24', '2016-12-09'),
('2168', '2016 Fall', 'UGRD', '2016-08-17', '2016-12-16', '1', 'Regular Academic Session', '2016-08-24', '2016-12-09');

INSERT INTO student.demographics
(sid, gender, minority)
VALUES
('11667051', 'Different Identity', FALSE),
('2345678901', 'Decline to State', FALSE),
('3456789012', 'Male', FALSE),
('5678901234', 'Male', FALSE),
('7890123456', 'Female', TRUE),
('8901234567', 'Different Identity', FALSE),
('890127492', 'Genderqueer/Gender Non-Conform', FALSE),
('9000000000', 'Female', TRUE),
('9100000000', 'Different Identity', FALSE);

INSERT INTO student.ethnicities
(sid, ethnicity)
VALUES
('1133399', 'Japanese / Japanese American'),
('11667051', 'Chinese / Chinese-American'),
('2345678901', 'African-American / Black'),
('3456789012', 'African-American / Black'),
('5678901234', 'Mexican / Mexican-American / Chicano'),
('7890123456', 'Japanese / Japanese American'),
('8901234567', 'White'),
-- Student has two (2) ethnicities mapped to SID
('890127492', 'African-American / Black'),
('890127492', 'Thai'),
('9000000000', 'Japanese / Japanese American'),
('9100000000', 'Korean / Korean-American');

INSERT INTO student.student_holds
(sid, feed)
VALUES
('5678901234', :holds_5678901234_S01),
('5678901234', :holds_5678901234_V00);

INSERT INTO student.student_profiles
(sid, profile)
VALUES
('11667051', :profile_11667051),
('2345678901', :profile_2345678901),
('3456789012', :profile_3456789012),
('5678901234', :profile_5678901234),
('7890123456', :profile_7890123456),
('8901234567', :profile_8901234567),
('890127492', :profile_890127492),
('9000000000', :profile_9000000000),
('9100000000', :profile_9100000000);

INSERT INTO student.student_academic_status
(sid, uid, first_name, last_name, level, gpa, units, transfer, expected_grad_term)
VALUES
('11667051', '61889', 'Deborah', 'Davies', NULL, NULL, 0, FALSE, '2198'),
('2345678901', '98765', 'Dave', 'Doolittle', '30', 3.495, 34, FALSE, '2192'),
('3456789012', '242881', 'Paul', 'Kerschen', '30', 3.005, 70, FALSE, '2192'),
('5678901234', '9933311', 'Sandeep', 'Jayaprakash', '40', 3.501, 102, FALSE, '2192'),
('7890123456', '1049291', 'Paul', 'Farestveit', '40', 3.9, 110, FALSE, '2202'),
('8901234567', '123456', 'John David', 'Crossman', '10', 1.85, 12, FALSE, '2192'),
('890127492', '211159', 'Siegfried', 'Schlemiel', '20', 0.4, 8, FALSE, '2192'),
('9000000000', '300847', 'Wolfgang', 'Pauli-O''Rourke', '20', 2.3, 55, TRUE, '2202'),
('9100000000', '300848', 'Nora Stanton', 'Barney', '20', 3.85, 60, TRUE, '2192');

INSERT INTO student.student_majors
(sid, major)
VALUES
('11667051', 'English BA'),
('11667051', 'Nuclear Engineering BS'),
('2345678901', 'Chemistry BS'),
('3456789012', 'English BA'),
('3456789012', 'Political Economy BA'),
('5678901234', 'Letters & Sci Undeclared UG'),
('7890123456', 'Nuclear Engineering BS'),
('8901234567', 'Economics BA'),
('890127492', 'Mathematics'),
('9000000000', 'Engineering Undeclared UG'),
('9100000000', 'Engineering Undeclared UG');

INSERT INTO student.student_names
(sid, name)
VALUES
('11667051', 'DAVIES'),
('11667051', 'DEBORAH'),
('2345678901', 'DAVE'),
('2345678901', 'DOOLITTLE'),
('3456789012', 'KERSCHEN'),
('3456789012', 'PAUL'),
('5678901234', 'JAYAPRAKASH'),
('5678901234', 'SANDEEP'),
('7890123456', 'FARESTVEIT'),
('7890123456', 'PAUL'),
('8901234567', 'CROSSMAN'),
('8901234567', 'DAVID'),
('8901234567', 'JOHN'),
('890127492', 'SCHLEMIEL'),
('890127492', 'SIEGFRIED'),
('9000000000', 'PAULIOROURKE'),
('9000000000', 'WOLFGANG'),
('9100000000', 'BARNEY'),
('9100000000', 'NORA'),
('9100000000', 'STANTON');

INSERT INTO student.student_enrollment_terms
(sid, term_id, enrollment_term)
VALUES
('11667051', '2012', :enrollment_term_11667051_2012),
('11667051', '2162', :enrollment_term_11667051_2162),
('11667051', '2172', :enrollment_term_11667051_2172),
('11667051', '2178', :enrollment_term_11667051_2178),
('11667051', '2182', :enrollment_term_11667051_2182),
('2345678901', '2172', :enrollment_term_2345678901_2172),
('3456789012', '2178', :enrollment_term_3456789012_2178),
('5678901234', '2178', :enrollment_term_5678901234_2178);

INSERT INTO student.student_term_gpas
(sid, term_id, gpa, units_taken_for_gpa)
VALUES
('11667051', '2162', 3.8, 15),
('11667051', '2172', 2.7, 17),
('11667051', '2175', 0, 0),
('11667051', '2178', 1.8, 15),
('11667051', '2182', 2.9, 14),
('2345678901', '2172', 3.5, 16),
('2345678901', '2175', 0, 4),
('3456789012', '2178', 3.2, 15),
('5678901234', '2178', 2.1, 14);
