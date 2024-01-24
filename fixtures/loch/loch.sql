DROP SCHEMA IF EXISTS boac_advising_appointments cascade;
DROP SCHEMA IF EXISTS boac_advising_asc cascade;
DROP SCHEMA IF EXISTS boac_advising_coe cascade;
DROP SCHEMA IF EXISTS boac_advising_data_science cascade;
DROP SCHEMA IF EXISTS boac_advising_e_i cascade;
DROP SCHEMA IF EXISTS boac_advising_eop cascade;
DROP SCHEMA IF EXISTS boac_advising_history_dept cascade;
DROP SCHEMA IF EXISTS boac_advising_l_s cascade;
DROP SCHEMA IF EXISTS boac_advising_notes cascade;
DROP SCHEMA IF EXISTS boac_advising_oua cascade;
DROP SCHEMA IF EXISTS boac_advisor cascade;
DROP SCHEMA IF EXISTS boac_analytics cascade;
DROP SCHEMA IF EXISTS sis_advising_notes cascade;
DROP SCHEMA IF EXISTS sis_data cascade;
DROP SCHEMA IF EXISTS student cascade;
DROP SCHEMA IF EXISTS terms cascade;

CREATE SCHEMA boac_advising_appointments;
CREATE SCHEMA boac_advising_asc;
CREATE SCHEMA boac_advising_coe;
CREATE SCHEMA boac_advising_data_science;
CREATE SCHEMA boac_advising_e_i;
CREATE SCHEMA boac_advising_eop;
CREATE SCHEMA boac_advising_history_dept;
CREATE SCHEMA boac_advising_l_s;
CREATE SCHEMA boac_advising_notes;
CREATE SCHEMA boac_advising_oua;
CREATE SCHEMA boac_advisor;
CREATE SCHEMA boac_analytics;
CREATE SCHEMA sis_advising_notes;
CREATE SCHEMA sis_data;
CREATE SCHEMA student;
CREATE SCHEMA terms;

CREATE TABLE boac_advising_appointments.ycbm_advising_appointments
(
    id VARCHAR NOT NULL,
    student_uid VARCHAR,
    student_sid VARCHAR,
    title VARCHAR,
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ends_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cancelled BOOLEAN,
    cancellation_reason TEXT,
    advisor_name VARCHAR,
    appointment_type VARCHAR,
    details VARCHAR
);

CREATE TABLE boac_advising_asc.advising_notes
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
    subject VARCHAR,
    body TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_advising_asc.advising_note_topics (
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

CREATE TABLE boac_advising_data_science.advising_notes
(
    id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    student_first_name VARCHAR,
    student_last_name VARCHAR,
    advisor_email VARCHAR,
    reason_for_appointment VARCHAR,
    conversation_type VARCHAR,
    body VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_advising_e_i.advising_notes
(
    id VARCHAR NOT NULL,
    e_i_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    student_first_name VARCHAR,
    student_last_name VARCHAR,
    meeting_date VARCHAR,
    advisor_uid VARCHAR,
    advisor_first_name VARCHAR,
    advisor_last_name VARCHAR,
    overview VARCHAR,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_advising_e_i.advising_note_topics (
    id VARCHAR NOT NULL,
    e_i_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    topic VARCHAR
);

CREATE TABLE boac_advising_eop.advising_note_topics (
    id VARCHAR,
    sid VARCHAR NOT NULL,
    topic VARCHAR
);

CREATE TABLE boac_advising_eop.advising_notes (
    id VARCHAR PRIMARY KEY,
    sid VARCHAR NOT NULL,
    student_first_name VARCHAR,
    student_last_name VARCHAR,
    meeting_date VARCHAR,
    advisor_uid VARCHAR,
    advisor_first_name VARCHAR,
    advisor_last_name VARCHAR,
    overview VARCHAR,
    note TEXT,
    contact_method VARCHAR,
    attachment VARCHAR,
    privacy_permissions VARCHAR,
    searchable_topics VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_advising_history_dept.advising_notes
(
    id VARCHAR NOT NULL,
    advisor_uid VARCHAR NOT NULL,
    note TEXT,
    sid VARCHAR NOT NULL,
    student_first_name VARCHAR,
    student_last_name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
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

CREATE TABLE boac_advising_notes.advising_note_author_names
(
    uid VARCHAR NOT NULL,
    name VARCHAR NOT NULL
);

CREATE TABLE boac_advising_notes.advising_note_authors
(
    uid VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    campus_email VARCHAR
);

CREATE TABLE boac_advising_oua.student_admit_names (
    sid VARCHAR,
    name VARCHAR
);

CREATE TABLE boac_advising_oua.student_admits
(
    applyuc_cpid VARCHAR NOT NULL,
    cs_empl_id VARCHAR NOT NULL,
    residency_category VARCHAR,
    freshman_or_transfer VARCHAR,
    admit_term VARCHAR,
    admit_status VARCHAR,
    current_sir VARCHAR,
    college VARCHAR,
    first_name VARCHAR,
    middle_name VARCHAR,
    last_name VARCHAR,
    birthdate VARCHAR,
    daytime_phone VARCHAR,
    mobile VARCHAR,
    email VARCHAR,
    campus_email_1 VARCHAR,
    permanent_street_1 VARCHAR,
    permanent_street_2 VARCHAR,
    permanent_city VARCHAR,
    permanent_region VARCHAR,
    permanent_postal VARCHAR,
    permanent_country VARCHAR,
    sex VARCHAR,
    gender_identity VARCHAR,
    xethnic VARCHAR,
    hispanic VARCHAR,
    urem VARCHAR,
    first_generation_college VARCHAR,
    parent_1_education_level VARCHAR,
    parent_2_education_level VARCHAR,
    highest_parent_education_level VARCHAR,
    hs_unweighted_gpa VARCHAR,
    hs_weighted_gpa VARCHAR,
    transfer_gpa VARCHAR,
    act_composite INTEGER,
    act_math INTEGER,
    act_english INTEGER,
    act_reading INTEGER,
    act_writing INTEGER,
    sat_total INTEGER,
    sat_r_evidence_based_rw_section INTEGER,
    sat_r_math_section INTEGER,
    sat_r_essay_reading INTEGER,
    sat_r_essay_analysis INTEGER,
    sat_r_essay_writing INTEGER,
    application_fee_waiver_flag VARCHAR,
    foster_care_flag VARCHAR,
    family_is_single_parent VARCHAR,
    student_is_single_parent VARCHAR,
    family_dependents_num VARCHAR,
    student_dependents_num VARCHAR,
    family_income VARCHAR,
    student_income VARCHAR,
    is_military_dependent VARCHAR,
    military_status VARCHAR,
    reentry_status VARCHAR,
    athlete_status VARCHAR,
    summer_bridge_status VARCHAR,
    last_school_lcff_plus_flag VARCHAR,
    special_program_cep VARCHAR,
    us_citizenship_status VARCHAR,
    us_non_citizen_status VARCHAR,
    citizenship_country VARCHAR,
    permanent_residence_country VARCHAR,
    non_immigrant_visa_current VARCHAR,
    non_immigrant_visa_planned VARCHAR,
    uid VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE boac_advisor.advisor_attributes (
    sid VARCHAR,
    uid VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    title VARCHAR,
    dept_code VARCHAR,
    email VARCHAR,
    campus_email VARCHAR
);

CREATE TABLE boac_advisor.advisor_roles
(
   sid VARCHAR NOT NULL,
   uid VARCHAR NOT NULL,
   advisor_type_code VARCHAR,
   advisor_type VARCHAR,
   instructor_type_code VARCHAR,
   instructor_type VARCHAR,
   academic_program_code VARCHAR,
   academic_program VARCHAR,
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

CREATE TABLE sis_advising_notes.advising_appointments
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

CREATE TABLE sis_advising_notes.advising_appointment_advisor_names
(
    uid VARCHAR NOT NULL,
    name VARCHAR NOT NULL
);

CREATE TABLE sis_advising_notes.advising_appointment_advisors
(
    uid VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL
);

CREATE TABLE sis_advising_notes.advising_notes
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

CREATE TABLE sis_advising_notes.advising_note_topics
(
    advising_note_id VARCHAR NOT NULL,
    sid VARCHAR NOT NULL,
    note_topic VARCHAR NOT NULL
);

CREATE TABLE sis_advising_notes.advising_note_attachments
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

CREATE TABLE sis_advising_notes.advising_note_topic_mappings (
  boa_topic VARCHAR NOT NULL,
  sis_topic VARCHAR NOT NULL
);

CREATE TABLE sis_advising_notes.student_late_drop_eforms (
    id VARCHAR,
    career_code VARCHAR,
    course_display_name VARCHAR,
    course_title VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE,
    edl_load_date VARCHAR,
    eform_id INTEGER,
    eform_status VARCHAR,
    eform_type VARCHAR,
    grading_basis_code VARCHAR,
    grading_basis_description VARCHAR,
    requested_action VARCHAR,
    requested_grading_basis_code VARCHAR,
    requested_grading_basis_description VARCHAR,
    requested_units_taken VARCHAR,
    section_id INTEGER,
    section_num VARCHAR,
    sid VARCHAR NOT NULL,
    student_name VARCHAR,
    term_id VARCHAR(4),
    units_taken VARCHAR,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE sis_data.academic_plan_hierarchy
(
    plan_code VARCHAR,
    plan_status VARCHAR,
    plan_name VARCHAR,
    major_code VARCHAR,
    major_name VARCHAR,
    plan_type_code VARCHAR,
    department_code VARCHAR,
    department_name VARCHAR,
    division_code VARCHAR,
    division_name VARCHAR,
    college_code VARCHAR,
    college_name VARCHAR,
    career_code VARCHAR,
    career_name VARCHAR,
    program_code VARCHAR,
    program_name VARCHAR,
    degree_code VARCHAR,
    degree_name VARCHAR
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

CREATE TABLE student.academic_standing
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR NOT NULL,
    acad_standing_action VARCHAR NOT NULL,
    acad_standing_status VARCHAR NOT NULL,
    action_date VARCHAR NOT NULL
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

CREATE TABLE student.intended_majors
(
    sid VARCHAR NOT NULL,
    major VARCHAR NOT NULL
);

CREATE TABLE student.minors
(
    sid VARCHAR NOT NULL,
    minor VARCHAR NOT NULL
);

CREATE TABLE student.student_degrees
(
    sid VARCHAR NOT NULL,
    plan VARCHAR NOT NULL,
    date_awarded DATE NOT NULL,
    term_id VARCHAR NOT NULL
);

CREATE TABLE student.student_holds
(
    sid VARCHAR NOT NULL,
    feed TEXT NOT NULL
);

CREATE TABLE student.student_incompletes
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    frozen BOOLEAN,
    lapse_date VARCHAR,
    grade VARCHAR
);

CREATE TABLE student.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL,
    profile_summary TEXT NOT NULL
);

CREATE TABLE student.student_profile_index
(
    sid VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    level VARCHAR(2),
    gpa DECIMAL(5,3),
    units DECIMAL (4,1),
    transfer BOOLEAN,
    email_address VARCHAR,
    entering_term VARCHAR(4),
    expected_grad_term VARCHAR(4),
    terms_in_attendance INT,
    academic_career_status VARCHAR
);

CREATE TABLE student.student_majors
(
    sid VARCHAR NOT NULL,
    college VARCHAR NOT NULL,
    major VARCHAR NOT NULL,
    division VARCHAR NOT NULL
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
    enrollment_term TEXT NOT NULL,
    midpoint_deficient_grade BOOLEAN NOT NULL,
    incomplete_grade BOOLEAN NOT NULL,
    enrolled_units DECIMAL(3,1),
    term_gpa DECIMAL(5,3)
);

CREATE TABLE student.student_term_gpas
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    gpa DECIMAL(4,3),
    units_taken_for_gpa DECIMAL(4,1)
);

CREATE TABLE student.visas (
    sid VARCHAR,
    visa_status VARCHAR,
    visa_type VARCHAR
);

CREATE TABLE terms.current_term_index
(
    current_term_name VARCHAR NOT NULL,
    future_term_name VARCHAR NOT NULL
);

CREATE TABLE terms.term_definitions
(
    term_id VARCHAR(4) NOT NULL,
    term_name VARCHAR NOT NULL,
    term_begins DATE NOT NULL,
    term_ends DATE NOT NULL
);

INSERT INTO boac_advising_appointments.ycbm_advising_appointments
(id, student_uid, student_sid, title, starts_at, ends_at, cancelled, cancellation_reason, advisor_name, appointment_type, details)
VALUES
('34789-925470-48723', '191919', '9191919191', 'Need help getting Travis to pass', '2021-08-13 11:00:00+00', '2021-08-13 1:00:00+00', FALSE, NULL, 'Crossman', 'Github', 'Failure is the name of the game'),
('78342-847236-73423', '191919', '9191919191', 'YCBM', '2021-08-13 11:00:00+00', '2021-08-13 1:00:00+00', FALSE, NULL, 'Villalobos', 'Github', 'Need an A to pass'),
('83920-809233-32433', '191919', '9191919191', 'Did you know when you eat pineapples, they eat you back?', '2015-08-13 11:00:00+00', '2015-08-13 1:00:00+00', TRUE, 'Dont eat too many pineapples', 'Cesar', 'Hangout', 'It is because of an enzyme that breaks down proteins in your tongue, thats why it feels tingly');

INSERT INTO boac_advising_asc.advising_notes
(id, asc_id, sid, student_first_name, student_last_name, meeting_date, advisor_uid, advisor_first_name, advisor_last_name, subject, body, created_at, updated_at)
VALUES
('11667051-139362', '139362', '11667051', 'Deborah', 'Davies', '2014-01-03', '1133399', 'Lemmy', 'Kilmister', NULL, NULL, '2014-01-03 20:30:00+00', '2014-01-03 20:30:00+00'),
('11667051-139379', '139379', '11667051', 'Deborah', 'Davies', '2014-01-16', '90412', 'Ginger', 'Baker', 'Ginger Baker''s Air Force', E'Bands led by drummers\ntend to leave a lot of space for drum solos', '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00'),
('8901234567-139379', '139379', '8901234567', 'John David', 'Crossman', '2014-01-16', '90412', 'Ginger', 'Baker', NULL, NULL, '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00'),
('2345678901-139379', '139379', '2345678901', 'Dave', 'Doolittle', '2014-01-16', '90412', 'Ginger', 'Baker', NULL, NULL, '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00');

INSERT INTO boac_advising_asc.advising_note_topics
(id, asc_id, sid, topic)
VALUES
('11667051-139362', '139362', '11667051', 'Academic'),
('11667051-139362', '139362', '11667051', 'Other');

CREATE MATERIALIZED VIEW boac_advising_asc.advising_notes_search_index AS (
  SELECT n.id, to_tsvector('english', COALESCE(topic || ' ', '') || advisor_first_name || ' ' || advisor_last_name) AS fts_index
  FROM boac_advising_asc.advising_notes n
  LEFT OUTER JOIN boac_advising_asc.advising_note_topics t
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

INSERT INTO boac_advising_data_science.advising_notes
(id, sid, student_first_name, student_last_name, advisor_email, reason_for_appointment, conversation_type, body, created_at)
VALUES
('11667051-20190801112456','11667051','Deborah','Davies','joni@berkeley.edu','Degree Check','Scheduled appointment','Buyer beware: there are many data charlatans out there posing as data scientists. There’s no magic that makes certainty out of uncertainty.','2019-08-01 18:24:56+00'),
('11667051-20181003051208','11667051','Deborah','Davies','33333@berkeley.edu','Declaring the major, Course planning, Domain Emphasis','Unscheduled Drop-in','Data that is loved tends to survive.','2018-10-04 00:12:08+00');

CREATE MATERIALIZED VIEW boac_advising_data_science.advising_notes_search_index AS (
  SELECT n.id, to_tsvector('english', COALESCE(n.body || ' ', '') || n.reason_for_appointment) AS fts_index
  FROM boac_advising_data_science.advising_notes n
);

INSERT INTO boac_advising_e_i.advising_notes
(id, e_i_id, sid, student_first_name, student_last_name, meeting_date, advisor_uid, advisor_first_name, advisor_last_name, overview, note, created_at, updated_at)
VALUES
('11667051-151620', '151620', '11667051', 'Deborah', 'Davies', '2014-01-03', '1133398', 'Charlie', 'Christian', 'Drop-In', NULL, '2014-01-03 20:30:00+00', '2014-01-03 20:30:00+00'),
('11667051-151621', '151621', '11667051', 'Deborah', 'Davies', '2014-01-16', NULL, 'Reception', 'Front Desk', 'Admin', NULL, '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00'),
('8901234567-151622', '151622', '8901234567', 'John David', 'Crossman', '2014-01-16', NULL, 'Graduate Intern', '', 'Question', NULL, '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00'),
('2345678901-151622', '151622', '2345678901', 'Dave', 'Doolittle', '2014-01-16', NULL, 'Graduate Intern', '', 'Scheduled', NULL, '2014-01-16 16:52:00+00', '2014-01-16 16:52:00+00');

INSERT INTO boac_advising_e_i.advising_note_topics
(id, e_i_id, sid, topic)
VALUES
('11667051-151620', '151620', '11667051', 'Course Planning'),
('11667051-151620', '151620', '11667051', 'Personal');

CREATE MATERIALIZED VIEW boac_advising_e_i.advising_notes_search_index AS (
  SELECT n.id, to_tsvector('english', COALESCE(topic || ' ', '') || advisor_first_name || ' ' || advisor_last_name) AS fts_index
  FROM boac_advising_e_i.advising_notes n
  LEFT OUTER JOIN boac_advising_e_i.advising_note_topics t
  ON n.id = t.id
);

INSERT INTO boac_advising_eop.advising_note_topics
(id, sid, topic)
VALUES
('eop_advising_note_100', '11667051', 'Post-Graduation'),
('eop_advising_note_100', '11667051', 'Cool Podcasts'),
('eop_advising_note_100', '11667051', 'Instagrammable Restaurants');

INSERT INTO boac_advising_eop.advising_notes
(id, sid, student_first_name, student_last_name, meeting_date, advisor_uid, advisor_first_name, advisor_last_name, overview, note, contact_method, attachment, privacy_permissions, searchable_topics, created_at)
VALUES
('eop_advising_note_100', '11667051', 'Deborah', 'Davies', '3/7/2023', '211159', 'ROLAND', 'BESTWESTERN', 'TBB Check In', 'An EOP note', 'Online scheduled', NULL, NULL, '["Post-Graduation", "Cool Podcasts", "Instagrammable Restaurants"]', '2023-03-06 16:00:00+00'),
('eop_advising_note_101', '890127492', 'Siegfried', 'Schlemiel', '3/16/2023', '211159', 'ROLAND', 'BESTWESTERN', NULL, NULL, NULL, 'i am attached.txt', 'Note available only to CE3', '[]', '2023-03-16 12:00:00+00'),
('eop_advising_note_102', '890127492', 'Siegfried', 'Schlemiel', '2/7/2023', '2525', 'MARIAN', 'LIBRARY', 'On the neon, neon side of town', NULL, 'In Person', NULL, 'Note available only to CE3', '[]', '2023-03-06 16:00:00+00');

CREATE MATERIALIZED VIEW boac_advising_eop.advising_notes_search_index AS
  SELECT n.id, to_tsvector('english', COALESCE(n.searchable_topics || ' ', '') || n.advisor_first_name || ' ' || n.advisor_last_name || ' ' || n.overview || ' ' || n.note) AS fts_index
  FROM boac_advising_eop.advising_notes n;

INSERT INTO boac_advising_history_dept.advising_notes
(id, advisor_uid, note, sid, student_first_name, student_last_name, created_at)
VALUES
('history_dept_advising_note_1','82523','History dept note #1','11667051','Deborah','Davies', now()),
('history_dept_advising_note_2','82523','History dept note #2','11667051','Deborah','Davies', now());

CREATE MATERIALIZED VIEW boac_advising_history_dept.advising_notes_search_index AS (
  SELECT id, to_tsvector('english', COALESCE(note, '')) AS fts_index
  FROM boac_advising_history_dept.advising_notes
);

INSERT INTO boac_advising_l_s.students
(sid, acadplan_code, acadplan_descr, acadplan_type_code, acadplan_ownedby_code, ldap_uid, first_name, last_name, email_address, affiliations)
VALUES
('3456789012', '252B2U', 'Political Economy BA', 'MAJ', 'ISSP', '242881', 'Pauline', 'Kerschen', 'atem@example.edu', 'STUDENT-TYPE-REGISTERED'),
('5678901234', '25000U', 'Letters & Sci Undeclared UG', 'MAJ', 'CLS', '9933311', 'Sandeep', 'Jayaprakash', 'sj@example.edu', 'STUDENT-TYPE-NOT REGISTERED');

INSERT INTO boac_advising_notes.advising_note_author_names
(uid, name)
VALUES
('1133397', 'ROBERT'),
('1133397', 'JOHNSON'),
('1133398', 'CHARLIE'),
('1133398', 'CHRISTIAN'),
('1133399', 'JONI'),
('1133399', 'MITCHELL'),
('33333', 'JOHN'),
('33333', 'DELETED-IN-BOA'),
('211159', 'ROLAND'),
('211159', 'BESTWESTERN');

INSERT INTO boac_advising_notes.advising_note_authors
(uid, sid, first_name, last_name, campus_email)
VALUES
('1133397', '600500400', 'Robert', 'Johnson', NULL),
('1133398', '700600500', 'Charlie', 'Christian', NULL),
('1133399', '800700600', 'Joni', 'Mitchell', 'joni@berkeley.edu'),
('33333', '333333333', 'John', 'Deleted-in-BOA', '33333@berkeley.edu'),
('211159', '211159', 'Roland', 'Bestwestern', 'rbestwestern@berkeley.edu');

INSERT INTO boac_advising_oua.student_admit_names
(sid, name)
VALUES
('00005852', 'RALPH'),
('00005852', 'BURGESS'),
('00029117', 'DANIEL'),
('00029117', 'J'),
('00005852', 'MCKNIGHT'),
('11667051', 'DEBORAH'),
('11667051', 'JESSICA'),
('11667051', 'LYNN'),
('11667051', 'DAVIES');

INSERT INTO boac_advising_oua.student_admits
(applyuc_cpid, cs_empl_id, residency_category, freshman_or_transfer, admit_term, admit_status, current_sir, college, first_name, middle_name, last_name, birthdate, daytime_phone, mobile, email, campus_email_1, permanent_street_1, permanent_street_2, permanent_city, permanent_region, permanent_postal, permanent_country, sex, gender_identity, xethnic, hispanic, urem, first_generation_college, parent_1_education_level, parent_2_education_level, highest_parent_education_level, hs_unweighted_gpa, hs_weighted_gpa, transfer_gpa, act_composite, act_math, act_english, act_reading, act_writing, sat_total, sat_r_evidence_based_rw_section, sat_r_math_section, sat_r_essay_reading, sat_r_essay_analysis, sat_r_essay_writing, application_fee_waiver_flag, foster_care_flag, family_is_single_parent, student_is_single_parent, family_dependents_num, student_dependents_num, family_income, student_income, is_military_dependent, military_status, reentry_status, athlete_status, summer_bridge_status, last_school_lcff_plus_flag, special_program_cep, us_citizenship_status, us_non_citizen_status, citizenship_country, permanent_residence_country, non_immigrant_visa_current, non_immigrant_visa_planned, uid, created_at, updated_at)
VALUES
('19938035', '00005852', 'RES', 'Transfer', 'Spring', 'No', 'No', 'College of Letters and Science', 'Ralph', null, 'Burgess', '1984-09-04', '984.110.7693x347', '681-857-8070', 'robert28@hotmail.com', 'abc@b.e', '9590 Chang Extensions', 'Suite 478', 'East Jacobton', 'NY', '55531', 'United States', 'F', 'Other', 'International', 'F', 'No', 'Yes', 'MasterDegree', '3 - High School Graduate', NULL, '0.86', '0.51', '2.47', 7.18, 17.8, 29.18, 18.43, 3.14, 603, 707, 241, 3, 2, 4, 'FeeWaiver', 'Y', NULL, NULL, '05', '02', '41852', '942', 'Y', 'ReserveOfficersTrainingProgram', 'No', NULL, NULL, NULL, NULL, 'Citizen', NULL, 'United States', NULL, NULL, NULL, '123', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00'),
('98002344', '00029117', 'INT', 'Freshman', 'Spring', 'No', 'No', 'College of Engineering', 'Daniel', 'J', 'Mcknight', '1993-07-06', '859-319-8215x8689', '231.865.8093', 'umiles@gmail.com', null, '87758 Brown Throughway', 'Suite 657', 'West Andrea', 'M', '25101', 'United States', '', 'Other', 'White', 'T', NULL, 'Yes', '', '5 - College Attended', NULL, '2.51', '2.7', '3.23', 25.08, 19.28, 1.83, 14.98, 9.02, 1445, 639, 724, 7, 5, 5, NULL, NULL, NULL, 'Y', '0', '02', '23915', '426', 'Y', '', NULL, 'Committed', NULL, '1', 'Destination College', 'Citizen', NULL, 'United States', NULL, NULL, NULL, NULL, '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00'),
('44631475', '11667051', 'RES', '', 'Fall', 'Yes', 'Yes', '', 'Deborah', 'Jessica Lynn', 'Davies', '1985-06-02', '+1-589-507-0244x25165', '+891.337.1621', 'zmitchell@morgan.net', 'food@berkeley.edu', '33770 Miller Fort', 'Apt. 408', 'New Alan', 'GA', '27353', 'Greece', 'M', 'Male', 'NotSpecified', NULL, 'Yes', 'No', 'DoctoralDegree', '3 - High School Graduate', '5 - College Attended', '3.31', '1.06', '1.51', 5.31, 9.42, 16.85, 33.1, 9.66, 1148, 476, 511, 4, 5, 8, 'FeeWaiver', NULL, 'Y', NULL, '05', '01', '12509', '242', NULL, 'Reserve', 'No', NULL, NULL, NULL, '', 'NonCitizen', 'NonImmigrant', 'Greece', NULL, NULL, 'F1', '61889', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00');

INSERT INTO boac_advisor.advisor_attributes
(sid, uid, first_name, last_name, title, dept_code, email, campus_email)
VALUES
('100000000', '13', 'Hurdley', 'Bardolf', 'Student Academic Advisor', 'EDESS', NULL, 'hbarde@berkeley.edu'),
('100100100', '90412', 'Ginger', 'Baker', NULL, 'EGCEE', NULL, 'gbaker@berkeley.edu'),
('100100300', '1022796', 'Bebe', 'De La Rosa', 'Undergraduate Affairs Officer', 'EDDNO', NULL, 'bebe@berkeley.edu'),
('800700600', '1133399', 'Roberta', 'Anderson', 'Department Manager', 'EIIEO', 'joni@gmail.edu', '100200300'),
('211159', '211159', 'Roland', 'Bestwestern', 'Academic Advisor', 'EDESS', NULL, 'rbestwestern@berkeley.edu'),
('100100600', '242881', 'Geert', 'Biederschmitz', 'Harmless Drudge', 'HENGL', NULL, 'geert@berkeley.edu'),
('600500400', '1133397', 'Robert', 'Johnson', 'Undergraduate Academic Advisor', 'HOGSP', NULL, 'robertjohnson@berkeley.edu'),
('111111111', '1', 'Jazz', 'Gunn', 'Graduate Affairs Advisor', 'EDESS', NULL, 'jazzgunn@berkeley.edu'),
('222222222', '2', 'Jimmy', 'Integer', NULL, NULL, NULL, 'jimint@berkeley.edu'),
('333333333', '1234567', 'John', 'Deleted-in-BOA', NULL, NULL, NULL, 'no-boa@berkeley.edu');

INSERT INTO boac_advisor.advisor_roles
(sid, uid, advisor_type_code, advisor_type, instructor_type_code, instructor_type, academic_program_code, academic_program, cs_permissions)
VALUES
('100000000', '13', NULL, 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('100100100', '90412', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_ADVISOR_VIEW'),
('100100100', '90412', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('100100300', '1022796', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_ADVISOR_VIEW'),
('100100300', '1022796', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCLS', 'Undergrad Letters & Science', 'UC_CS_AA_ADVISOR_VIEW'),
('800700600', '1133399', 'DNDS', 'College Dean Designate', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('211159', '211159', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('100100600', '242881', 'MAJ', 'Major Advisor', 'ADV', 'Advisor Only', 'UCLS', 'Undergrad Letters & Science', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('600500400', '1133397', 'MIN', 'Minor Advisor', 'ADV', 'Advisor Only', 'UCLS', 'Undergrad Letters & Science', 'UC_CS_AA_CURRICULAR_ADVISOR'),
('111111111', '1', NULL, NULL, NULL, NULL, NULL, NULL, 'UC_CS_AA_CURRICULAR_ADVISOR'),
('222222222', '2', NULL, NULL, NULL, NULL, 'UBUS', 'Undergrad Business', 'UC_CS_AA_CO_CURRICULAR_ADVISOR'),
('333333333', '1234567', 'COLL', 'College Advisor', 'ADV', 'Advisor Only', 'UCOE', 'Undergrad Engineering', 'UC_CS_AA_ADVISOR_VIEW');

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

INSERT INTO sis_advising_notes.advising_appointments
(id, sid, student_note_nr, advisor_sid, appointment_id, note_category, note_subcategory, note_body, created_by, updated_by, created_at, updated_at)
VALUES
('11667051-00010', '11667051', '00010', '53791', '000000123', 'Appointment Type', 'Document', 'To my people who keep an impressive wingspan even when the cubicle shrink: you got to pull up the intruder by the root of the weed; N.Y. Chew through the machine', NULL, NULL, '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00'),
('11667051-00011', '11667051', '00011', '700600500', NULL, 'Appointment Type', '', '', NULL, NULL, '2017-11-01T12:00:00+00', '2017-11-01T12:00:00+00'),
('11667051-00012', '11667051', '00012', '100200300', NULL, 'Appointment Type', 'Entry w/o Contact', 'When soldering a perfect union it is vital to calculate any ornery loose ends so if mutiny ensues the aloof is assumed nuisance. The clue is in his vacancy, the proof is in his goosebumps.', NULL, NULL, '2017-11-05T12:00:00+00', '2017-11-06T12:00:00+00'),
('9100000000-00010', '9100000000', '00010', '100200300', NULL, 'Appointment Type', '', 'Art imitates life.', 'UCBCONVERSION', NULL, '2017-11-02T12:00:00+00', '2017-11-02T12:00:00+00'),
('2718281828-00002', '2718281828', '00002', '600500400', NULL, 'Appointment Type', '', 'As the largest Pez dispenser on record recouped his numbers', 'UCBCONVERSION', NULL, '2006-11-02T12:00:00+00', '2006-11-02T12:00:00+00');

CREATE MATERIALIZED VIEW sis_advising_notes.advising_appointments_search_index AS (
  SELECT id, to_tsvector(
    'english',
    CASE
      WHEN note_body IS NOT NULL and TRIM(note_body) != '' THEN note_body
      WHEN note_subcategory IS NOT NULL THEN note_category || ' ' || note_subcategory
      ELSE note_category
    END
  ) AS fts_index
  FROM sis_advising_notes.advising_appointments
);

INSERT INTO sis_advising_notes.advising_appointment_advisor_names
(uid, name)
VALUES
('1081940', 'LORAMPS'),
('1081940', 'GLUB'),
('1133398', 'CHARLIE'),
('1133398', 'CHRISTIAN'),
('53791', 'MILICENT'),
('53791', 'BALTHAZAR'),
('1133397', 'Robert'),
('1133397', 'Johnson');

INSERT INTO sis_advising_notes.advising_appointment_advisors
(uid, sid, first_name, last_name)
VALUES
('1081940', '100200300', 'Loramps', 'Glub'),
('1133398', '700600500', 'Charlie', 'Christian'),
('53791', '53791', 'Milicent', 'Balthazar'),
('1133397', '600500400', 'Robert', 'Johnson');

INSERT INTO sis_advising_notes.advising_notes
(id, sid, student_note_nr, advisor_sid, appointment_id, note_category, note_subcategory, note_body, created_by, updated_by, created_at, updated_at)
VALUES
('11667051-00001', '11667051', '00001', '800700600', NULL, 'Quick Question', 'Hangouts', 'Brigitte is making athletic and moral progress', NULL, NULL, '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00'),
('11667051-00002', '11667051', '00002', '700600500', NULL, 'Evaluation', '', 'Brigitte demonstrates a cavalier attitude toward university requirements', NULL, NULL, '2017-11-01T12:00:00+00', '2017-11-01T12:00:00+00'),
('11667051-00003', '11667051', '00003', '600500400', NULL, 'Student Request', '', 'But the iniquity of oblivion blindely scattereth her poppy, and deals with the memory of men without distinction to merit of perpetuity. Who can but pity the founder of the Pyramids? Herostratus lives that burnt the Temple of Diana, he is almost lost that built it; Time hath spared the Epitaph of Adrians horse, confounded that of himself. In vain we compute our felicities by the advantage of our good names, since bad have equall durations; and Thersites is like to live as long as Agamenon, without the favour of the everlasting Register: Who knows whether the best of men be known? or whether there be not more remarkable persons forgot, then any that stand remembred in the known account of time? the first man had been as unknown as the last, and Methuselahs long life had been his only Chronicle.', NULL, NULL, '2017-11-05T12:00:00+00', '2017-11-06T12:00:00+00'),
('11667051-00004', '11667051', '00004', '600500400', NULL, 'Quick Question', 'Unanswered', ' ', NULL, NULL, '2017-11-05T12:00:00+00', '2017-11-06T12:00:00+00'),
('9000000000-00001', '9000000000', '00001', '600500400', NULL, 'Administrative', '', 'Is this student even on campus?', NULL, NULL, '2017-11-02T12:00:00+00', '2017-11-02T13:00:00+00'),
('9000000000-00002', '9000000000', '00002', '700600500', NULL, 'Evaluation', '', 'I am confounded by this confounding student', 'UCBCONVERSION', NULL, '2017-11-02T07:00:00+00', '2017-11-02T07:00:00+00'),
('9100000000-00001', '9100000000', '00001', '600500400', NULL, 'Evaluation', '', 'Met w/ stu; scheduled next appt. 2/1/2019 @ 1:30. Student continued on 2.0 prob (COP) until Sp ''19. E-mailed test@berkeley.edu: told her she''ll need to drop Eng. 123 by 1-24-19', 'UCBCONVERSION', NULL, '2017-11-02T12:00:00+00', '2017-11-02T12:00:00+00'),
('2718281828-00001', '2718281828', '00001', '600500400', NULL, 'Conundrum', '', 'I fear this young fellow shall never settle upon a respectable vocation.', 'UCBCONVERSION', NULL, '2006-11-02T12:00:00+00', '2006-11-02T12:00:00+00');

CREATE MATERIALIZED VIEW sis_advising_notes.advising_notes_search_index AS (
  SELECT id, to_tsvector(
    'english',
    CASE
      WHEN note_body IS NOT NULL and TRIM(note_body) != '' THEN note_body
      WHEN note_subcategory IS NOT NULL THEN note_category || ' ' || note_subcategory
      ELSE note_category
    END
  ) AS fts_index
  FROM sis_advising_notes.advising_notes
);

INSERT INTO sis_advising_notes.advising_note_topics
(advising_note_id, sid, note_topic)
VALUES
('11667051-00001', '11667051', 'God Scéaw'),
('11667051-00002', '11667051', 'Earg Scéaw'),
('11667051-00003', '11667051', 'Scéaw Tima'),
('11667051-00002', '11667051', 'Ofscéaw'),
('11667051-00010', '11667051', 'Ofscéaw'),
('9000000000-00001', '9000000000', 'Ne Scéaw');

INSERT INTO sis_advising_notes.advising_note_topic_mappings
(boa_topic, sis_topic)
VALUES
('Good Show', 'God Scéaw'),
('Bad Show', 'Earg Scéaw'),
('Show Time', 'Scéaw Tima'),
('Show Off', 'Ofscéaw'),
('No Show', 'Ne Scéaw');

INSERT INTO sis_advising_notes.advising_note_attachments
(advising_note_id, sid, attachment_seq_nr, attachment_date, created_by, created_at, updated_at, sis_file_name, user_file_name)
VALUES
('11667051-00001', '11667051', 1, '2017-10-31', 'UCBCONVERSION', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '11667051_00001_1.pdf', 'efac7b10-c3f2-11e4-9bbd-ab6a6597d26f.pdf'),
('11667051-00002', '11667051', 2, '2017-10-31', '1234', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '11667051_00002_2.jpeg', 'brigitte_photo.jpeg'),
('9000000000-00002', '9000000000', 1, '2017-10-31', '4567', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '9000000000_00002_1.pdf', 'dog_eaten_homework.pdf'),
('9100000000-00010', '9100000000', 1, '2017-10-31', '8901', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '9100000000_00010_1.pdf', 'not_a_virus.exe'),
('11667051-00010', '11667051', 1, '2017-10-31', 'UCBCONVERSION', '2017-10-31T12:00:00+00', '2017-10-31T12:00:00+00', '11667051-00010_1.pdf', '11667051-00010_1.pdf');

INSERT INTO sis_advising_notes.student_late_drop_eforms
(id, career_code, course_display_name, course_title, created_at, edl_load_date, eform_id, eform_status, eform_type, grading_basis_code, grading_basis_description, requested_action, requested_grading_basis_code, requested_grading_basis_description, requested_units_taken, section_id, section_num, sid, student_name, term_id, units_taken, updated_at)
VALUES
('eform-10096', 'UGRD', 'MATH 16A', 'ANAL GEO & CALCULUS', '2020-12-05 00:00:00+00', '2021-09-01', 468999, 'Executed', 'SRLATEDROP', 'CPN', 'Pass/No Pass College Adjust', 'Unit Change', ' ', ' ', '1.00', 22335, '001', '11667051', 'Deborah Davies', '2208', '3', '2020-12-08 10:32:08+00'),
('eform-10098', 'UGRD', 'PSYCH 110', 'INTROD BIOL PSYCH', '2020-12-05 12:00:00+00', '2021-09-01', 469118, 'In Error', 'SRLATEDROP', 'EPN', 'Elective Pass/No Pass', 'Late Grading Basis Change', 'GRD', 'Graded', '0.00', 24460, '001', '9000000000', 'Wolfgang Pauli-O''Rourke', '2208', '3', '2020-12-05 00:02:57+00'),
('eform-10099', 'UGRD', 'EECS 16A', 'DESIGN INFO DEV I', '2020-12-05 00:00:00+00', '2021-09-01', 469242, 'Executed', 'SRLATEDROP', 'GRD', 'Graded', 'Late Grading Basis Change', 'EPN', 'Elective Pass/No Pass', '0.00', 31262, '001', '11667051', 'Deborah Davies', '2208', '4', '2020-12-05 00:00:07+00'),
('eform-101', 'UGRD', 'PBHLTH 126', 'HEALTH ECONOMICS', '2020-04-15 00:00:00+00', '2021-09-01', 378785, 'Executed', 'SRLATEDROP', ' ', 'DefaultPNP', 'Late Drop', ' ', ' ', '0.00', 10589, '001', '11667051', 'Deborah Davies', '2202', '3', '2020-04-15 12:46:01+00');

CREATE TABLE boac_advising_notes.advising_notes AS (
SELECT sis.sid, sis.id, sis.note_body, sis.advisor_sid,
       NULL::varchar AS advisor_uid, NULL::varchar AS advisor_first_name, NULL::varchar AS advisor_last_name,
       sis.note_category, sis.note_subcategory, FALSE AS is_private, sis.created_by, sis.created_at, sis.updated_at
FROM sis_advising_notes.advising_notes sis
UNION
SELECT ascn.sid, ascn.id, NULL AS note_body, NULL AS advisor_sid, ascn.advisor_uid, ascn.advisor_first_name, ascn.advisor_last_name,
       NULL AS note_category, NULL AS note_subcategory, FALSE AS is_private, NULL AS created_by, ascn.created_at, ascn.updated_at
FROM boac_advising_asc.advising_notes ascn
UNION
SELECT dsn.sid, dsn.id, dsn.body AS note_body, dsna.sid AS advisor_sid, dsna.uid AS advisor_uid, dsna.first_name AS advisor_first_name,
       dsna.last_name AS advisor_last_name, NULL AS note_category, NULL AS note_subcategory, FALSE AS is_private, NULL AS created_by,
       dsn.created_at, NULL AS updated_at
FROM boac_advising_data_science.advising_notes dsn
JOIN boac_advising_notes.advising_note_authors dsna ON dsn.advisor_email = dsna.campus_email
UNION
SELECT ein.sid, ein.id, NULL AS note_body, NULL AS advisor_sid, ein.advisor_uid, ein.advisor_first_name, ein.advisor_last_name,
       NULL AS note_category, NULL AS note_subcategory, FALSE AS is_private, NULL AS created_by, ein.created_at, ein.updated_at
FROM boac_advising_e_i.advising_notes ein
UNION
SELECT eop.sid, eop.id, note AS note_body, NULL AS advisor_sid, eop.advisor_uid, eop.advisor_first_name, eop.advisor_last_name,
       NULL AS note_category, NULL AS note_subcategory,
       CASE
          WHEN eop.privacy_permissions IS NOT NULL THEN TRUE
          ELSE FALSE
       END AS is_private, eop.advisor_uid AS created_by, eop.created_at,
       eop.created_at AS updated_at
FROM boac_advising_eop.advising_notes eop
UNION
SELECT hdn.sid, hdn.id, hdn.note AS note_body, NULL AS advisor_sid, NULL AS advisor_uid, NULL AS advisor_first_name,
       NULL AS advisor_last_name, NULL AS note_category, NULL AS note_subcategory, FALSE AS is_private, NULL AS created_by,
       NULL AS created_at, NULL AS updated_at
FROM boac_advising_history_dept.advising_notes hdn
);

CREATE MATERIALIZED VIEW boac_advising_notes.advising_notes_search_index AS (
  SELECT id, fts_index FROM boac_advising_asc.advising_notes_search_index
  UNION SELECT id, fts_index FROM boac_advising_data_science.advising_notes_search_index
  UNION SELECT id, fts_index FROM boac_advising_e_i.advising_notes_search_index
  UNION SELECT id, fts_index FROM boac_advising_eop.advising_notes_search_index
  UNION SELECT id, fts_index FROM boac_advising_history_dept.advising_notes_search_index
  UNION SELECT id, fts_index FROM sis_advising_notes.advising_notes_search_index
);

INSERT INTO sis_data.academic_plan_hierarchy
(plan_code, plan_status, plan_name, major_code, major_name, plan_type_code, department_code, department_name, division_code,
division_name, college_code, college_name, career_code, career_name, program_code, program_name, degree_code, degree_name)
VALUES
('00005CCAG', 'A', 'Eng & Busn Sustainability Cert', '00005', 'Grad Div Special Prog', 'OP2', 'GRADDIVOTH', 'Graduate Division Other Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', NULL, NULL, 'CA', 'Eng Bus Sustainability Cert'),
('00014CWOG', 'A', 'African American Studies CWO', '00014', 'African American Studies', 'MAJ', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00014MAG', 'A', 'African American Studies MA', '00014', 'African American Studies', 'MAJ', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00014PHDG', 'A', 'African American Studies PhD', '00014', 'African American Studies', 'MAJ', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00051CPHLG', 'A', 'Anc Hist & Medit Archae CPhil', '00051', 'Anc Hist & Medit Archae', 'MAJ', 'GGAHMA', 'Ancient History and Mediterranean Archaeology GG', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00051CWOG', 'A', 'Anc Hist & Medit Archae CWO', '00051', 'Anc Hist & Medit Archae', 'MAJ', 'GGAHMA', 'Ancient History and Mediterranean Archaeology GG', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00051MAG', 'A', 'Anc Hist & Medit Archae MA', '00051', 'Anc Hist & Medit Archae', 'MAJ', 'GGAHMA', 'Ancient History and Mediterranean Archaeology GG', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00051PHDG', 'A', 'Anc Hist & Medit Archae PhD', '00051', 'Anc Hist & Medit Archae', 'MAJ', 'GGAHMA', 'Ancient History and Mediterranean Archaeology GG', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00059CWOG', 'A', 'International & Area Stds CWO', '00059', 'International & Area Stds', 'MAJ', 'GGIAS', 'Global Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00063CWOG', 'A', 'Anthropology CWO', '00063', 'Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00063MAG', 'A', 'Anthropology MA', '00063', 'Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00072MAG', 'A', 'Applied Mathematics MA', '00072', 'Applied Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00072MSG', 'A', 'Applied Mathematics MS', '00072', 'Applied Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00072PHDG', 'A', 'Applied Mathematics PhD', '00072', 'Applied Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00086PHDG', 'A', 'Applied Science & Tech PhD', '00086', 'Applied Science & Tech', 'MAJ', 'GGAST', 'Applied Science and Technology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00090CWOG', 'A', 'Art CWO', '00090', 'Art', 'MAJ', 'ART', 'Art Practice', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00096PHDG', 'A', 'Asian Studies PhD', '00096', 'Asian Studies', 'MAJ', 'GGASNST', 'Asian Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00099PHDG', 'A', 'Astronomy PhD', '00099', 'Astronomy', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00101CWOG', 'A', 'Astrophysics CWO', '00101', 'Astrophysics', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00101MAG', 'A', 'Astrophysics MA', '00101', 'Astrophysics', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00111MAG', 'A', 'Biochemistry MA', '00111', 'Biochemistry', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00111MSG', 'A', 'Biochemistry MS', '00111', 'Biochemistry', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00111PHDG', 'A', 'Biochemistry PhD', '00111', 'Biochemistry', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00126CWOG', 'A', 'Biophysics CWO', '00126', 'Biophysics', 'MAJ', 'GGBIOPH', 'Biophysics Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00126MSG', 'A', 'Biophysics MS', '00126', 'Biophysics', 'MAJ', 'GGBIOPH', 'Biophysics Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00129MBRG', 'A', 'Bioradiology MBR', '00129', 'Bioradiology', 'HS', 'GRADDIVOTH', 'Graduate Division Other Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '12', 'Master of Bioradiology'),
('00133PHDG', 'A', 'Developmental Biology PhD', '00133', 'Developmental Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00138MAG', 'A', 'Botany MA', '00138', 'Botany', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00138PHDG', 'A', 'Botany PhD', '00138', 'Botany', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00139CWOG', 'A', 'Buddhist Studies CWO', '00139', 'Buddhist Studies', 'MAJ', 'GGBUDST', 'Buddhist Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00174CPHLG', 'A', 'Classics CPhil', '00174', 'Classics', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00174CWOG', 'A', 'Classics CWO', '00174', 'Classics', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00174MAG', 'A', 'Classics MA', '00174', 'Classics', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00174PHDG', 'A', 'Classics PhD', '00174', 'Classics', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00192CPHLG', 'A', 'Comparative Literature CPhil', '00192', 'Comparative Literature', 'MAJ', 'COMLIT', 'Comparative Literature', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00192MAG', 'A', 'Comparative Literature MA', '00192', 'Comparative Literature', 'MAJ', 'COMLIT', 'Comparative Literature', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00192PHDG', 'A', 'Comparative Literature PhD', '00192', 'Comparative Literature', 'MAJ', 'COMLIT', 'Comparative Literature', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00213CWOG', 'A', 'Demography CWO', '00213', 'Demography', 'MAJ', 'DEMOG', 'Demography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00239CWOG', 'A', 'Energy & Resources CWO', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00239EAJDG', 'A', 'Energy & Res MA-JD CDP', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00239EAPPG', 'A', 'Energy & Resources MA-MPP CDP', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00239ESPPG', 'A', 'Energy & Resources MS-MPP CDP', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00239MAG', 'A', 'Energy & Resources MA', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00246CPHLG', 'A', 'Economics CPhil', '00246', 'Economics', 'MAJ', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00246ECJDG', 'A', 'Economics MA-JD CDP', '00246', 'Economics', 'MAJ', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00246MAG', 'A', 'Economics MA', '00246', 'Economics', 'MAJ', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00246PHDG', 'A', 'Economics PhD', '00246', 'Economics', 'MAJ', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002A4CWOG', 'A', 'Earth & Planetary Science CWO', '002A4', 'Earth & Planetary Science', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002A4MSG', 'A', 'Earth & Planetary Science MS', '002A4', 'Earth & Planetary Science', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('002A5PHDG', 'A', 'Sociology & Demography PhD', '002A5', 'Sociology & Demography', 'MAJ', 'GGSODEJ', 'Sociology and Demography Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002A6CPHLG', 'A', 'Molecular & Biochem Nutr CPhil', '002A6', 'Molecular & Biochem Nutrition', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('002A6CWOG', 'A', 'Molecular & Biochem Nutr CWO', '002A6', 'Molecular & Biochem Nutrition', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002C3PHDG', 'A', 'Film and Media PhD', '002C3', 'Film and Media', 'MAJ', 'FILM', 'Film and Media', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002C5MDPG', 'A', 'Development Practice MDP', '002C5', 'Development Practice', 'MAJ', 'GGDEVPR', 'Development Practice Graduate Group', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '97', 'Master of Development Practice'),
('002C7CWOG', 'A', 'Computational Biology CWO', '002C7', 'Computational Biology', 'MAJ', 'GGCPBIO', 'Computational Biology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002C7PHDG', 'A', 'Computational Biology PhD', '002C7', 'Computational Biology', 'MAJ', 'GGCPBIO', 'Computational Biology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002D0CWOG', 'A', 'Metabolic Biology CWO', '002D0', 'Metabolic Biology', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002G6CPHLG', 'A', 'Middle Eastern Lan & Cul CPhil', '002G6', 'Middle Eastern Lang & Cultures', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('002G6CWOG', 'A', 'Middle Eastern Lang & Cul CWO', '002G6', 'Middle Eastern Lang & Cultures', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002G6MAG', 'A', 'Middle Eastern Lang & Cul MA', '002G6', 'Middle Eastern Lang & Cultures', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00360CWOG', 'A', 'Ethnic Studies CWO', '00360', 'Ethnic Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00360MAG', 'A', 'Ethnic Studies MA', '00360', 'Ethnic Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00366MAG', 'A', 'Folklore MA', '00366', 'Folklore', 'MAJ', 'GGFOLK', 'Folklore Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00387CWOG', 'A', 'French CWO', '00387', 'French', 'MAJ', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00396MAG', 'A', 'Geography MA', '00396', 'Geography', 'MAJ', 'GEOG', 'Geography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00402PHDG', 'A', 'Geology PhD', '00402', 'Geology', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00405MSG', 'A', 'Geophysics MS', '00405', 'Geophysics', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00408CWOG', 'A', 'German CWO', '00408', 'German', 'MAJ', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00414MAG', 'A', 'Greek MA', '00414', 'Greek', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00424CWOG', 'A', 'Health & Medical Sciences CWO', '00424', 'Health & Medical Sciences', 'HS', 'GGHMS', 'Health and Medical Sciences Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00425CPHLG', 'A', 'Hispanic Lang & Lit CPhil', '00425', 'Hispanic Lang & Lit', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00425CWOG', 'A', 'Hispanic Lang & Lit CWO', '00425', 'Hispanic Lang & Lit', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00425MAG', 'A', 'Hispanic Lang & Lit MA', '00425', 'Hispanic Lang & Lit', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00428CPHLG', 'A', 'Hlth Serv & Pol Analysis CPhil', '00428', 'Hlth Servs & Pol Analysis', 'HS', 'GGHSPA', 'Health Policy Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00428PHDG', 'A', 'Hlth Serv & Pol Analysis PhD', '00428', 'Hlth Servs & Pol Analysis', 'HS', 'GGHSPA', 'Health Policy Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00429CPHLG', 'A', 'History CPhil', '00429', 'History', 'MAJ', 'HISTORY', 'History', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00429CWOG', 'A', 'History CWO', '00429', 'History', 'MAJ', 'HISTORY', 'History', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00429MAG', 'A', 'History MA', '00429', 'History', 'MAJ', 'HISTORY', 'History', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00469MAG', 'A', 'Chinese Language MA', '00469', 'Chinese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00469PHDG', 'A', 'Chinese Language PhD', '00469', 'Chinese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00470MAG', 'A', 'Japanese Language MA', '00470', 'Japanese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00470PHDG', 'A', 'Japanese Language PhD', '00470', 'Japanese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00477MAG', 'A', 'Italian MA', '00477', 'Italian', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00477PHDG', 'A', 'Italian PhD', '00477', 'Italian', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00492MAG', 'A', 'Global Studies MA', '00492', 'Global Studies', 'MAJ', 'GGIAS', 'Global Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00495MAG', 'A', 'Latin MA', '00495', 'Latin', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00498CWOG', 'A', 'Latin American Studies CWO', '00498', 'Latin American Studies', 'MAJ', 'GGLTAMS', 'Latin American Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00510MAG', 'A', 'Linguistics MA', '00510', 'Linguistics', 'MAJ', 'LINGUIS', 'Linguistics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00510PHDG', 'A', 'Linguistics PhD', '00510', 'Linguistics', 'MAJ', 'LINGUIS', 'Linguistics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00540MAG', 'A', 'Mathematics MA', '00540', 'Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00540PHDG', 'A', 'Mathematics PhD', '00540', 'Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00552PHDG', 'A', 'Medical Physics PhD', '00552', 'Medical Physics', 'HS', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00553CPHLG', 'A', 'Medical Anthro Joint Pgm CPhil', '00553', 'Medical Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '95', 'Joint Candidate in Philosophy'),
('00553CWOG', 'A', 'Medical Anthropology CWO', '00553', 'Medical Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00553JPHDG', 'A', 'Medical Anthro Joint Pgm PhD', '00553', 'Medical Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('00553PHDG', 'A', 'Medical Anthropology PhD', '00553', 'Medical Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00570CWOG', 'A', 'Microbiology CWO', '00570', 'Microbiology', 'MAJ', 'GGMICRO', 'Microbiology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00570MSG', 'A', 'Microbiology MS', '00570', 'Microbiology', 'MAJ', 'GGMICRO', 'Microbiology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00570PHDG', 'A', 'Microbiology PhD', '00570', 'Microbiology', 'MAJ', 'GGMICRO', 'Microbiology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00579MAG', 'A', 'Music MA', '00579', 'Music', 'MAJ', 'MUSIC', 'Music', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00579PHDG', 'A', 'Music PhD', '00579', 'Music', 'MAJ', 'MUSIC', 'Music', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00591CPHLG', 'A', 'Near Eastern Studies CPhil', '00591', 'Near Eastern Studies', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00591CWOG', 'A', 'Near Eastern Studies CWO', '00591', 'Near Eastern Studies', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00591PHDG', 'A', 'Near Eastern Studies PhD', '00591', 'Near Eastern Studies', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00592CPHLG', 'A', 'Near East Relig Jnt Pgm CPhil', '00592', 'Near Eastern Religions', 'MAJ', 'GGNER', 'Near Eastern Religions Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '95', 'Joint Candidate in Philosophy'),
('00592CWOG', 'A', 'Near East Relig Jnt Pgm CWO', '00592', 'Near Eastern Religions', 'MAJ', 'GGNER', 'Near Eastern Religions Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00592JPHDG', 'A', 'Near East Relig Jnt Pgm PhD', '00592', 'Near Eastern Religions', 'MAJ', 'GGNER', 'Near Eastern Religions Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('00593PHDG', 'A', 'Neurobiology PhD', '00593', 'Neurobiology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00594MAG', 'A', 'Neuroscience MA', '00594', 'Neuroscience', 'MAJ', 'HWNI', 'Neuroscience Graduate Program', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('005C3JPHDG', 'A', 'Comp Precision Health Jt PhD', '005C3', 'Comp Precision Health', 'HS', 'GGCPHLTH', 'Computational Precision Health Graduate Group', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('00621CWOG', 'A', 'East Asian Languages CWO', '00621', 'East Asian Languages', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00621MAG', 'A', 'East Asian Languages MA', '00621', 'East Asian Languages', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00627PHDG', 'A', 'Paleontology PhD', '00627', 'Paleontology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00641CPHLG', 'A', 'Human Biodynamics CPhil', '00641', 'Human Biodynamics', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00641MAG', 'A', 'Human Biodynamics MA', '00641', 'Human Biodynamics', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00641PHDG', 'A', 'Human Biodynamics PhD', '00641', 'Human Biodynamics', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00651CWOG', 'A', 'Philosophy CWO', '00651', 'Philosophy', 'MAJ', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00651PHDG', 'A', 'Philosophy PhD', '00651', 'Philosophy', 'MAJ', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00654MAG', 'A', 'Physical Education MA', '00654', 'Physical Education', 'MAJ', 'PHYSED', 'Physical Education', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00666CWOG', 'A', 'Physics CWO', '00666', 'Physics', 'MAJ', 'PHYSICS', 'Physics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00666MAG', 'A', 'Physics MA', '00666', 'Physics', 'MAJ', 'PHYSICS', 'Physics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00666PHDG', 'A', 'Physics PhD', '00666', 'Physics', 'MAJ', 'PHYSICS', 'Physics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00699CWOG', 'A', 'Political Science CWO', '00699', 'Political Science', 'MAJ', 'POLSCI', 'Charles & Louise Travers Dept of Political Science', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00699PHDG', 'A', 'Political Science PhD', '00699', 'Political Science', 'MAJ', 'POLSCI', 'Charles & Louise Travers Dept of Political Science', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00780CPHLG', 'A', 'Psychology CPhil', '00780', 'Psychology', 'MAJ', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00780MAG', 'A', 'Psychology MA', '00780', 'Psychology', 'MAJ', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00807CPHLG', 'A', 'Rhetoric CPhil', '00807', 'Rhetoric', 'MAJ', 'RHETOR', 'Rhetoric', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00807CWOG', 'A', 'Rhetoric CWO', '00807', 'Rhetoric', 'MAJ', 'RHETOR', 'Rhetoric', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00812CWOG', 'A', 'Romance Lang & Lit CWO', '00812', 'Romance Lang & Lit', 'MAJ', 'GGRLL', 'Romance Languages & Literatures Graduate Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00812PHDG', 'A', 'Romance Lang & Lit PhD', '00812', 'Romance Lang & Lit', 'MAJ', 'GGRLL', 'Romance Languages & Literatures Graduate Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00838CPHLG', 'A', 'Scandinavian Lang & Lit CPhil', '00838', 'Scandinavian Lang & Lit', 'MAJ', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00838CWOG', 'A', 'Scandinavian Lang & Lit CWO', '00838', 'Scandinavian Lang & Lit', 'MAJ', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00838MAG', 'A', 'Scandinavian Lang & Lit MA', '00838', 'Scandinavian Lang & Lit', 'MAJ', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00838PHDG', 'A', 'Scandinavian Lang & Lit PhD', '00838', 'Scandinavian Lang & Lit', 'MAJ', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00843CWOG', 'A', 'Science & Math Education CWO', '00843', 'Science & Math Education', 'MAJ', 'GGSME', 'Science and Mathematics Education Graduate Group', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00848CWOG', 'A', 'Infec Diseases & Immunity CWO', '00848', 'Infec Diseases & Immunity', 'HS', 'GGIDI', 'Infectious Diseases & Immunity Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00848MSG', 'A', 'Infec Diseases & Immunity MS', '00848', 'Infec Diseases & Immunity', 'HS', 'GGIDI', 'Infectious Diseases & Immunity Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00848PHDG', 'A', 'Infec Diseases & Immunity PhD', '00848', 'Infec Diseases & Immunity', 'HS', 'GGIDI', 'Infectious Diseases & Immunity Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00849C85G', 'A', 'Russian & E European Stds Cert', '00849', 'Slavic Lang & Lit', 'CRT', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '85', 'Cert-Russ and East European St'),
('00849CPHLG', 'A', 'Slavic Lang & Lit CPhil', '00849', 'Slavic Lang & Lit', 'MAJ', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00849MAG', 'A', 'Slavic Lang & Lit MA', '00849', 'Slavic Lang & Lit', 'MAJ', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00849PHDG', 'A', 'Slavic Lang & Lit PhD', '00849', 'Slavic Lang & Lit', 'MAJ', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00867CWOG', 'A', 'Sociology CWO', '00867', 'Sociology', 'MAJ', 'SOCIOL', 'Sociology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00867PHDG', 'A', 'Sociology PhD', '00867', 'Sociology', 'MAJ', 'SOCIOL', 'Sociology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00877PHDG', 'A', 'South & SE Asian Studies PhD', '00877', 'South & SE Asian Studies', 'MAJ', 'SSEASN', 'South and Southeast Asian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00882MAG', 'A', 'Spanish MA', '00882', 'Spanish', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00891CWOG', 'A', 'Statistics CWO', '00891', 'Statistics', 'MAJ', 'STAT', 'Statistics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00933MAG', 'A', 'Zoology MA', '00933', 'Zoology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('25I047U', 'A', 'History of Art UG', '25MNRHISTART', 'History of Art Minors', 'MIN', 'HISTART', 'History of Art', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('00974CPHLG', 'A', 'Molecular & Cell Biology CPhil', '00974', 'Molecular & Cell Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00974MAG', 'A', 'Molecular & Cell Biology MA', '00974', 'Molecular & Cell Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00974MSG', 'A', 'Molecular & Cell Biology MS', '00974', 'Molecular & Cell Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00974PHDG', 'A', 'Molecular & Cell Biology PhD', '00974', 'Molecular & Cell Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00975CWOG', 'A', 'Integrative Biology CWO', '00975', 'Integrative Biology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('009B2CPHLG', 'A', 'Performance Studies CPhil', '009B2', 'Performance Studies', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('009B2CWOG', 'A', 'Performance Studies CWO', '009B2', 'Performance Studies', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('009B2MAG', 'A', 'Performance Studies MA', '009B2', 'Performance Studies', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00E001L', 'A', 'Comm Computation and Stats DE', '00E001', 'Comm Computation and Stats DE', 'DE', 'GGCCS', 'Communication, Computation, & Statistics Grad Grp', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E002L', 'A', 'Comp and Genomic Biology DE', '00E002', 'Comp and Genomic Biology DE', 'DE', 'GGCPBIO', 'Computational Biology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E003L', 'A', 'Comp & Data Sci & Eng DE', '00E003', 'Computational Sci Engr DE', 'DE', 'GGCSE', 'Comp & Data Science & Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E004L', 'A', 'Critical Theory DE', '00E004', 'Critical Theory DE', 'DE', 'GGCRITH', 'Critical Theory Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E005G', 'A', 'Development Engineering DE', '00E005', 'Development Engineering DE', 'DE', 'GGDEVEN', 'Development Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E006G', 'A', 'Dutch Studies DE', '00E006', 'Dutch Studies DE', 'DE', 'GGDUTCH', 'Dutch Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E008G', 'A', 'Film Studies DE', '00E008', 'Film Studies DE', 'DE', 'GGFILM', 'Film Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E008L', 'A', 'Film Studies DE', '00E008', 'Film Studies DE', 'DE', 'GGFILM', 'Film Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E010G', 'A', 'Global Metropolitan Studies DE', '00E010', 'Global Metropolitan Studies DE', 'DE', 'GGGMS', 'Global Metropolitan Studies Graduate Group', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E013G', 'A', 'Nanoscale Sci and Engr DE', '00E013', 'Nanoscale Sci and Engr DE', 'DE', 'GGNANO', 'Nanoscale Science and Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E014G', 'A', 'New Media DE', '00E014', 'New Media DE', 'DE', 'GGMEDIA', 'New Media Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E014L', 'A', 'New Media DE', '00E014', 'New Media DE', 'DE', 'GGMEDIA', 'New Media Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E015L', 'A', 'Ren and Early Modern Stds DE', '00E015', 'Ren and Early Modern Stds DE', 'DE', 'GGREMS', 'Renaissance & Early Modern Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E016G', 'A', 'Science and Technology Stds DE', '00E016', 'Science and Technology Stds DE', 'DE', 'GGSTS', 'Science and Technology Studies Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E018L', 'A', 'European Studies DE', '00E018', 'European Studies DE', 'DE', 'GGEUROST', 'European Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E021L', 'A', 'Study of Religion DE', '00E021', 'Study of Religion DE', 'DE', 'GGSR', 'Study of Religion Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', NULL, NULL, NULL, NULL),
('00E022G', 'A', 'Political Economy DE', '00E022', 'Political Economy DE', 'DE', 'GGPOLECON', 'Political Economy Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E022L', 'A', 'Political Economy DE', '00E022', 'Political Economy DE', 'DE', 'GGPOLECON', 'Political Economy Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', NULL, NULL, NULL, NULL),
('00E023G', 'A', 'Cognitive Science DE', '00E023', 'Cognitive Science DE', 'DE', 'GGCOGSCI', 'Cognitive Science Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E023L', 'A', 'Cognitive Science DE', '00E023', 'Cognitive Science DE', 'DE', 'GGCOGSCI', 'Cognitive Science Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', NULL, NULL, NULL, NULL),
('00E024L', 'A', 'Comp Precision Health DE', '00E024', 'Comp Precision Health DE', 'DE', 'GGCPHLTH', 'Computational Precision Health Graduate Group', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'LAW', 'Law', NULL, NULL, NULL, NULL),
('00E20L', 'A', 'Sociology of Orgs & Markets DE', '00E20', 'Sociology of Orgs & Markets DE', 'DE', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'LAW', 'Law', NULL, NULL, NULL, NULL),
('00INDMAG', 'A', 'Grad Div Individual Major MA', '00451', 'Grad Div Individual Major', 'MAJ', 'GRADDIVIDP', 'Interdisciplinary Doctoral Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00INDPHDG', 'A', 'Grad Div Individual Major PhD', '00451', 'Grad Div Individual Major', 'MAJ', 'GRADDIVIDP', 'Interdisciplinary Doctoral Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00OPT2001G', 'A', 'New Media Cert', '00OPT2001', 'New Media Cert', 'OP2', 'GGMEDIA', 'New Media Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2006G', 'A', 'Social Work with Latinos Cert', '00OPT2006', 'Social Work with Latinos Cert', 'OP2', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2008G', 'A', 'Graduate Certificate in Aging', '00OPT2008', 'Graduate Certificate in Aging', 'OP2', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2010G', 'A', 'Grad Cert Business Analytics', '00OPT2010', 'Grad Cert Business Analytics', 'OP2', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2012G', 'A', 'Grad Cert Sustainable Business', '00OPT2012', 'Grad Cert Sustainable Business', 'OP2', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2014G', 'A', 'Security Policy Certificate', '00OPT2014', 'Security Policy Certificate', 'OP2', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2018G', 'A', 'Nuclear Security Certificate', '00OPT2018', 'Nuclear Security Certificate', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2019G', 'A', 'IP & Entrep Strategy Cert', '00OPT2019', 'IP & Entrep Strategy Cert', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2021G', 'A', 'Robotic Systems Certificate', '00OPT2021', 'Robotic Systems Certificate', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2023G', 'A', 'TELS&CP Cert', '00OPT2023', 'TELS&CP Certificate', 'OP2', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2024G', 'A', 'Racism, Health, & Soc Jus Cert', '00OPT2024', 'Racism, Health, & Soc Jus Cert', 'OP2', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00V00G', 'A', 'Non-UC Campus Visitor GR', '00V00', 'Non-UC Campus Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V02ICVG', 'A', 'UC San Francisco ICV GR', '00V02', 'UC San Francisco Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V03G', 'A', 'UC Davis Visitor GR', '00V03', 'UC Davis Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V03ICVG', 'A', 'UC Davis ICV GR', '00V03', 'UC Davis Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V05G', 'A', 'UC Riverside Visitor GR', '00V05', 'UC Riverside Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V05ICVG', 'A', 'UC Riverside ICV GR', '00V05', 'UC Riverside Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V06ICVG', 'A', 'UC San Diego ICV GR', '00V06', 'UC San Diego Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V07G', 'A', 'UC Santa Cruz Visitor GR', '00V07', 'UC Santa Cruz Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V07ICVG', 'A', 'UC Santa Cruz ICV GR', '00V07', 'UC Santa Cruz Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V08ICVG', 'A', 'UC Santa Barbara ICV GR', '00V08', 'UC Santa Barbara Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V09ICVG', 'A', 'UC Irvine ICV GR', '00V09', 'UC Irvine Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V10G', 'A', 'UC Merced Visitor GR', '00V10', 'UC Merced Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04008U', 'A', 'CNR Limited UG', '04008', 'CNR Limited', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04034CPHLG', 'A', 'Ag & Resource Economics CPhil', '04034', 'Ag & Resource Economics', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04034CWOG', 'A', 'Ag & Resource Economics CWO', '04034', 'Ag & Resource Economics', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04034PHDG', 'A', 'Ag & Resource Economics PhD', '04034', 'Ag & Resource Economics', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('040IVMNSDG', 'A', 'Nutri Sci & Dietetics MNSD', '040IV', 'Nutri Sci & Dietetics', 'SS', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'C4', 'Master of Nutr Sci & Dietetics'),
('04128U', 'A', 'Biology of Natural Res BS', '04128', 'Biology of Natural Res', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04134U', 'A', 'Bioresource Sciences BS', '04134', 'Bioresource Sciences', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04189CPHLG', 'A', 'Comparative Biochemistry CPhil', '04189', 'Comparative Biochemistry', 'MAJ', 'GGCMBIO', 'Comparative Biochemistry Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04189CWOG', 'A', 'Comparative Biochemistry CWO', '04189', 'Comparative Biochemistry', 'MAJ', 'GGCMBIO', 'Comparative Biochemistry Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04189PHDG', 'A', 'Comparative Biochemistry PhD', '04189', 'Comparative Biochemistry', 'MAJ', 'GGCMBIO', 'Comparative Biochemistry Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04206U', 'A', 'Conserv & Resource Stds BS', '04206', 'Conserv & Resource Stds', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('042C5CWOG', 'A', 'Development Practice CWO', '042C5', 'Development Practice', 'MAJ', 'GGDEVPR', 'Development Practice Graduate Group', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('042C5MDPG', 'A', 'Development Practice MDP', '042C5', 'Development Practice', 'MAJ', 'GGDEVPR', 'Development Practice Graduate Group', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '97', 'Master of Development Practice'),
('042E7U', 'A', 'Eco Mgmt & For-Nat Res Mgmt BS', '042E7', 'Eco Mgmt & For-Nat Res Mgmt', 'SP', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04371U', 'A', 'Food, Nutrition, & Diet BS', '04371', 'Food, Nutrition, & Diet', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('043805YMFG', 'A', 'Forestry 5th Year MF', '04380', 'Forestry', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '23', 'Master of Forestry'),
('04380U', 'A', 'Forestry BS', '04380', 'Forestry', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04392U', 'A', 'Genetics BS', '04392', 'Genetics', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('043A2U', 'A', 'Society and Environment BS', '043A2', 'Society and Environment', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('045A7U', 'A', 'Microbial Biology BS', '045A7', 'Microbial Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04603CPHLG', 'A', 'Nutrition CPhil', '04603', 'Nutrition', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04606U', 'A', 'Nutritional Science BS', '04606', 'Nutritional Science', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04637U', 'A', 'Pest Management BS', '04637', 'Pest Management', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04680CWOG', 'A', 'Plant Biology CWO', '04680', 'Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04680MAG', 'A', 'Plant Biology MA', '04680', 'Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('04680MSG', 'A', 'Plant Biology MS', '04680', 'Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04680PHDG', 'A', 'Plant Biology PhD', '04680', 'Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04681MSG', 'A', 'Plant Pathology MS', '04681', 'Plant Pathology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04681PHDG', 'A', 'Plant Pathology PhD', '04681', 'Plant Pathology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04683CPHLG', 'A', 'Env Sci, Policy, & Mgmt CPhil', '04683', 'Env Sci, Policy, & Mgmt', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04683MSG', 'A', 'Env Sci, Policy, & Mgmt MS', '04683', 'Env Sci, Policy, & Mgmt', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04683PHDG', 'A', 'Env Sci, Policy, & Mgmt PhD', '04683', 'Env Sci, Policy, & Mgmt', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04691U', 'A', 'Plant & Soil Biology BS', '04691', 'Plant & Soil Biology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04698U', 'A', 'Pol Econ of Nat Resources BS', '04698', 'Pol Econ of Nat Resources', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04746U', 'A', 'Genetics & Plant Biology BS', '04746', 'Genetics & Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04798MSG', 'A', 'Rangeland & Wildlife Mgmt MS', '04798', 'Rangeland & Wildlife Mgmt', 'MAJ', 'GGRANGE', 'Rangeland and Wildlife Management Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04803U', 'A', 'Resource Management BS', '04803', 'Resource Management', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04847U', 'A', 'Molecular Environ Biology BS', '04847', 'Molecular Environ Biology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04860U', 'A', 'Soil Environment BS', '04860', 'Soil Environment', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04875U', 'A', 'Soil Resource Management BS', '04875', 'Soil Resource Management', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04876CPHLG', 'A', 'Soil Science CPhil', '04876', 'Soil Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04876PHDG', 'A', 'Soil Science PhD', '04876', 'Soil Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04879U', 'A', 'Soils & Plant Resources BS', '04879', 'Soils & Plant Resources', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04930CPHLG', 'A', 'Wildland Resource Sci CPhil', '04930', 'Wildland Resource Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04930PHDG', 'A', 'Wildland Resource Science PhD', '04930', 'Wildland Resource Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04931U', 'A', 'Forestry & Natural Res BS', '04931', 'Forestry & Natural Resources', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('049A3U', 'A', 'Nutritional Sci-Toxicology BS', '049A3', 'Nutritional Sci-Toxicology', 'SP', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04I002U', 'A', 'Energy & Resources UG', '04MNRERG', 'Energy & Resources Minors', 'MIN', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I005U', 'A', 'Geospatl Info Sci & Tech UG', '04MNRESPM', 'ESPM Minors', 'MIN', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I006U', 'A', 'Nutritional Science UG', '04MNRNUTRSCI', 'Nutritional Science Minors', 'MIN', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I007U', 'A', 'Toxicology UG', '04MNRNUTRSCI', 'Nutritional Science Minors', 'MIN', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I146U', 'A', 'Entomology UG', '04MNRESPM', 'ESPM Minors', 'MIN', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I155U', 'A', 'Sustainability UG', '04MNRERG', 'Energy & Resources Minors', 'MIN', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04V00U', 'A', 'Non-UC Campus Visitor CNR UG', '04V00', 'Non-UC Campus Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V03ICVU', 'A', 'UC Davis ICV CNR UG', '04V03', 'UC Davis Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V03U', 'A', 'UC Davis Visitor CNR UG', '04V03', 'UC Davis Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V04ICVU', 'A', 'UC Los Angeles ICV CNR UG', '04V04', 'UC Los Angeles Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V05ICVU', 'A', 'UC Riverside ICV CNR UG', '04V05', 'UC Riverside Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V07ICVU', 'A', 'UC Santa Cruz ICV CNR UG', '04V07', 'UC Santa Cruz Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V08ICVU', 'A', 'UC Santa Barbara ICV CNR UG', '04V08', 'UC Santa Barbara Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V08U', 'A', 'UC Santa Barbara Visitor NR UG', '04V08', 'UC Santa Barbara Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V09U', 'A', 'UC Irvine Visitor CNR UG', '04V09', 'UC Irvine Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V10ICVU', 'A', 'UC Merced ICV CNR UG', '04V10', 'UC Merced Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('08160U', 'A', 'Chicano Studies BA', '08160', 'Chicano Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('08360U', 'A', 'Ethnic Studies BA', '08360', 'Ethnic Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('08415U', 'A', 'Health Arts and Sciences BA', '08415', 'Health Arts and Sciences', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('08631U', 'A', 'Peace & Conflict Studies BA', '08631', 'Peace & Conflict Studies', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('09000U', 'A', 'Other Undeclared UG', '09000', 'Other Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'BACHL', 'Bachelor''s Degree'),
('09V03U', 'A', 'UC Davis Visitor EVCP UG', '09V03', 'UC Davis Visitor EVCP', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('09V07U', 'A', 'UC Santa Cruz Visitor EVCP UG', '09V07', 'UC Santa Cruz Visitor EVCP', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('10001U', 'A', 'Chem Eng/Eng Joint Major BS', '10001', 'Chem Eng/Eng Joint Major', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('10153CPHLG', 'A', 'Chemistry CPhil', '10153', 'Chemistry', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('10153CWOG', 'A', 'Chemistry CWO', '10153', 'Chemistry', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('10153U', 'A', 'Chemistry BS', '10153', 'Chemistry', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('101A1U', 'A', 'Chemical Biology BS', '101A1', 'Chemical Biology', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('10294CWOG', 'A', 'Chemical Engineering CWO', '10294', 'Chemical Engineering', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('10294MSG', 'A', 'Chemical Engineering MS', '10294', 'Chemical Engineering', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MS', 'Master of Science'),
('10294U', 'A', 'Chemical Engineering BS', '10294', 'Chemical Engineering', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('102B5U', 'A', 'Chem Eng/MSE Joint Major BS', '102B5', 'Chem Eng/MSE Joint Major', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('1038SU', 'A', 'Chemical Biology BS', '1038S', 'Chemical Biology', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('10I008U', 'A', 'Chemical Engineering UG', '10MNRCHMENG', 'Chemical Engineering Minors', 'MIN', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('10I168U', 'A', 'Resp Process Implementation UG', '10MNRCHMENG', 'Chemical Engineering Minors', 'MIN', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('10V00U', 'A', 'Non-UC Campus Visitor CCH UG', '10V00', 'Non-UC Campus Visitor CCH', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('160FQMDESG', 'A', 'Design MDes', '160FQ', 'Master of Design', 'SS', 'DESINV', 'Design Innovation', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'A9', 'Master of Design'),
('162015YMSG', 'A', 'Computer Science 5th Yr MS', '16201', 'Computer Science', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16201CWOG', 'A', 'Computer Science CWO', '16201', 'Computer Science', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16201PHDG', 'A', 'Computer Science PhD', '16201', 'Computer Science', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16275CEARG', 'A', 'Civil & Env Eng MS-MArch CDP', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16275CEBAG', 'A', 'Civ Env Engin MEng-MBA CDP', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16275CECPG', 'A', 'Civil & Env Eng MS-MCP CDP', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16275CWOG', 'A', 'Civil & Environmental Eng CWO', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16275MSG', 'A', 'Civil & Environmental Eng MS', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16275U', 'A', 'Civil & Environmental Eng BS', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16279U', 'A', 'Aerospace Engineering BS', '16279', 'Aerospace Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16287CPHLG', 'A', 'Civil Engineering CPhil', '16287', 'Civil Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('16287DENGG', 'A', 'Civil Engineering DEng', '16287', 'Civil Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16287MSG', 'A', 'Civil Engineering MS', '16287', 'Civil Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16288CWOG', 'A', 'Bioengineering CWO', '16288', 'Bioengineering', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16288JPHDG', 'A', 'Bioengineering Joint PhD', '16288', 'Bioengineering', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('16288MENGG', 'A', 'Bioengineering MEng', '16288', 'Bioengineering', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16290CSPPG', 'A', 'EECS MS-MPP CDP', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16290CWOG', 'A', 'Electrical Eng & Comp Sci CWO', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16290DENGG', 'A', 'Electrical Eng & Comp Sci DEng', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16290EEBAG', 'A', 'EECS MEng-MBA CDP', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16290MENGG', 'A', 'Electrical Eng & Comp Sci MEng', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16292CWOG', 'A', 'Industrial Eng & Ops Rsch CWO', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16292DENGG', 'A', 'Industrial Eng & Ops Rsch DEng', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16292IEPPG', 'A', 'IEOR MS-MPP CDP', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16293MSG', 'A', 'Materials Sci & Mineral Eng MS', '16293', 'Mat Sci & Mineral Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16293PHDG', 'A', 'Mat Sci & Mineral Eng PhD', '16293', 'Mat Sci & Mineral Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('162955YMSG', 'A', 'Mechanical Eng 5th Yr MS', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16295CPHLG', 'A', 'Mechanical Engineering CPhil', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('16295MEBAG', 'A', 'MechEng MEng-MBA CDP', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16295MENGG', 'A', 'Mechanical Engineering MEng', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16295PHDG', 'A', 'Mechanical Engineering PhD', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16296DENGG', 'A', 'Naval Architecture DEng', '16296', 'Naval Architecture', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16296MENGG', 'A', 'Naval Architecture MEng', '16296', 'Naval Architecture', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16298CWOG', 'A', 'Nuclear Engineering CWO', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16298MENGG', 'A', 'Nuclear Engineering MEng', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16298MSG', 'A', 'Nuclear Engineering MS', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16298NEPPG', 'A', 'Nuclear Eng MS-MPP CDP', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('162B3U', 'A', 'BioE/MSE Joint Major BS', '162B3', 'BioE/MSE Joint Major', 'MAJ', 'COEJNT', 'Engineering Joint Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162C0U', 'A', 'ME/NE Joint Major BS', '162C0', 'ME/NE Joint Major', 'MAJ', 'COEJNT', 'Engineering Joint Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162C6U', 'A', 'Energy Engineering BS', '162C6', 'Energy Engineering', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162C9MASG', 'A', 'Master of Adv Std - IC MAS', '162C9', 'Master of Adv Std - IC', 'SS', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '72', 'Master of Adv Study'),
('162D3MENGG', 'A', 'Bioengineering PT MEng', '162D3', 'Bioengineering PT MEng', 'SS', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162D5MENGG', 'A', 'El Eng & Comp Sci PT MEng', '162D5', 'El Eng & Comp Sci PT MEng', 'SS', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162D6MENGG', 'A', 'Ind Eng & Ops Rsch PT MEng', '162D6', 'Ind Eng & Ops Rsch PT MEng', 'SS', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162D8MENGG', 'A', 'Materials Sci & Eng PT MEng', '162D8', 'Materials Sci & Eng PT MEng', 'SS', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162E9CEPPG', 'A', 'Civil & Env Eng MS-MPP CDP', '162E9', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MS', 'Master of Science'),
('162E9MSP', 'A', 'Civil & Env Eng Prof MS', '162E9', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MS', 'Master of Science'),
('162G7MASG', 'A', 'Master of Adv Study Eng MAS', '162G7', 'Master of Adv Std Engineering', 'SS', 'AS-ENGIN', 'Advanced Study - Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '72', 'Master of Adv Study'),
('16300U', 'A', 'Civil Engineering BS', '16300', 'Civil Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16315U', 'A', 'Engineering Physics BS', '16315', 'Engineering Physics', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16324U', 'A', 'Industrial Eng & Ops Rsch BS', '16324', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('163285YMSG', 'A', 'Materials Sci & Eng 5th Yr MS', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16328CWOG', 'A', 'Materials Science & Eng CWO', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16328DENGG', 'A', 'Materials Science & Eng DEng', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16328MENGG', 'A', 'Materials Science & Eng MEng', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16328MSBAG', 'A', 'MatSciEng MEng-MBA CDP', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16328MSG', 'A', 'Materials Science & Eng MS', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16328PHDG', 'A', 'Materials Science & Eng PhD', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16342U', 'A', 'Nuclear Engineering BS', '16342', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16381U', 'A', 'Manufacturing Engineering BS', '16381', 'Manufacturing Engineering', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16649U', 'A', 'Earth Resources Eng BS', '16649', 'Earth Resources Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16A19U', 'I', 'MatSci Eng + BusAdm MET Pgm UG', '16A19', 'MatSci Eng + BusAdm MET Pgm', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A20U', 'I', 'Engin Und + BusAdm MET Pgm UG', '16A20', 'Engin Undec + BusAdm MET Pgm', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A22U', 'A', 'Aero Engin + BusAdm MET Pgm UG', '16A22', 'Aero Engin + BusAdm MET Pgm', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16I014U', 'A', 'Environmental Eng UG', '16MNRCIVENG', 'Civil & Env Engineering Minors', 'MIN', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I019U', 'A', 'Nuclear Engineering UG', '16MNRNUCENG', 'Nuclear Engineering Minors', 'MIN', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I020U', 'A', 'Structural Engineering UG', '16MNRCIVENG', 'Civil & Env Engineering Minors', 'MIN', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I101U', 'A', 'Civil & Environ Eng UG', '16MNRCIVENG', 'Civil & Env Engineering Minors', 'MIN', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I156U', 'A', 'Electronic Intelligent Sys UG', '16MNREECS', 'El Eng & Comp Sci Minors', 'MIN', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16V00U', 'A', 'Non-UC Campus Visitor COE UG', '16V00', 'Non-UC Campus Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V03U', 'A', 'UC Davis Visitor COE UG', '16V03', 'UC Davis Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V04U', 'A', 'UC Los Angeles Visitor COE UG', '16V04', 'UC Los Angeles Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V05ICVU', 'A', 'UC Riverside ICV COE UG', '16V05', 'UC Riverside Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V05U', 'A', 'UC Riverside Visitor COE UG', '16V05', 'UC Riverside Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V06ICVU', 'A', 'UC San Diego ICV COE UG', '16V06', 'UC San Diego Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V06U', 'A', 'UC San Diego Visitor COE UG', '16V06', 'UC San Diego Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V07ICVU', 'A', 'UC Santa Cruz ICV COE UG', '16V07', 'UC Santa Cruz Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V07U', 'A', 'UC Santa Cruz Visitor COE UG', '16V07', 'UC Santa Cruz Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V08ICVU', 'A', 'UC Santa Barbara ICV COE UG', '16V08', 'UC Santa Barbara Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V09U', 'A', 'UC Irvine Visitor COE UG', '16V09', 'UC Irvine Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V10U', 'A', 'UC Merced Visitor COE UG', '16V10', 'UC Merced Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19000U', 'A', 'Env Design Undeclared UG', '19000', 'Env Design Undeclared', 'MAJ', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'BACHL', 'Bachelor''s Degree'),
('19084MSG', 'A', 'Architecture MS', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('19084PHDG', 'A', 'Architecture PhD', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('19165CPARG', 'A', 'City & Reg Plan MCP-MArch CDP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165CPCEG', 'A', 'City & Reg Plan MCP-CEE MS CDP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165CPHLG', 'A', 'City & Regional Planning CPhil', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('19165CPHTG', 'A', 'City & Reg Plan MCP-UCH JD CDP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165CPJDG', 'A', 'City & Reg Plan MCP-JD CDP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165CPLAG', 'A', 'City & Reg Plan MCP-MLA CDP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165CPPHG', 'A', 'City & Reg Plan MCP-MPH CDP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165MCPG', 'A', 'City & Regional Planning MCP', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19165PHDG', 'A', 'City & Regional Planning PhD', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('19222CWOG', 'A', 'Design CWO', '19222', 'Design', 'MAJ', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('192F2ARCEG', 'A', 'Architecture MArch-CEE MS CDP', '192F2', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('192F2ARLAG', 'A', 'Architecture MArch-MLA CDP', '192F2', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('192F2MARCG', 'A', 'Architecture MArch', '192F2', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('192F3LACPG', 'A', 'Landscape Arch MLA-MCP CDP', '192F3', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '27', 'Master of Landscape Arch'),
('192F3MLAG', 'A', 'Landscape Architecture MLA', '192F3', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '27', 'Master of Landscape Arch'),
('192F5CPARG', 'A', 'City & Reg Plan MCP-MArch CDP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('192F5CPJDG', 'A', 'City & Reg Plan MCP-JD CDP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('192F5CPLAG', 'A', 'City & Reg Plan MCP-MLA CDP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('192F5CPPHG', 'A', 'City & Reg Plan MCP-MPH CDP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19340PHDG', 'A', 'Environmental Planning PhD', '19340', 'Environmental Planning', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('19489CWOG', 'A', 'Landscape Architecture CWO', '19489', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('19489LAARG', 'A', 'Landscape Arch MLA-MArch CDP', '19489', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '27', 'Master of Landscape Arch'),
('19489LACPG', 'A', 'Landscape Arch MLA-MCP CDP', '19489', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '27', 'Master of Landscape Arch'),
('19489MLAG', 'A', 'Landscape Architecture MLA', '19489', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '27', 'Master of Landscape Arch'),
('19489U', 'A', 'Landscape Architecture BA', '19489', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'AB', 'Bachelor of Arts'),
('194A9CPHLG', 'A', 'Landscp Arch & Env Plan CPhil', '194A9', 'Landscape Arch & Env Plan', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('194A9CWOG', 'A', 'Landscp Arch & Env Plan CWO', '194A9', 'Landscape Arch & Env Plan', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('194A9PHDG', 'A', 'Landscp Arch & Env Plan PhD', '194A9', 'Landscape Arch & Env Plan', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('19920CWOG', 'A', 'Urban Design CWO', '19920', 'Urban Design', 'MAJ', 'IURD', 'Institute of Urban & Regional Development Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('19920MUDG', 'A', 'Urban Design MUD', '19920', 'Urban Design', 'MAJ', 'IURD', 'Institute of Urban & Regional Development Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '39', 'Master of Urban Design'),
('19I022U', 'A', 'City & Regional Planning UG', '19MNRCYPLAN', 'City & Reg Planning Minors', 'MIN', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I023U', 'A', 'Env Dsgn & Urb Devl Coun UG', '19MNRARCH', 'Architecture Minors', 'MIN', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I024U', 'A', 'History & Theory of LAEP UG', '19MNRLAEP', 'Land Arch & Env Plan Minors', 'MIN', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I025U', 'A', 'History of Built Environ UG', '19MNRARCH', 'Architecture Minors', 'MIN', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I026U', 'A', 'Social Cultrl Factors ED UG', '19MNRARCH', 'Architecture Minors', 'MIN', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I027U', 'A', 'Sustainable Design UG', '19MNRLAEP', 'Land Arch & Env Plan Minors', 'MIN', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19INDU', 'A', 'CED Individual Major BA', '19451', 'CED Individual Major', 'MAJ', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'AB', 'Bachelor of Arts'),
('19V03ICVU', 'A', 'UC Davis ICV CED UG', '19V03', 'UC Davis Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V04ICVU', 'A', 'UC Los Angeles ICV CED UG', '19V04', 'UC Los Angeles Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V04U', 'A', 'UC Los Angeles Visitor CED UG', '19V04', 'UC Los Angeles Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V05U', 'A', 'UC Riverside Visitor CED UG', '19V05', 'UC Riverside Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V07ICVU', 'A', 'UC Santa Cruz ICV CED UG', '19V07', 'UC Santa Cruz Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V07U', 'A', 'UC Santa Cruz Visitor CED UG', '19V07', 'UC Santa Cruz Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V09ICVU', 'A', 'UC Irvine ICV CED UG', '19V09', 'UC Irvine Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V10U', 'A', 'UC Merced Visitor CED UG', '19V10', 'UC Merced Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25000MILLU', 'A', 'L&S UCB Changemaker Oakland UG', '25000', 'Letters & Sci Undeclared', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'BACHL', 'Bachelor''s Degree'),
('25000U', 'A', 'Letters & Sci Undeclared UG', '25000', 'Letters & Sci Undeclared', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'BACHL', 'Bachelor''s Degree'),
('25045U', 'A', 'American Studies BA', '25045', 'American Studies', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25072U', 'A', 'Applied Mathematics BA', '25072', 'Applied Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25095U', 'A', 'Asian Studies - China BA', '25095', 'Asian Studies - China', 'SP', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25096U', 'A', 'Asian Studies BA', '25096', 'Asian Studies', 'SP', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25098U', 'A', 'Asian Studies - SE Asia BA', '25098', 'Asian Studies - SE Asia', 'SP', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25099U', 'A', 'Astronomy BA', '25099', 'Astronomy', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('250AMU', 'A', 'Data Science BA', '250AM', 'L&S Data Science', 'MAJ', 'LSDATASCI', 'Letters & Science Data Science', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('250HDU', 'A', 'MELC Languages & Literature BA', '250HD', 'MELC Languages & Literature', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25101U', 'A', 'Astrophysics BA', '25101', 'Astrophysics', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25104U', 'A', 'Asian Studies-SE Asia BA', '25104', 'Asian Studies-SE Asia', 'SP', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25109U', 'A', 'BioSci-Functional Bio BA', '25109', 'BioSci-Functional Bio', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25110U', 'A', 'BioSci-System & Evol Bio BA', '25110', 'BioSci-System & Evol Bio', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25112U', 'A', 'BioSci-Ecology BA', '25112', 'BioSci-Ecology', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25113U', 'A', 'BioSci-Marine Biology BA', '25113', 'BioSci-Marine Biology', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25131U', 'A', 'Biophy-Med Phys BA', '25131', 'Biophy-Med Phys', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25160U', 'A', 'Chicano Studies BA', '25160', 'Chicano Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25171U', 'A', 'Classical Languages BA', '25171', 'Classical Languages', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('251A6U', 'A', 'Atmospheric Science BA', '251A6', 'Atmospheric Science', 'SP', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25201U', 'A', 'Computer Science BA', '25201', 'L&S Computer Science', 'MAJ', 'LSCS', 'Letters and Science Computer Science', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25238U', 'A', 'Development Studies BA', '25238', 'Development Studies', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252A1U', 'A', 'Dance & Perf Studies BA', '252A1', 'Dance & Perf Studies', 'MAJ', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252A9U', 'A', 'Media Studies BA', '252A9', 'Media Studies', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252B2U', 'A', 'Political Economy BA', '252B2', 'Political Economy', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252G5U', 'A', 'Chicanx Latinx Studies BA', '25160', 'Chicano Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25345U', 'A', 'English BA', '25345', 'English', 'MAJ', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25356U', 'A', 'Environmental Studies BA', '25356', 'L&S Environmental Studies', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25374U', 'A', 'Environ Sci-Biol Sci BA', '25374', 'Environ Sci-Biol Sci', 'SP', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25377U', 'A', 'Environ Sci-Soc Sci BA', '25377', 'Environ Sci-Soc Sci', 'SP', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25379U', 'A', 'Film and Media BA', '25379', 'Film', 'MAJ', 'FILM', 'Film and Media', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25396U', 'A', 'Geography BA', '25396', 'Geography', 'MAJ', 'GEOG', 'Geography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('253D2U', 'A', 'Ops Research & Mgmt Sci BA', '253D2', 'L&S Ops Research & Mgmt Sci', 'MAJ', 'LSORMS', 'Letters & Science Operations Research & Mgmt Sci', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25405U', 'A', 'Geophysics BA', '25405', 'Geophysics', 'SP', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25430U', 'A', 'History of Art BA', '25430', 'History of Art', 'MAJ', 'HISTART', 'History of Art', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25444U', 'A', 'Humanities Field Major BA', '25444', 'Humanities Field Major', 'MAJ', 'ARTHUMOTHS', 'Other Arts and Humanities Programs', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25469U', 'A', 'Chinese Language BA', '25469', 'Chinese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25470U', 'A', 'Japanese Language BA', '25470', 'Japanese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25479U', 'A', 'Italian Studies BA', '25479', 'Italian Studies', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25498U', 'A', 'Latin American Studies BA', '25498', 'Latin American Studies', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25510U', 'A', 'Linguistics BA', '25510', 'Linguistics', 'MAJ', 'LINGUIS', 'Linguistics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25535U', 'A', 'Marine Science BA', '25535', 'Marine Science', 'SP', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25539U', 'A', 'Mass Communications BA', '25539', 'Mass Communications', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25540U', 'A', 'Mathematics BA', '25540', 'Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25543U', 'A', 'Mathematics for Teachers BA', '25543', 'Mathematics for Teachers', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25552U', 'A', 'Medical Physics BA', '25552', 'Medical Physics', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25571U', 'A', 'Middle Eastern Studies BA', '25571', 'Middle Eastern Studies', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25587U', 'A', 'Native American Studies BA', '25587', 'Native American Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25588U', 'A', 'Near Eastern Lang & Lit BA', '25588', 'Near Eastern Lang & Lit', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25591U', 'A', 'Near Eastern Studies BA', '25591', 'Near Eastern Studies', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25593U', 'A', 'Neurobiology BA', '25593', 'Neurobiology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('255C1U', 'A', 'Near Eastern Civilizations BA', '255C1', 'Near Eastern Civilizations', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25641U', 'A', 'Human Biodynamics BA', '25641', 'Human Biodynamics', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25665U', 'A', 'Altaic Language BA', '25665', 'Altaic Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25666U', 'A', 'Physics BA', '25666', 'Physics', 'MAJ', 'PHYSICS', 'Physics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25699U', 'A', 'Political Science BA', '25699', 'Political Science', 'MAJ', 'POLSCI', 'Charles & Louise Travers Dept of Political Science', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25807U', 'A', 'Rhetoric BA', '25807', 'Rhetoric', 'MAJ', 'RHETOR', 'Rhetoric', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25834U', 'A', 'Scandinavian BA', '25834', 'Scandinavian', 'MAJ', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25849U', 'A', 'Slavic Lang & Lit BA', '25849', 'Slavic Lang & Lit', 'MAJ', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25866U', 'A', 'Spanish-Iberian Lang & Lit BA', '25866', 'Spanish-Iberian Lang & Lit', 'SP', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25867U', 'A', 'Sociology BA', '25867', 'Sociology', 'MAJ', 'SOCIOL', 'Sociology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25874U', 'A', 'Span-Luso-Brazil Lang & Lit BA', '25874', 'Spanish-Luso-Brazil Lang & Lit', 'SP', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25881U', 'A', 'Spanish and Portuguese BA', '25881', 'Spanish and Portuguese', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25919U', 'A', 'Span-Hisp Lang/Biling Iss BA', '25919', 'Spanish-Hisp Lang/Biling Iss', 'SP', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25960U', 'A', 'IB-Morph, Physio & Dev BA', '25960', 'IB-Morph, Physio & Dev', 'SP', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25961U', 'A', 'IB-Behavioral Biology BA', '25961', 'IB-Behavioral Biology', 'SP', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25962U', 'A', 'IB-SystBio/Paleo/Gen/Evol BA', '25962', 'IB-SystBio/Paleo/Gen/Evol', 'SP', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25964U', 'A', 'IB-Integrat Human Biology BA', '25964', 'IB-Integrat Human Biology', 'SP', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25965U', 'A', 'IB-General Integrat Biol BA', '25965', 'IB-General Integrat Biol', 'SP', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25966U', 'A', 'MCB-Biochem & Mol Biol BA', '25966', 'MCB-Biochem & Mol Biol', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25970U', 'A', 'MCB-Cell Physiology BA', '25970', 'MCB-Cell Physiology', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25974U', 'A', 'Molecular & Cell Biology BA', '25974', 'Molecular & Cell Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25975U', 'A', 'Integrative Biology BA', '25975', 'Integrative Biology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('259A2U', 'A', 'Theater & Perf Studies BA', '259A2', 'Theater & Perf Studies', 'MAJ', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25A01U', 'I', 'Intending Unspecified L&S UG', '25A01', 'Intending Unspecified L&S', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A05U', 'I', 'Intending Arts Hum/Soc Sci UG', '25A05', 'Intending Arts Hum/Soc Sci', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A10U', 'I', 'Undecided Math Physical Sci UG', '25A10', 'Undecided Math Physical Sci', 'MAJ', 'PHYSOTH', 'Other Math and Physical Sciences Programs', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A11U', 'I', 'Undecided Social Sciences UG', '25A11', 'Undecided Social Sciences', 'MAJ', 'SOCSCIOTHS', 'Other Social Sciences Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A12U', 'I', 'Undecided Undergrad Studies UG', '25A12', 'Undecided Undergrad Studies', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A13U', 'I', 'Undecided Arts & Humanities UG', '25A13', 'Undecided Arts & Humanities', 'MAJ', 'ARTHUMOTHS', 'Other Arts and Humanities Programs', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A14U', 'I', 'Intending Business Admin UG', '25A14', 'Intending Business Admin', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A15U', 'I', 'Haas Global Mgmt Program UG', '25A15', 'Haas Global Mgmt Program', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A18U', 'I', 'Biology + BusAdm Pgm UG', '25A18', 'Biology+Business Program', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25I029U', 'A', 'Arabic UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I032U', 'A', 'Buddhism UG', '25MNREALANG', 'East Asian Lang Culture Minors', 'MIN', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I035U', 'A', 'Classical Civilization UG', '25MNRCLASSIC', 'Classics Minors', 'MIN', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I037U', 'A', 'Dance & Performance Stds UG', '25MNRTHEATER', 'Theater Dance Perf Stds Minors', 'MIN', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I040U', 'A', 'French UG', '25MNRFRENCH', 'French Minors', 'MIN', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I043U', 'A', 'French Literature UG', '25MNRFRENCH', 'French Minors', 'MIN', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I044U', 'A', 'German UG', '25MNRGERMAN', 'German Minors', 'MIN', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I046U', 'A', 'Hebrew UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I049U', 'A', 'Japanese UG', '25MNREALANG', 'East Asian Lang Culture Minors', 'MIN', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I051U', 'A', 'Korean UG', '25MNREALANG', 'East Asian Lang Culture Minors', 'MIN', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I058U', 'A', 'Polish Language & Lit UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I059U', 'A', 'Rhetoric UG', '25MNRRHETOR', 'Rhetoric Minors', 'MIN', 'RHETOR', 'Rhetoric', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I062U', 'A', 'Russian Literature UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I063U', 'A', 'Scandinavian UG', '25MNRSCANDIN', 'Scandinavian Minors', 'MIN', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I065U', 'A', 'Spanish Lang, Lit & Culture UG', '25MNRSPANPOR', 'Spanish & Portuguese Minors', 'MIN', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I067U', 'A', 'Theater & Performance St UG', '25MNRTHEATER', 'Theater Dance Perf Stds Minors', 'MIN', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I068U', 'A', 'Turkish UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I070U', 'A', 'Earth & Planetary Sci UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I072U', 'A', 'Physics UG', '25MNRPHYSICS', 'Physics Minors', 'MIN', 'PHYSICS', 'Physics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I073U', 'A', 'Statistics UG', '25MNRSTAT', 'Statistics Minors', 'MIN', 'STAT', 'Statistics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I074U', 'A', 'African American Studies UG', '25MNRAFRICAM', 'African American Stds Minors', 'MIN', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I076U', 'A', 'Asian Am/Asn Diaspora St UG', '25MNRETHSTD', 'Ethnic Studies Minors', 'MIN', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I080U', 'A', 'Gender & Women''s Studies UG', '25MNRGWS', 'Gender & Womens Studies Minors', 'MIN', 'GWS', 'Gender and Womens Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I082U', 'A', 'History UG', '25MNRHISTORY', 'History Minors', 'MIN', 'HISTORY', 'History', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I085U', 'A', 'Linguistics UG', '25MNRLINGUIS', 'Linguistics Minors', 'MIN', 'LINGUIS', 'Linguistics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I086U', 'A', 'Native American Studies UG', '25MNRETHSTD', 'Ethnic Studies Minors', 'MIN', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I090U', 'A', 'Disability Studies UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I092U', 'A', 'Global Poverty & Prac UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I094U', 'A', 'Korean Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I095U', 'A', 'Middle Eastern Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I096U', 'A', 'Peace & Conflict Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I097U', 'A', 'Religious Studies UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I104U', 'A', 'East Asian Languages UG', '25MNREALANG', 'East Asian Lang Culture Minors', 'MIN', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I109U', 'A', 'Intl & Area Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I110U', 'A', 'Intl Envir Policy & Dev UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I116U', 'A', 'Applied Math UG', '25MNRMATH', 'Mathematics Minors', 'MIN', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I119U', 'A', 'Political Science UG', '25MNRPOLSCI', 'Political Science Minors', 'MIN', 'POLSCI', 'Charles & Louise Travers Dept of Political Science', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I123U', 'A', 'Political Economy UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I124U', 'A', 'Comparative Literature UG', '25MNRCOMLIT', 'Comparative Literature Minors', 'MIN', 'COMLIT', 'Comparative Literature', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I126U', 'A', 'Global Studies - Africa UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I128U', 'A', 'Global Studies - Americas UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I134U', 'A', 'Geophysics UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I136U', 'A', 'Planetary Science UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I138U', 'A', 'Logic UG', '25MNRPHILOS', 'Philosophy Minors', 'MIN', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I139U', 'A', 'American Literature UG', '25MNRENGLISH', 'English Minors', 'MIN', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I142U', 'A', 'Geographic Information Sys UG', '25MNRGEOG', 'Geography Minors', 'MIN', 'GEOG', 'Geography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I146U', 'A', 'Archaeology UG', '25MNRANTHRO', 'Anthropology Minors', 'MIN', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I150U', 'A', 'Buddhist Studies UG', '25MNRGGBUDST', 'Buddhist Studies Minors', 'MIN', 'GGBUDST', 'Buddhist Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I151U', 'A', 'Race and the Law UG', '25MNRSOCSCIOTHS', 'Other Social Sciences Minors', 'MIN', 'SOCSCIOTHS', 'Other Social Sciences Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I153U', 'A', 'Digital Humanities UG', '25MNRARTHUMOTHS', 'Other A&H Minors', 'MIN', 'ARTHUMOTHS', 'Other Arts and Humanities Programs', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I158U', 'A', 'Climate Science UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I161U', 'A', 'Politics, Philosophy, & Law UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I163U', 'A', 'Middle Eastern Lang & Cultr UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25V00U', 'A', 'Non-UC Campus Visitor L&S UG', '25V00', 'Non-UC Campus Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V02U', 'A', 'UC San Francisco Visitor LS UG', '25V02', 'UC San Francisco Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V03ICVU', 'A', 'UC Davis ICV L&S UG', '25V03', 'UC Davis Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V05ICVU', 'A', 'UC Riverside ICV L&S UG', '25V05', 'UC Riverside Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V06U', 'A', 'UC San Diego Visitor L&S UG', '25V06', 'UC San Diego Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V07ICVU', 'A', 'UC Santa Cruz ICV L&S UG', '25V07', 'UC Santa Cruz Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V08U', 'A', 'UC Santa Barbara Visitor LS UG', '25V08', 'UC Santa Barbara Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V10ICVU', 'A', 'UC Merced ICV L&S UG', '25V10', 'UC Merced Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V10U', 'A', 'UC Merced Visitor L&S UG', '25V10', 'UC Merced Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('30XCECCENX', 'A', 'UCBX Concurrent Enrollment', '30XCE', 'UCBX-Concurrent Enrollment', 'SS', 'UCBXCCEDPT', 'UCB Extension - Concurrent Enrollment Department', 'UCBXCCEDIV', 'UCB Extension - Concurrent Enrollment Division', 'UNEX', 'UC Berkeley Extension', 'UCBX', 'UC Berkeley Extension', 'XCCRT', 'UCBX Concurrent Enrollment', NULL, NULL),
('70008U', 'A', 'Business Limited UG', '70008', 'Business Limited', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('70141BAPHG', 'A', 'Business Admin MBA-MPH CDP', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('70141CWOG', 'A', 'Business Administration CWO', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('70141MBAG', 'A', 'Business Administration MBA', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('701F1MFE2G', 'A', 'Financial Engineering 2-Yr MFE', '701F1', 'Financial Engineering', 'SS', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '71', 'Master of Financial Eng'),
('701F1MFEG', 'A', 'Financial Engineering MFE', '701F1', 'Financial Engineering', 'SS', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '71', 'Master of Financial Eng'),
('702F7BAMEG', 'A', 'Business Admin MBA-MEng CDP', '702F7', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('702F7BAPHG', 'A', 'Business Admin MBA-MPH CDP', '702F7', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('702F7MBAG', 'A', 'Business Administration MBA', '702F7', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('70V00U', 'A', 'Non-UC Campus Visitor BUS UG', '70V00', 'Non-UC Campus Visitor BUS', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('71483CWOG', 'A', 'Journalism CWO', '71483', 'Journalism', 'MAJ', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('71483JNASG', 'A', 'Journalism MJ-Asian St MA CDP', '71483', 'Journalism', 'MAJ', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '25', 'Master of Journalism'),
('71483U', 'A', 'Journalism BA', '71483', 'Journalism', 'MAJ', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('71I121U', 'A', 'Journalism UG', '71MNRJOURN', 'Journalism Minors', 'MIN', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('79227JEDDG', 'A', 'Ed Leadership Joint Pgm EdD', '79227', 'Educational Leadership Jnt Pgm', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '96', 'Joint Doctor of Education'),
('79248C81G', 'A', 'Ed Cred Pgm Admin Prelim Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '81', 'Cert-Eductnl Admin Ser-Prelim'),
('79248C82G', 'A', 'Ed Cred Pgm Mult Subjects Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '82', 'Crtfct-Eductnl Multiple Subj'),
('79248C84G', 'A', 'Ed Cred Pgm Pupil Personl Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '84', 'Crtfct-Educational Pupil Per'),
('79248C88G', 'A', 'Ed Cred Pgm Reading Spec Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '88', 'Crtfct-Educational Read Spec'),
('79248C91G', 'A', 'Ed Cred Pgm Svr Hndc Spec Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '91', 'Crtfct-Severely Handicapped Sp'),
('79248C92G', 'A', 'Ed Cred Admin Prof Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '92', 'Cert-Eductnl Admin Ser-Profess'),
('79248C93G', 'A', 'Ed Cred Pgm Math Spec Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '93', 'Math Spec Credential'),
('79249C78G', 'A', 'Education Schl Psych Intn Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, '78', 'Credential-School Psych Intern'),
('79249C83G', 'A', 'Education Single Subject Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, '83', 'Crtfct-Educational Single Subj'),
('79249C88G', 'A', 'Education Reading Speclst Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '88', 'Crtfct-Educational Read Spec'),
('79249C90G', 'A', 'Learning Handicapped Spec Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '90', 'Crtfct-Learning Handicapped Sp'),
('79249C92G', 'A', 'Education Admin Prof Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '92', 'Cert-Eductnl Admin Ser-Profess'),
('79249CWOG', 'A', 'Education CWO', '79249', 'Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('79249MAG', 'A', 'Education MA', '79249', 'Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('79249MATG', 'A', 'Education MAT', '79249', 'Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '11', 'Master of Arts in Teaching'),
('79249PHDG', 'A', 'Education PhD', '79249', 'Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('79892CWOG', 'A', 'Special Ed Joint Pgm CWO', '79892', 'Special Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('79892JEDDG', 'A', 'Special Ed Joint Pgm EdD', '79892', 'Special Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '96', 'Joint Doctor of Education'),
('79892MAG', 'A', 'Special Education MA', '79892', 'Special Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('799A4MAG', 'A', 'Teacher Education MA', '799A4', 'Teacher Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MA', 'Master of Arts'),
('79I098U', 'A', 'Education UG', '79MNREDUC', 'Education Minors', 'MIN', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('79I099U', 'A', 'CalTeach Sci & Math Edu UG', '25MNRPHYSOTH', 'Other MPS Pgms Minors', 'MIN', 'PHYSOTH', 'Other Math and Physical Sciences Programs', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('810DHMICSG', 'A', 'Info & Cyber Security MICS', '810DH', 'Master of Info & Cybersecurity', 'SS', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'IC', 'Master of Info & CyberSecurity'),
('812E05YMIG', 'A', 'Info & Data Sci 5th Yr MIDS', '812E0', 'Info & Data Science-MIDS', 'SS', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '99', 'Master of Info & Data Science'),
('81504DLSG', 'A', 'Library & Info Studies DLS', '81504', 'Library & Info Studies', 'MAJ', 'LINFOST', 'Library and Information Studies', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '58', 'Doctor of Lib & Info Studies'),
('81504MLSG', 'A', 'Library & Info Studies MLS', '81504', 'Library & Info Studies', 'MAJ', 'LINFOST', 'Library and Information Studies', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '29', 'Master of Libr & Info Studies'),
('81504PHDG', 'A', 'Library & Info Studies PhD', '81504', 'Library & Info Studies', 'MAJ', 'LINFOST', 'Library and Information Studies', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('81776MIMSG', 'A', 'Info Mgmt & Systems MIMS', '81776', 'Info Mgmt & Systems', 'MAJ', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '40', 'Master of Info Mgmt & Systems'),
('82790PHDG', 'A', 'Public Policy PhD', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('82790PPCEG', 'A', 'Public Policy MPP-CEE MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPCSG', 'A', 'Public Policy MPP-EECS MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPEAG', 'A', 'Public Policy MPP-ERG MA CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPESG', 'A', 'Public Policy MPP-ERG MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPJDG', 'A', 'Public Policy MPP-JD CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPMSG', 'A', 'Public Policy MPP-MSE MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPNEG', 'A', 'Pub Policy MPP-Nuc Eng MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('842C1JSDG', 'A', 'Doctor of Science of Law JSD', '842C1', 'Doctor of Science of Law (JSD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', '69', 'Juris Scientiae Doctor'),
('84485CPHLG', 'A', 'JSP CPhil', '84485', 'Jurisprudence & Social Policy', 'MAJ', 'GGJSP', 'Jurisprudence and Social Policy Graduate Program', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', '48', 'Candidate in Philosophy'),
('84485LLMG', 'A', 'JSP LLM', '84485', 'Jurisprudence & Social Policy', 'MAJ', 'GGJSP', 'Jurisprudence and Social Policy Graduate Program', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', '28', 'Master of Laws'),
('84485PHDG', 'A', 'JSP PhD', '84485', 'Jurisprudence & Social Policy', 'MAJ', 'GGJSP', 'Jurisprudence and Social Policy Graduate Program', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', 'PD', 'Doctor of Philosophy'),
('84501JDBAG', 'A', 'Law JD-MBA CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDECG', 'A', 'Law JD-Econ MA CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDESG', 'A', 'Law JD-Energy & Res MS CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDG', 'A', 'Law JD', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDJPG', 'A', 'Law JD-JSP CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDSWG', 'A', 'Law JD-MSW CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501PHDG', 'A', 'Law PhD', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', 'PD', 'Doctor of Philosophy'),
('845B0HLLMG', 'A', 'LL.M. Executive Track', '845B0', 'Master of Laws (LLM)', 'SS', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LSSDP', 'Law Self-Supporting Programs', '28', 'Master of Laws'),
('845B0LLMG', 'A', 'Master of Laws LLM', '845B0', 'Master of Laws (LLM)', 'SS', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LSSDP', 'Law Self-Supporting Programs', '28', 'Master of Laws'),
('845B0SLLMG', 'A', 'LLM Executive Track', '845B0', 'Master of Laws (LLM)', 'SS', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LSSDP', 'Law Self-Supporting Programs', '28', 'Master of Laws'),
('84V00G', 'A', 'Law Non-UC Campus Visitor GR', '84V00', 'Non-UC Campus Visitor Law', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'LAW', 'Law', 'LNODG', 'Law Non-Degree/Non-FinAid', NULL, NULL),
('860EZFSWEG', 'A', 'Flex MSW - Extended', '860EZ', 'Flexible Master of Soc Welfare', 'SS', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '38', 'Master of Social Welfare'),
('86864CWOG', 'A', 'Social Welfare CWO', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('86864MSWG', 'A', 'Social Welfare MSW', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '38', 'Master of Social Welfare'),
('86864PHDG', 'A', 'Social Welfare PhD', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('86864SWPHG', 'A', 'Social Welfare MSW-MPH CDP', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '38', 'Master of Social Welfare'),
('86864SWPPG', 'A', 'Social Welfare MSW-MPP CDP', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '38', 'Master of Social Welfare'),
('91612CWOG', 'A', 'Optometry CWO', '91612', 'Optometry', 'HS', 'OPTOMDPT', 'Optometry', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('91612U4U', 'A', 'Optometry-Second Bachelors OD', '91612', 'Optometry', 'HS', 'OPTOMDPT', 'Optometry', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'UGRD', 'Undergraduate', 'UOPTM', 'Undergrad Optometry', '62', 'Doctor of Optometry'),
('91672MSG', 'A', 'Physiological Optics MS', '91672', 'Physiological Optics', 'HS', 'GGVISCI', 'Vision Science Graduate Group', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('91672PHDG', 'A', 'Physiological Optics PhD', '91672', 'Physiological Optics', 'HS', 'GGVISCI', 'Vision Science Graduate Group', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('91935PHDG', 'A', 'Vision Science PhD', '91935', 'Vision Science', 'MAJ', 'GGVISCI', 'Vision Science Graduate Group', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('96132MAG', 'A', 'Biostatistics MA', '96132', 'Biostatistics', 'HS', 'GGBSTAT', 'Biostatistics Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('96132PHDG', 'A', 'Biostatistics PhD', '96132', 'Biostatistics', 'HS', 'GGBSTAT', 'Biostatistics Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('962C4MPHG', 'A', 'On-Campus/Online Prfsnl MPH', '962C4', 'On-Campus/Online Prfsnl MPH', 'SS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '36', 'Master of Public Health'),
('96354PHDG', 'A', 'Environ Health Sciences PhD', '96354', 'Environ Health Sciences', 'HS', 'GGEHS', 'Environmental Health Sciences Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('96447PHDG', 'A', 'Immunology PhD', '96447', 'Immunology', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('96570MAG', 'A', 'Microbiology MA', '96570', 'SPH Microbiology', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('96630PHDG', 'A', 'Parasitology PhD', '96630', 'Parasitology', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('96789PHBAG', 'A', 'Public Health MPH-MBA CDP', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96789PHCPG', 'A', 'Public Health MPH-MCP CDP', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96789PHJNG', 'A', 'Public Health MPH-Journ MJ CDP', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96I118U', 'A', 'Public Health UG', '96MNRPUBHEALTH', 'Public Health Minors', 'MIN', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('96I137U', 'A', 'Global Public Health UG', '96MNRPUBHEALTH', 'Public Health Minors', 'MIN', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('99V02G', 'A', 'Summer UC San Francisco Vis GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V03G', 'A', 'Summer UC Davis Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V05G', 'A', 'Summer UC Riverside Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V05U', 'A', 'Summer UC Riverside Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V06G', 'A', 'Summer UC San Diego Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V07G', 'A', 'Summer UC Santa Cruz Vis GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V07U', 'A', 'Summer UC Santa Cruz Vis UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V08G', 'A', 'Summer UC Santa Barbara Vis GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V10G', 'A', 'Summer UC Merced Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('A50AMU', 'A', 'Data Science BA', NULL, NULL, 'MAJ', NULL, NULL, NULL, NULL, NULL, NULL, 'UGRD', 'Undergraduate', 'UCDSS', 'Undergrad Comp Data Sci & Soc', 'AB', 'Bachelor of Arts'),
('00000G', 'A', 'Grad Division Undeclared GR', '00000', 'Grad Division Undeclared', 'MAJ', 'GRADDIVOTH', 'Graduate Division Other Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00048MAG', 'A', 'Anatomy MA', '00048', 'Anatomy', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00048PHDG', 'A', 'Anatomy PhD', '00048', 'Anatomy', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00059MAG', 'A', 'International & Area Stds MA', '00059', 'International & Area Stds', 'MAJ', 'GGIAS', 'Global Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00063CPHLG', 'A', 'Anthropology CPhil', '00063', 'Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00063PHDG', 'A', 'Anthropology PhD', '00063', 'Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00072CPHLG', 'A', 'Applied Mathematics CPhil', '00072', 'Applied Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00072CWOG', 'A', 'Applied Mathematics CWO', '00072', 'Applied Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('000865YMSG', 'A', 'Applied Sci & Tech 5th Yr MS', '00086', 'Applied Science & Tech', 'MAJ', 'GGAST', 'Applied Science and Technology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00086CWOG', 'A', 'Applied Science & Tech CWO', '00086', 'Applied Science & Tech', 'MAJ', 'GGAST', 'Applied Science and Technology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00086MSG', 'A', 'Applied Science & Tech MS', '00086', 'Applied Science & Tech', 'MAJ', 'GGAST', 'Applied Science and Technology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00090MAG', 'A', 'Art MA', '00090', 'Art', 'MAJ', 'ART', 'Art Practice', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00090MFARG', 'A', 'Art MFA', '00090', 'Art', 'MAJ', 'ART', 'Art Practice', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '22', 'Master of Fine Arts'),
('00096ASJDG', 'A', 'Asian Studies MA-JD CDP', '00096', 'Asian Studies', 'MAJ', 'GGASNST', 'Asian Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00096ASJNG', 'A', 'Asian St MA-Journalism MJ CDP', '00096', 'Asian Studies', 'MAJ', 'GGASNST', 'Asian Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00096CWOG', 'A', 'Asian Studies CWO', '00096', 'Asian Studies', 'MAJ', 'GGASNST', 'Asian Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00096MAG', 'A', 'Asian Studies MA', '00096', 'Asian Studies', 'MAJ', 'GGASNST', 'Asian Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00099MAG', 'A', 'Astronomy MA', '00099', 'Astronomy', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00099MSG', 'A', 'Astronomy MS', '00099', 'Astronomy', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('000HIMCSSG', 'A', 'Comp Social Science MCSS', '000HI', 'Computational Social Science', 'SS', 'GGCPSOCSCI', 'Computational Social Science Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'C6', 'Master of Comp Social Science'),
('00101PHDG', 'A', 'Astrophysics PhD', '00101', 'Astrophysics', 'MAJ', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('0010KPHDG', 'A', 'Medieval Studies Concrnt PhD', '0010K', 'Medieval Studies', 'MAJ', 'GGMEDST', 'Medieval Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00126MAG', 'A', 'Biophysics MA', '00126', 'Biophysics', 'MAJ', 'GGBIOPH', 'Biophysics Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00126PHDG', 'A', 'Biophysics PhD', '00126', 'Biophysics', 'MAJ', 'GGBIOPH', 'Biophysics Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00139PHDG', 'A', 'Buddhist Studies PhD', '00139', 'Buddhist Studies', 'MAJ', 'GGBUDST', 'Buddhist Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00168CPHLG', 'A', 'Classical Archaeology CPhil', '00168', 'Classical Archaeology', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00168CWOG', 'A', 'Classical Archaeology CWO', '00168', 'Classical Archaeology', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00168MAG', 'A', 'Classical Archaeology MA', '00168', 'Classical Archaeology', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00168PHDG', 'A', 'Classical Archaeology PhD', '00168', 'Classical Archaeology', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00192CWOG', 'A', 'Comparative Literature CWO', '00192', 'Comparative Literature', 'MAJ', 'COMLIT', 'Comparative Literature', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00207MCG', 'A', 'Criminology MC', '00207', 'Criminology', 'MAJ', 'GRADDIVOTH', 'Graduate Division Other Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '18', 'Master of Criminology'),
('00213MAG', 'A', 'Demography MA', '00213', 'Demography', 'MAJ', 'DEMOG', 'Demography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00213PHDG', 'A', 'Demography PhD', '00213', 'Demography', 'MAJ', 'DEMOG', 'Demography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00234CPHLG', 'A', 'Dramatic Art CPhil', '00234', 'Dramatic Art', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00234MAG', 'A', 'Dramatic Art MA', '00234', 'Dramatic Art', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00234PHDG', 'A', 'Dramatic Art PhD', '00234', 'Dramatic Art', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00239ESJDG', 'A', 'Energy & Res MS-JD CDP', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00239MSG', 'A', 'Energy & Resources MS', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00239PHDG', 'A', 'Energy & Resources PhD', '00239', 'Energy & Resources', 'MAJ', 'GGERG', 'Energy & Resources Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00246CWOG', 'A', 'Economics CWO', '00246', 'Economics', 'MAJ', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00270CWOG', 'A', 'Endocrinology CWO', '00270', 'Endocrinology', 'MAJ', 'GGENDOC', 'Endocrinology Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00270MAG', 'A', 'Endocrinology MA', '00270', 'Endocrinology', 'MAJ', 'GGENDOC', 'Endocrinology Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00270PHDG', 'A', 'Endocrinology PhD', '00270', 'Endocrinology', 'MAJ', 'GGENDOC', 'Endocrinology Graduate Group', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00288JMSG', 'A', 'Bioengineering UCSF Joint MS', '00288', 'Bioengineering (UCSF)', 'MAJ', 'GGBIOENG', 'Bioengineering-UCSF Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '94', 'Joint Master of Science'),
('00288JPHDG', 'A', 'Bioengineering UCSF Joint PhD', '00288', 'Bioengineering (UCSF)', 'MAJ', 'GGBIOENG', 'Bioengineering-UCSF Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('002A4MAG', 'A', 'Earth & Planetary Science MA', '002A4', 'Earth & Planetary Science', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('002A4PHDG', 'A', 'Earth & Planetary Science PhD', '002A4', 'Earth & Planetary Science', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002A5CWOG', 'A', 'Sociology & Demography CWO', '002A5', 'Sociology & Demography', 'MAJ', 'GGSODEJ', 'Sociology and Demography Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002A6MSG', 'A', 'Molecular & Biochem Nutr MS', '002A6', 'Molecular & Biochem Nutrition', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('002A6PHDG', 'A', 'Molecular & Biochem Nutr PhD', '002A6', 'Molecular & Biochem Nutrition', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002C3CWOG', 'A', 'Film and Media CWO', '002C3', 'Film and Media', 'MAJ', 'FILM', 'Film and Media', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002C3MAG', 'A', 'Film and Media MA', '002C3', 'Film and Media', 'MAJ', 'FILM', 'Film and Media', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('002C8MTMG', 'A', 'Translatnl Medicine UCSF MTM', '002C8', 'Translational Medicine (UCSF)', 'MAJ', 'GGBIOENG', 'Bioengineering-UCSF Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '98', 'Master of Translational Med'),
('002D0CPHLG', 'A', 'Metabolic Biology CPhil', '002D0', 'Metabolic Biology', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('002D0MSG', 'A', 'Metabolic Biology MS', '002D0', 'Metabolic Biology', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('002D0PHDG', 'A', 'Metabolic Biology PhD', '002D0', 'Metabolic Biology', 'MAJ', 'GGMBBIO', 'Metabolic Biology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002E3CWOG', 'A', 'Health Policy CWO', '002E3', 'Health Policy', 'HS', 'GGHSPA', 'Health Policy Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('002E3PHDG', 'A', 'Health Policy PhD', '002E3', 'Health Policy', 'HS', 'GGHSPA', 'Health Policy Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002G2MDEG', 'A', 'Development Engineering MDE', '002G2', 'Development Engineering', 'SS', 'GGDEVEN', 'Development Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'B8', 'Master of Dev Engineering'),
('002G6PHDG', 'A', 'Middle Eastern Lang & Cul PhD', '002G6', 'Middle Eastern Lang & Cultures', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('002G9MBTG', 'A', 'Biotechnology M.Biotech', '002G9', 'Master of Biotechnology', 'SS', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'C8', 'Master of Biotechnology'),
('00345CPHLG', 'A', 'English CPhil', '00345', 'English', 'MAJ', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00345CWOG', 'A', 'English CWO', '00345', 'English', 'MAJ', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00345MAG', 'A', 'English MA', '00345', 'English', 'MAJ', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00345MATG', 'A', 'English MAT', '00345', 'English', 'MAJ', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '11', 'Master of Arts in Teaching'),
('00345PHDG', 'A', 'English PhD', '00345', 'English', 'MAJ', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00360CPHLG', 'A', 'Ethnic Studies CPhil', '00360', 'Ethnic Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00360PHDG', 'A', 'Ethnic Studies PhD', '00360', 'Ethnic Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00366CWOG', 'A', 'Folklore CWO', '00366', 'Folklore', 'MAJ', 'GGFOLK', 'Folklore Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00368CWOG', 'A', 'Molecular Toxicology CWO', '00368', 'Molecular Toxicology', 'MAJ', 'GGMTOX', 'Molecular Toxicology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00368MSG', 'A', 'Molecular Toxicology MS', '00368', 'Molecular Toxicology', 'MAJ', 'GGMTOX', 'Molecular Toxicology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00368PHDG', 'A', 'Molecular Toxicology PhD', '00368', 'Molecular Toxicology', 'MAJ', 'GGMTOX', 'Molecular Toxicology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00387MAG', 'A', 'French MA', '00387', 'French', 'MAJ', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00387PHDG', 'A', 'French PhD', '00387', 'French', 'MAJ', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00396CWOG', 'A', 'Geography CWO', '00396', 'Geography', 'MAJ', 'GEOG', 'Geography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00396PHDG', 'A', 'Geography PhD', '00396', 'Geography', 'MAJ', 'GEOG', 'Geography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00402MAG', 'A', 'Geology MA', '00402', 'Geology', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00402MSG', 'A', 'Geology MS', '00402', 'Geology', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00405MAG', 'A', 'Geophysics MA', '00405', 'Geophysics', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00405PHDG', 'A', 'Geophysics PhD', '00405', 'Geophysics', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00408CPHLG', 'A', 'German CPhil', '00408', 'German', 'MAJ', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00408MAG', 'A', 'German MA', '00408', 'German', 'MAJ', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00408PHDG', 'A', 'German PhD', '00408', 'German', 'MAJ', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00424MSG', 'A', 'Health & Medical Sciences MS', '00424', 'Health & Medical Sciences', 'HS', 'GGHMS', 'Health and Medical Sciences Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MS', 'Master of Science'),
('00425PHDG', 'A', 'Hispanic Lang & Lit PhD', '00425', 'Hispanic Lang & Lit', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00428CWOG', 'A', 'Hlth Serv & Pol Analysis CWO', '00428', 'Hlth Servs & Pol Analysis', 'HS', 'GGHSPA', 'Health Policy Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00429PHDG', 'A', 'History PhD', '00429', 'History', 'MAJ', 'HISTORY', 'History', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00430CWOG', 'A', 'History of Art CWO', '00430', 'History of Art', 'MAJ', 'HISTART', 'History of Art', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00430MAG', 'A', 'History of Art MA', '00430', 'History of Art', 'MAJ', 'HISTART', 'History of Art', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00430PHDG', 'A', 'History of Art PhD', '00430', 'History of Art', 'MAJ', 'HISTART', 'History of Art', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00469CWOG', 'A', 'Chinese Language CWO', '00469', 'Chinese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00470CWOG', 'A', 'Japanese Language CWO', '00470', 'Japanese Language', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00479CPHLG', 'A', 'Italian Studies CPhil', '00479', 'Italian Studies', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00479CWOG', 'A', 'Italian Studies CWO', '00479', 'Italian Studies', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00479MAG', 'A', 'Italian Studies MA', '00479', 'Italian Studies', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00479PHDG', 'A', 'Italian Studies PhD', '00479', 'Italian Studies', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00482CPHLG', 'A', 'Jewish Studies Joint Pgm CPhil', '00482', 'Jewish Studies', 'MAJ', 'GGJWST', 'Jewish Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00482CWOG', 'A', 'Jewish Studies Joint Pgm CWO', '00482', 'Jewish Studies', 'MAJ', 'GGJWST', 'Jewish Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00482JPHDG', 'A', 'Jewish Studies Joint Pgm PhD', '00482', 'Jewish Studies', 'MAJ', 'GGJWST', 'Jewish Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('00492CWOG', 'A', 'Global Studies CWO', '00492', 'Global Studies', 'MAJ', 'GGIAS', 'Global Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00498MAG', 'A', 'Latin American Studies MA', '00498', 'Latin American Studies', 'MAJ', 'GGLTAMS', 'Latin American Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00498PHDG', 'A', 'Latin American Studies PhD', '00498', 'Latin American Studies', 'MAJ', 'GGLTAMS', 'Latin American Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00510CPHLG', 'A', 'Linguistics CPhil', '00510', 'Linguistics', 'MAJ', 'LINGUIS', 'Linguistics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00510CWOG', 'A', 'Linguistics CWO', '00510', 'Linguistics', 'MAJ', 'LINGUIS', 'Linguistics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00531CPHLG', 'A', 'Logic/Methodology of Sci CPhil', '00531', 'Logic/Methodology of Science', 'MAJ', 'GGLOGIC', 'Logic and the Methodology of Science Graduate Grp', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00531CWOG', 'A', 'Logic/Methodology of Sci CWO', '00531', 'Logic/Methodology of Science', 'MAJ', 'GGLOGIC', 'Logic and the Methodology of Science Graduate Grp', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00531PHDG', 'A', 'Logic/Methodology of Sci PhD', '00531', 'Logic/Methodology of Science', 'MAJ', 'GGLOGIC', 'Logic and the Methodology of Science Graduate Grp', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00540CPHLG', 'A', 'Mathematics CPhil', '00540', 'Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00540CWOG', 'A', 'Mathematics CWO', '00540', 'Mathematics', 'MAJ', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00553MAG', 'A', 'Medical Anthropology MA', '00553', 'Medical Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00570CPHLG', 'A', 'Microbiology CPhil', '00570', 'Microbiology', 'MAJ', 'GGMICRO', 'Microbiology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00570MAG', 'A', 'Microbiology MA', '00570', 'Microbiology', 'MAJ', 'GGMICRO', 'Microbiology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00573MAG', 'A', 'Molecular Biology MA', '00573', 'Molecular Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00573PHDG', 'A', 'Molecular Biology PhD', '00573', 'Molecular Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00579CWOG', 'A', 'Music CWO', '00579', 'Music', 'MAJ', 'MUSIC', 'Music', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00591MAG', 'A', 'Near Eastern Studies MA', '00591', 'Near Eastern Studies', 'MAJ', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00593MAG', 'A', 'Neurobiology MA', '00593', 'Neurobiology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00594CWOG', 'A', 'Neuroscience CWO', '00594', 'Neuroscience', 'MAJ', 'HWNI', 'Neuroscience Graduate Program', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00594PHDG', 'A', 'Neuroscience PhD', '00594', 'Neuroscience', 'MAJ', 'HWNI', 'Neuroscience Graduate Program', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('005C3JMSG', 'A', 'Comp Precision Health Jt MS', '005C3', 'Comp Precision Health', 'HS', 'GGCPHLTH', 'Computational Precision Health Graduate Group', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '94', 'Joint Master of Science'),
('00621PHDG', 'A', 'East Asian Languages PhD', '00621', 'East Asian Languages', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00627CPHLG', 'A', 'Paleontology CPhil', '00627', 'Paleontology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00627MAG', 'A', 'Paleontology MA', '00627', 'Paleontology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00651CPHLG', 'A', 'Philosophy CPhil', '00651', 'Philosophy', 'MAJ', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00651MAG', 'A', 'Philosophy MA', '00651', 'Philosophy', 'MAJ', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00654CPHLG', 'A', 'Physical Education CPhil', '00654', 'Physical Education', 'MAJ', 'PHYSED', 'Physical Education', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00654PHDG', 'A', 'Physical Education PhD', '00654', 'Physical Education', 'MAJ', 'PHYSED', 'Physical Education', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00675MAG', 'A', 'Physiology MA', '00675', 'Physiology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00675PHDG', 'A', 'Physiology PhD', '00675', 'Physiology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00699CPHLG', 'A', 'Political Science CPhil', '00699', 'Political Science', 'MAJ', 'POLSCI', 'Charles & Louise Travers Dept of Political Science', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00699MAG', 'A', 'Political Science MA', '00699', 'Political Science', 'MAJ', 'POLSCI', 'Charles & Louise Travers Dept of Political Science', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00780CWOG', 'A', 'Psychology CWO', '00780', 'Psychology', 'MAJ', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00780PHDG', 'A', 'Psychology PhD', '00780', 'Psychology', 'MAJ', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00807MAG', 'A', 'Rhetoric MA', '00807', 'Rhetoric', 'MAJ', 'RHETOR', 'Rhetoric', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00807PHDG', 'A', 'Rhetoric PhD', '00807', 'Rhetoric', 'MAJ', 'RHETOR', 'Rhetoric', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00812CPHLG', 'A', 'Romance Lang & Lit CPhil', '00812', 'Romance Lang & Lit', 'MAJ', 'GGRLL', 'Romance Languages & Literatures Graduate Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00816PHDG', 'A', 'Romance Philology PhD', '00816', 'Romance Philology', 'MAJ', 'GGRLL', 'Romance Languages & Literatures Graduate Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00843PHDG', 'A', 'Science & Math Education PhD', '00843', 'Science & Math Education', 'MAJ', 'GGSME', 'Science and Mathematics Education Graduate Group', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00849CWOG', 'A', 'Slavic Lang & Lit CWO', '00849', 'Slavic Lang & Lit', 'MAJ', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00867MAG', 'A', 'Sociology MA', '00867', 'Sociology', 'MAJ', 'SOCIOL', 'Sociology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00877CWOG', 'A', 'South & SE Asian Studies CWO', '00877', 'South & SE Asian Studies', 'MAJ', 'SSEASN', 'South and Southeast Asian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00877MAG', 'A', 'South & SE Asian Studies MA', '00877', 'South & SE Asian Studies', 'MAJ', 'SSEASN', 'South and Southeast Asian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00882CWOG', 'A', 'Spanish CWO', '00882', 'Spanish', 'MAJ', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00891CPHLG', 'A', 'Statistics CPhil', '00891', 'Statistics', 'MAJ', 'STAT', 'Statistics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00891MAG', 'A', 'Statistics MA', '00891', 'Statistics', 'MAJ', 'STAT', 'Statistics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MA', 'Master of Arts'),
('00891PHDG', 'A', 'Statistics PhD', '00891', 'Statistics', 'MAJ', 'STAT', 'Statistics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00933CPHLG', 'A', 'Zoology CPhil', '00933', 'Zoology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00933PHDG', 'A', 'Zoology PhD', '00933', 'Zoology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00974CWOG', 'A', 'Molecular & Cell Biology CWO', '00974', 'Molecular & Cell Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00975CPHLG', 'A', 'Integrative Biology CPhil', '00975', 'Integrative Biology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00975MAG', 'A', 'Integrative Biology MA', '00975', 'Integrative Biology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('00975PHDG', 'A', 'Integrative Biology PhD', '00975', 'Integrative Biology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('009B2PHDG', 'A', 'Performance Studies PhD', '009B2', 'Performance Studies', 'MAJ', 'GGPERST', 'Performance Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('00E001G', 'A', 'Comm Computation and Stats DE', '00E001', 'Comm Computation and Stats DE', 'DE', 'GGCCS', 'Communication, Computation, & Statistics Grad Grp', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E002G', 'A', 'Comp and Genomic Biology DE', '00E002', 'Comp and Genomic Biology DE', 'DE', 'GGCPBIO', 'Computational Biology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E003G', 'A', 'Comp & Data Sci & Engin DE', '00E003', 'Computational Sci Engr DE', 'DE', 'GGCSE', 'Comp & Data Science & Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E004G', 'A', 'Critical Theory DE', '00E004', 'Critical Theory DE', 'DE', 'GGCRITH', 'Critical Theory Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E005L', 'A', 'Development Engineering DE', '00E005', 'Development Engineering DE', 'DE', 'GGDEVEN', 'Development Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E006L', 'A', 'Dutch Studies DE', '00E006', 'Dutch Studies DE', 'DE', 'GGDUTCH', 'Dutch Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E007G', 'A', 'Energy Sci and Technology DE', '00E007', 'Energy Sci and Technology DE', 'DE', 'GGEST', 'Energy Science & Technology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E007L', 'A', 'Energy Sci and Technology DE', '00E007', 'Energy Sci and Technology DE', 'DE', 'GGEST', 'Energy Science & Technology Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E009G', 'A', 'Folklore DE', '00E009', 'Folklore DE', 'DE', 'GGFOLK', 'Folklore Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E009L', 'A', 'Folklore DE', '00E009', 'Folklore DE', 'DE', 'GGFOLK', 'Folklore Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E010L', 'A', 'Global Metropolitan Studies DE', '00E010', 'Global Metropolitan Studies DE', 'DE', 'GGGMS', 'Global Metropolitan Studies Graduate Group', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E011G', 'A', 'Jewish Studies DE', '00E011', 'Jewish Studies DE', 'DE', 'GGJWST', 'Jewish Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E011L', 'A', 'Jewish Studies DE', '00E011', 'Jewish Studies DE', 'DE', 'GGJWST', 'Jewish Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E013L', 'A', 'Nanoscale Sci and Engr DE', '00E013', 'Nanoscale Sci and Engr DE', 'DE', 'GGNANO', 'Nanoscale Science and Engineering Graduate Group', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E015G', 'A', 'Ren and Early Modern Stds DE', '00E015', 'Ren and Early Modern Stds DE', 'DE', 'GGREMS', 'Renaissance & Early Modern Studies Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E016L', 'A', 'Science and Technology Stds DE', '00E016', 'Science and Technology Stds DE', 'DE', 'GGSTS', 'Science and Technology Studies Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E017G', 'A', 'Women, Gender and Sexuality DE', '00E017', 'Women, Gender and Sexuality DE', 'DE', 'GGWGS', 'Women, Gender, & Sexuality Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E017L', 'A', 'Women, Gender and Sexuality DE', '00E017', 'Women, Gender and Sexuality DE', 'DE', 'GGWGS', 'Women, Gender, & Sexuality Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', NULL, NULL),
('00E018G', 'A', 'European Studies DE', '00E018', 'European Studies DE', 'DE', 'GGEUROST', 'European Studies Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E019G', 'A', 'Indigenous Lang Revital DE', '00E019', 'Indigenous Language Revive DE', 'DE', 'GGILR', 'Indigenous Language Revitalization Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E019L', 'A', 'Indigenous Lang Revital DE', '00E019', 'Indigenous Language Revive DE', 'DE', 'GGILR', 'Indigenous Language Revitalization Graduate Group', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'LAW', 'Law', NULL, NULL, NULL, NULL),
('00E021G', 'A', 'Study of Religion DE', '00E021', 'Study of Religion DE', 'DE', 'GGSR', 'Study of Religion Graduate Group', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E024G', 'A', 'Comp Precision Health DE', '00E024', 'Comp Precision Health DE', 'DE', 'GGCPHLTH', 'Computational Precision Health Graduate Group', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00E20G', 'A', 'Sociology of Orgs & Markets DE', '00E20', 'Sociology of Orgs & Markets DE', 'DE', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00INDCPHLG', 'A', 'Grad Div Indiv Major CPhil', '00451', 'Grad Div Individual Major', 'MAJ', 'GRADDIVIDP', 'Interdisciplinary Doctoral Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('00INDMSG', 'A', 'Grad Div Individual Major MS', '00451', 'Grad Div Individual Major', 'MAJ', 'GRADDIVIDP', 'Interdisciplinary Doctoral Programs', 'GRADDIVDIV', 'Graduate Division (Division Lvl)', 'GRADDIV', 'Graduate Division', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('00OPT2002G', 'A', 'Geo Info Sci and Tech Cert', '00OPT2002', 'Geo Info Sci and Tech Cert', 'OP2', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2003G', 'A', 'Inter Grad Real Estate Cert', '00OPT2003', 'Inter Grad Real Estate Cert', 'OP2', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2004G', 'A', 'Info & Comm Tech & Dev Cert', '00OPT2004', 'Info & Comm Tech & Dev Cert', 'OP2', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2005G', 'A', 'Rsch Cognition & Math Ed Cert', '00OPT2005', 'Rsch Cognition & Math Ed Cert', 'OP2', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2007G', 'A', 'Global Urban Humanities Cert', '00OPT2007', 'Global Urban Humanities Cert', 'OP2', 'ARTHUMOTHS', 'Other Arts and Humanities Programs', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2009G', 'A', 'Grad Cert in Food Systems', '00OPT2009', 'Grad Cert in Food Systems', 'OP2', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2011G', 'A', 'Grad Cert Applied Data Science', '00OPT2011', 'Grad Cert Applied Data Science', 'OP2', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2013G', 'A', 'Learning Sciences Certificate', '00OPT2013', 'Learning Sciences Certificate', 'OP2', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2015G', 'A', 'Health Management Certificate', '00OPT2015', 'Health Management Certificate', 'OP2', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2016G', 'A', 'Mats for Bio & Med Apps Cert', '00OPT2016', 'Mats for Bio & Med Apps Cert', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2017G', 'A', 'Struct Mats for Nuc Apps Cert', '00OPT2017', 'Struct Mats for Nuc Apps Cert', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2020G', 'A', 'Engineering Data Science Cert', '00OPT2020', 'Engineering Data Science Cert', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00OPT2022G', 'A', 'Advncd Manuf Processes Cert', '00OPT2022', 'Advncd Manuf Processes Cert', 'OP2', 'FUNGINST', 'Fung Institute for Engineering Leadership', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', NULL, NULL, NULL, NULL),
('00V02G', 'A', 'UC San Francisco Visitor GR', '00V02', 'UC San Francisco Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V04G', 'A', 'UC Los Angeles Visitor GR', '00V04', 'UC Los Angeles Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V04ICVG', 'A', 'UC Los Angeles ICV GR', '00V04', 'UC Los Angeles Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('00V06G', 'A', 'UC San Diego Visitor GR', '00V06', 'UC San Diego Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V08G', 'A', 'UC Santa Barbara Visitor GR', '00V08', 'UC Santa Barbara Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V09G', 'A', 'UC Irvine Visitor GR', '00V09', 'UC Irvine Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('00V10ICVG', 'A', 'UC Merced ICV GR', '00V10', 'UC Merced Visitor', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', NULL, NULL),
('04000MILLU', 'A', 'CNR UCB Changemaker Oakland UG', '04000', 'CNR Undeclared', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BACHL', 'Bachelor''s Degree'),
('04000U', 'A', 'CNR Undeclared UG', '04000', 'CNR Undeclared', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BACHL', 'Bachelor''s Degree'),
('04021MSG', 'A', 'Ag & Environmental Chem MS', '04021', 'Ag & Environmental Chem', 'MAJ', 'GGAGECH', 'Agricultural and Environmental Chemistry Grad Grp', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04021PHDG', 'A', 'Ag & Environmental Chem PhD', '04021', 'Ag & Environmental Chem', 'MAJ', 'GGAGECH', 'Agricultural and Environmental Chemistry Grad Grp', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04034MAG', 'A', 'Ag & Resource Economics MA', '04034', 'Ag & Resource Economics', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('04034MSG', 'A', 'Ag & Resource Economics MS', '04034', 'Ag & Resource Economics', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04115U', 'A', 'Bioenergetics BS', '04115', 'Bioenergetics', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04189MAG', 'A', 'Comparative Biochemistry MA', '04189', 'Comparative Biochemistry', 'MAJ', 'GGCMBIO', 'Comparative Biochemistry Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('04202U', 'A', 'Conservation of Nat Res BS', '04202', 'Conservation of Nat Res', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04258U', 'A', 'Nut Sci-Physio & Metabol BS', '04258', 'Nut Sci-Physio & Metabol', 'SP', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04263U', 'A', 'Nutritional Sci-Dietetics BS', '04263', 'Nutritional Sci-Dietetics', 'SP', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04264U', 'A', 'Nutritional Sci-Toxicology BS', '04264', 'Nutritional Sci-Toxicology', 'SP', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('042E8U', 'A', 'Eco Mgmt & For-Forestry BS', '042E8', 'Eco Mgmt & For-Forestry', 'SP', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04348MSG', 'A', 'Entomology MS', '04348', 'Entomology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04348PHDG', 'A', 'Entomology PhD', '04348', 'Entomology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04348U', 'A', 'Entomology BS', '04348', 'Entomology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04351U', 'A', 'Environmental Sciences BS', '04351', 'Environmental Sciences', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04356U', 'A', 'Environmental Studies BS', '04356', 'Environmental Studies', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04368U', 'A', 'Molecular Toxicology BS', '04368', 'Molecular Toxicology', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04376U', 'A', 'Forest Products BS', '04376', 'Forest Products', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04380CWOG', 'A', 'Forestry CWO', '04380', 'Forestry', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04380MFG', 'A', 'Forestry MF', '04380', 'Forestry', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '23', 'Master of Forestry'),
('04390MAG', 'A', 'Genetics MA', '04390', 'Genetics', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('04390MSG', 'A', 'Genetics MS', '04390', 'Genetics', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04390PHDG', 'A', 'Genetics PhD', '04390', 'Genetics', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04390U', 'A', 'Genetics BS', '04390', 'Genetics', 'MAJ', 'CNROTHS', 'Other College of Natural Resources Programs', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04574U', 'A', 'Molecular Plant Biology BS', '04574', 'Molecular Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04603MSG', 'A', 'Nutrition MS', '04603', 'Nutrition', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04603PHDG', 'A', 'Nutrition PhD', '04603', 'Nutrition', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04607U', 'A', 'Nutrition & Clinical Diet BS', '04607', 'Nutrition & Clinical Diet', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04608U', 'A', 'Nutrition & Food Science BS', '04608', 'Nutrition & Food Science', 'MAJ', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04630PHDG', 'A', 'Parasitology PhD', '04630', 'CNR Parasitology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04680U', 'A', 'Plant Biology BS', '04680', 'Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04681U', 'A', 'Plant Pathology BS', '04681', 'Plant Pathology', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04683CWOG', 'A', 'Env Sci, Policy, & Mgmt CWO', '04683', 'Env Sci, Policy, & Mgmt', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04683U', 'A', 'Env Sci, Policy, & Mgmt BS', '04683', 'Env Sci, Policy, & Mgmt', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04684MSG', 'A', 'Mol & Phys Plant Biology MS', '04684', 'Mol & Phys Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04684PHDG', 'A', 'Mol & Phys Plant Biology PhD', '04684', 'Mol & Phys Plant Biology', 'MAJ', 'PLANTBI', 'Plant and Microbial Biology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04779U', 'A', 'Environ Econ & Policy BS', '04779', 'Environ Econ & Policy', 'MAJ', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04798CWOG', 'A', 'Rangeland & Wildlife Mgmt CWO', '04798', 'Rangeland & Wildlife Mgmt', 'MAJ', 'GGRANGE', 'Rangeland and Wildlife Management Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('04876MSG', 'A', 'Soil Science MS', '04876', 'Soil Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04929CPHLG', 'A', 'Wood Science & Tech CPhil', '04929', 'Wood Science & Technology', 'MAJ', 'GGWDST', 'Wood Science and Technology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('04929MSG', 'A', 'Wood Science & Technology MS', '04929', 'Wood Science & Technology', 'MAJ', 'GGWDST', 'Wood Science and Technology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04929PHDG', 'A', 'Wood Science & Technology PhD', '04929', 'Wood Science & Technology', 'MAJ', 'GGWDST', 'Wood Science and Technology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('04929U', 'A', 'Wood Science & Technology BS', '04929', 'Wood Science & Technology', 'MAJ', 'GGWDST', 'Wood Science and Technology Graduate Group', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', 'BS', 'Bachelor of Science'),
('04930MFG', 'A', 'Wildland Resource Science MF', '04930', 'Wildland Resource Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '23', 'Master of Forestry'),
('04930MSG', 'A', 'Wildland Resource Science MS', '04930', 'Wildland Resource Science', 'MAJ', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('04I001U', 'A', 'Conservation & Resrce St UG', '04MNRESPM', 'ESPM Minors', 'MIN', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I003U', 'A', 'Environ Econ & Policy UG', '04MNRARESEC', 'Ag & Resource Econ Pol Minors', 'MIN', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I004U', 'A', 'Forestry & Nat Resources UG', '04MNRESPM', 'ESPM Minors', 'MIN', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I122U', 'A', 'Food Systems UG', '04MNRESPM', 'ESPM Minors', 'MIN', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I144U', 'A', 'Molecular Toxicology UG', '04MNRNUTRSCI', 'Nutritional Science Minors', 'MIN', 'NUTRSCI', 'Nutritional Sciences and Toxicology', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('04I147U', 'A', 'Forestry & Resource Mgmt UG', '04MNRESPM', 'ESPM Minors', 'MIN', 'ESPM', 'Environmental Science, Policy, and Management', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16298U', 'A', 'Nuclear Engineering BS', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('04V04U', 'A', 'UC Los Angeles Visitor CNR UG', '04V04', 'UC Los Angeles Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V05U', 'A', 'UC Riverside Visitor CNR UG', '04V05', 'UC Riverside Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V06ICVU', 'A', 'UC San Diego ICV CNR UG', '04V06', 'UC San Diego Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V06U', 'A', 'UC San Diego Visitor CNR UG', '04V06', 'UC San Diego Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V07U', 'A', 'UC Santa Cruz Visitor CNR UG', '04V07', 'UC Santa Cruz Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('04V09ICVU', 'A', 'UC Irvine ICV CNR UG', '04V09', 'UC Irvine Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCNR', 'Undergrad Natural Resources', NULL, NULL),
('04V10U', 'A', 'UC Merced Visitor CNR UG', '04V10', 'UC Merced Visitor CNR', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('07I171U', 'A', 'Sustainable Business & Policy', '04MNRARESEC', 'Ag & Resource Econ Pol Minors', 'MIN', 'ARESEC', 'Agricultural and Resource Economics and Policy', 'CNRDIV', 'Rausser College of Natural Resources (Div Lvl)', 'CNR', 'Rausser College of Natural Resources', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('08008U', 'A', 'Other Limited UG', '08008', 'Other Limited', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('08100U', 'A', 'Asian American Studies BA', '08100', 'Asian American Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('0835VU', 'A', 'Unaffiliated Interdis Major BA', '0835V', 'Unaffiliated Interdis Major', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('08587U', 'A', 'Native American Studies BA', '08587', 'Native American Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('09V00U', 'A', 'Non-UC Campus Visitor EVCP UG', '09V00', 'Non-UC Campus Visitor EVCP', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('10000U', 'A', 'Chemistry Undeclared UG', '10000', 'Chemistry Undeclared', 'MAJ', 'CHMOTHS', 'Other College of Chemistry Programs', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BACHL', 'Bachelor''s Degree'),
('10008U', 'A', 'Chemistry Limited UG', '10008', 'Chemistry Limited', 'MAJ', 'CHMOTHS', 'Other College of Chemistry Programs', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('100DNMSSEG', 'A', 'Mol Sci & Software Engin MMSSE', '100DN', 'Mol Sci & Software Engin', 'SS', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'A1', 'Master of Mol Sci & SW Engin'),
('10153MSG', 'A', 'Chemistry MS', '10153', 'Chemistry', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('10153PHDG', 'A', 'Chemistry PhD', '10153', 'Chemistry', 'MAJ', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('10294ACMSG', 'A', 'Chemical Engineering Acad MS', '10294', 'Chemical Engineering', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('10294PHDG', 'A', 'Chemical Engineering PhD', '10294', 'Chemical Engineering', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('102B4U', 'A', 'Chem Eng/NE Joint Major BS', '102B4', 'Chem Eng/NE Joint Major', 'MAJ', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', 'UCCH', 'Undergrad Chemistry', 'BS', 'Bachelor of Science'),
('102F6MBEG', 'A', 'Bioprocess Engineering MBE', '102F6', 'Bioprocess Engineering MBE', 'SS', 'CHMENG', 'Chemical and Biomolecular Engineering', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'A8', 'Master of Bioprocess Engin'),
('10I009U', 'A', 'Chemistry UG', '10MNRCHEM', 'Chemistry Minors', 'MIN', 'CHEM', 'Chemistry', 'CCHDIV', 'College of Chemistry (Division Lvl)', 'CCH', 'College of Chemistry', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16008U', 'A', 'Engineering Limited UG', '16008', 'Engineering Limited', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16201CPHLG', 'A', 'Computer Science CPhil', '16201', 'Computer Science', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('16201MSG', 'A', 'Computer Science MS', '16201', 'Computer Science', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16228U', 'A', 'Computational Eng Science BS', '16228', 'Computational Eng Science', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16275CEPPG', 'A', 'Civil & Env Eng MS-MPP CDP', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16275DENGG', 'A', 'Civil & Environmental Eng DEng', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16275MENGG', 'A', 'Civil & Environmental Eng MEng', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16275PHDG', 'A', 'Civil & Environmental Eng PhD', '16275', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16287MENGG', 'A', 'Civil Engineering MEng', '16287', 'Civil Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16287PHDG', 'A', 'Civil Engineering PhD', '16287', 'Civil Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16288BEBAG', 'A', 'BioEng MEng-MBA CDP', '16288', 'Bioengineering', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16288JMSG', 'A', 'Bioengineering Joint MS', '16288', 'Bioengineering', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '94', 'Joint Master of Science'),
('16288U', 'A', 'Bioengineering BS', '16288', 'Bioengineering', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162905YMSG', 'A', 'Elec Eng & Comp Sci 5th Yr MS', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16290CPHLG', 'A', 'Elec Eng & Comp Sci CPhil', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('16290MSG', 'A', 'Electrical Eng & Comp Sci MS', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16290PHDG', 'A', 'Electrical Eng & Comp Sci PhD', '16290', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16292IEBAG', 'A', 'IEOR MEng-MBA CDP', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16292MENGG', 'A', 'Industrial Eng & Ops Rsch MEng', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16292MSG', 'A', 'Industrial Eng & Ops Rsch MS', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16292PHDG', 'A', 'Industrial Eng & Ops Rsch PhD', '16292', 'Industrial Eng & Ops Rsch', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16293MENGG', 'A', 'Mat Sci & Mineral Eng MEng', '16293', 'Mat Sci & Mineral Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '21', 'Master of Engineering'),
('16295CWOG', 'A', 'Mechanical Engineering CWO', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16295DENGG', 'A', 'Mechanical Engineering DEng', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '56', 'Doctor of Engineering'),
('16295MAG', 'A', 'Mechanical Engineering MA', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('16295MEPPG', 'A', 'Mechanical Eng MS-MPP CDP', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16295MSG', 'A', 'Mechanical Engineering MS', '16295', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16296MSG', 'A', 'Naval Architecture MS', '16296', 'Naval Architecture', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16296PHDG', 'A', 'Naval Architecture PhD', '16296', 'Naval Architecture', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16296U', 'A', 'Naval Architecture BS', '16296', 'Naval Architecture', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16298NEBAG', 'A', 'Nuclear Eng MEng-MBA CDP', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16298PHDG', 'A', 'Nuclear Engineering PhD', '16298', 'Nuclear Engineering', 'MAJ', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('25I081U', 'A', 'Geography UG', '25MNRGEOG', 'Geography Minors', 'MIN', 'GEOG', 'Geography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('162B0U', 'A', 'Engineering Undeclared UG', '162B0', 'Engineering Undeclared', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BACHL', 'Bachelor''s Degree'),
('162B6U', 'A', 'EECS/MSE Joint Major BS', '162B6', 'EECS/MSE Joint Major', 'MAJ', 'COEJNT', 'Engineering Joint Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162B7U', 'A', 'MSE/ME Joint Major BS', '162B7', 'MSE/ME Joint Major', 'MAJ', 'COEJNT', 'Engineering Joint Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162B8U', 'A', 'MSE/NE Joint Major BS', '162B8', 'MSE/NE Joint Major', 'MAJ', 'COEJNT', 'Engineering Joint Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162B9U', 'A', 'EECS/NE Joint Major BS', '162B9', 'EECS/NE Joint Major', 'MAJ', 'COEJNT', 'Engineering Joint Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('162C8CWOG', 'A', 'Translational Medicine CWO', '162C8', 'Translational Medicine', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('162C8MTMG', 'A', 'Translational Medicine MTM', '162C8', 'Translational Medicine', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '98', 'Master of Translational Med'),
('162D1MENGG', 'A', 'Nuclear Engineering PT MEng', '162D1', 'Nuclear Engineering PT MEng', 'SS', 'NUCENG', 'Nuclear Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162D2MENGG', 'A', 'Civil & Environ Eng PT MEng', '162D2', 'Civil & Environ Eng PT MEng', 'SS', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162D4MENGG', 'A', 'Engineering PT MEng', '162D4', 'Engineering PT MEng', 'SS', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162D7MENGG', 'A', 'Mechanical Engineering PT MEng', '162D7', 'Mechanical Engineering PT MEng', 'SS', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '21', 'Master of Engineering'),
('162E9CEARG', 'A', 'Civil & Env Eng MS-MArch CDP', '162E9', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MS', 'Master of Science'),
('162E9CECPG', 'A', 'Civil & Env Eng MS-MCP CDP', '162E9', 'Civil & Environmental Eng', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MS', 'Master of Science'),
('162G4ANLTG', 'A', 'Analytics MAnlytx', '162G4', 'Analytics', 'SS', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'C2', 'Master of Analytics'),
('16306U', 'A', 'Electrical Eng & Comp Sci BS', '16306', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16308MSG', 'A', 'Electrical Eng & Comp Sci MS', '16308', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16308PHDG', 'A', 'Electrical Eng & Comp Sci PhD', '16308', 'Electrical Eng & Comp Sci', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16309U', 'A', 'Engineering Geoscience BS', '16309', 'Engineering Geoscience', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16312U', 'A', 'Eng Math & Statistics BS', '16312', 'Eng Math & Statistics', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16318U', 'A', 'General Engineering Sci BS', '16318', 'General Engineering Sci', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16319PHDG', 'A', 'Transportation Engineering PhD', '16319', 'Transportation Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16328CPHLG', 'A', 'Materials Science & Eng CPhil', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('16328MSPPG', 'A', 'Matl Science & Eng MS-MPP CDP', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16328U', 'A', 'Materials Science & Eng BS', '16328', 'Materials Science & Eng', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16330U', 'A', 'Mechanical Engineering BS', '16330', 'Mechanical Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16334CWOG', 'A', 'Ocean Engineering CWO', '16334', 'Ocean Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('16334MENGG', 'A', 'Ocean Engineering MEng', '16334', 'Ocean Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '21', 'Master of Engineering'),
('16334MSG', 'A', 'Ocean Engineering MS', '16334', 'Ocean Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('16334PHDG', 'A', 'Ocean Engineering PhD', '16334', 'Ocean Engineering', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('16337U', 'A', 'Petroleum Engineering BS', '16337', 'Petroleum Engineering', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16338U', 'A', 'Mineral Engineering BS', '16338', 'Mineral Engineering', 'MAJ', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16384U', 'A', 'Environmental Eng Science BS', '16384', 'Environmental Eng Science', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16656U', 'A', 'General Engineering Sci BS', '16656', 'General Engineering Sci', 'MAJ', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', 'BS', 'Bachelor of Science'),
('16A07U', 'I', 'EECS+Business Admin MET Pgm UG', '16A07', 'EECS+Business Admin MET Pgm', 'MAJ', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A08U', 'I', 'IEOR+Business Admin MET Pgm UG', '16A08', 'IEOR+Business Admin MET Pgm', 'MAJ', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A09U', 'I', 'ME+Business Admin MET Pgm UG', '16A09', 'ME+Business Admin MET Pgm', 'MAJ', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A16U', 'I', 'BioEng + BusAdm MET Pgm UG', '16A16', 'BioEng + BusAdm MET Pgm', 'MAJ', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A17U', 'I', 'CivEng + BusAdm MET Pgm UG', '16A17', 'CivEng + BusAdm MET Pgm', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16A21U', 'A', 'Mills 3+2 Engineering Pgm UG', '16A21', 'Mills 3+2 Engineering Pgm', 'MAJ', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16I010U', 'A', 'Bioengineering UG', '16MNRBIOENG', 'Bioengineering Minors', 'MIN', 'BIOENG', 'Bioengineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I011U', 'A', 'Computer Science UG', '16MNREECS', 'El Eng & Comp Sci Minors', 'MIN', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I012U', 'A', 'Elec Eng & Computer Sci UG', '16MNREECS', 'El Eng & Comp Sci Minors', 'MIN', 'ELENG', 'Electrical Engineering and Computer Sciences', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I013U', 'A', 'Energy Engineering UG', '16MNRENGSCI', 'Engineering Science Minors', 'MIN', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I015U', 'A', 'Geosystems UG', '16MNRCIVENG', 'Civil & Env Engineering Minors', 'MIN', 'CIVENG', 'Civil and Environmental Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I016U', 'A', 'Industrial Eng & Op Rsch UG', '16MNRIEOR', 'Industrial Eng Ops Rsch Minors', 'MIN', 'INDENG', 'Industrial Engineering and Operations Research', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I017U', 'A', 'Materials Science & Eng UG', '16MNRMATSCI', 'Materials Science & Eng Minors', 'MIN', 'MATSCI', 'Materials Science and Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I018U', 'A', 'Mechanical Engineering UG', '16MNRMECENG', 'Mechanical Engineering Minors', 'MIN', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I148U', 'A', 'Geoengineering UG', '16MNRENGSCI', 'Engineering Science Minors', 'MIN', 'ENGSCI', 'Engineering Science Programs', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16I159U', 'A', 'Aerospace Engineering UG', '16MNRMECENG', 'Mechanical Engineering Minors', 'MIN', 'MECENG', 'Mechanical Engineering', 'COEDIV', 'College of Engineering (Division Lvl)', 'COE', 'College of Engineering', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('16V03ICVU', 'A', 'UC Davis ICV COE UG', '16V03', 'UC Davis Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V04ICVU', 'A', 'UC Los Angeles ICV COE UG', '16V04', 'UC Los Angeles Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V08U', 'A', 'UC Santa Barbara Visitor EN UG', '16V08', 'UC Santa Barbara Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('16V09ICVU', 'A', 'UC Irvine ICV COE UG', '16V09', 'UC Irvine Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('16V10ICVU', 'A', 'UC Merced ICV COE UG', '16V10', 'UC Merced Visitor COE', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCOE', 'Undergrad Engineering', NULL, NULL),
('19008U', 'A', 'Environmntl Design Limited UG', '19008', 'Environmental Design Limited', 'MAJ', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19084ARCEG', 'A', 'Architecture MArch-CEE MS CDP', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('19084ARCPG', 'A', 'Architecture MArch-MCP CDP', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('19084ARLAG', 'A', 'Architecture MArch-MLA CDP', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('19084CWOG', 'A', 'Architecture CWO', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('19084MARCG', 'A', 'Architecture MArch', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('19084U', 'A', 'Architecture BA', '19084', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'AB', 'Bachelor of Arts'),
('19165CWOG', 'A', 'City & Regional Planning CWO', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('19165U', 'A', 'City & Regional Planning BA', '19165', 'City & Regional Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'AB', 'Bachelor of Arts'),
('19222MAG', 'A', 'Design MA', '19222', 'Design', 'MAJ', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('192D9U', 'A', 'Sustainable Environ Dsgn BA', '192D9', 'Sustainable Environ Dsgn', 'MAJ', 'IURD', 'Institute of Urban & Regional Development Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'AB', 'Bachelor of Arts'),
('192F1REDDG', 'A', 'Real Estate Dev & Design MREDD', '192F1', 'Real Estate Dev & Design', 'SS', 'IURD', 'Institute of Urban & Regional Development Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'RE', 'Master of Real Estate Dev Des'),
('192F2ARCPG', 'A', 'Architecture MArch-MCP CDP', '192F2', 'Architecture', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '10', 'Master of Architecture'),
('192F3LAARG', 'A', 'Landscape Arch MLA-MArch CDP', '192F3', 'Landscape Architecture', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '27', 'Master of Landscape Arch'),
('192F4MAADG', 'A', 'Master of Adv Arch Design MAAD', '192F4', 'Master of Adv Arch Design', 'MAJ', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'A7', 'Master of Adv Arch Design'),
('192F5CPCEG', 'A', 'City & Reg Plan MCP-CEE MS CDP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('192F5CPHTG', 'A', 'City & Reg Plan MCP-UCL JD CDP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('192F5MCPG', 'A', 'Master of City Planning MCP', '192F5', 'Master of City Planning', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '15', 'Master of City Planning'),
('19340CPHLG', 'A', 'Environmental Planning CPhil', '19340', 'Environmental Planning', 'MAJ', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('19912U', 'A', 'Urban Studies BA', '19912', 'Urban Studies', 'MAJ', 'CYPLAN', 'City and Regional Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', 'AB', 'Bachelor of Arts'),
('19I021U', 'A', 'Architecture UG', '19MNRARCH', 'Architecture Minors', 'MIN', 'ARCH', 'Architecture', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I114U', 'A', 'Ecological Design UG', '19MNRLAEP', 'Land Arch & Env Plan Minors', 'MIN', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I115U', 'A', 'Landscape Design UG', '19MNRLAEP', 'Land Arch & Env Plan Minors', 'MIN', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19I149U', 'A', 'Landscape Architecture UG', '19MNRLAEP', 'Land Arch & Env Plan Minors', 'MIN', 'LDARCH', 'Landscape Architecture and Environmental Planning', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19INDMAG', 'A', 'Env Design Individual Major MA', '19451', 'CED Individual Major', 'MAJ', 'ENVDOST', 'Other College of Environmental Design Programs', 'CEDDIV', 'College of Environmental Design (Division Lvl)', 'CED', 'College of Environmental Design', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('19V00U', 'A', 'Non-UC Campus Visitor CED UG', '19V00', 'Non-UC Campus Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V03U', 'A', 'UC Davis Visitor CED UG', '19V03', 'UC Davis Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V05ICVU', 'A', 'UC Riverside ICV CED UG', '19V05', 'UC Riverside Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V06ICVU', 'A', 'UC San Diego ICV CED UG', '19V06', 'UC San Diego Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V06U', 'A', 'UC San Diego Visitor CED UG', '19V06', 'UC San Diego Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25I160U', 'A', 'American Studies UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('19V08ICVU', 'A', 'UC Santa Barbara ICV CED UG', '19V08', 'UC Santa Barbara Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('19V08U', 'A', 'UC Santa Barbara Visitor ED UG', '19V08', 'UC Santa Barbara Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V09U', 'A', 'UC Irvine Visitor CED UG', '19V09', 'UC Irvine Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('19V10ICVU', 'A', 'UC Merced ICV CED UG', '19V10', 'UC Merced Visitor CED', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCED', 'Undergrad Environmental Design', NULL, NULL),
('25000FPFU', 'A', 'L&S Undcl Fall Pgm First Sm UG', '25000', 'Letters & Sci Undeclared', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'BACHL', 'Bachelor''s Degree'),
('25008U', 'A', 'Letters & Science Limited UG', '25008', 'Letters & Science Limited', 'MAJ', 'LSLIMITED', 'Letters & Science Limited Majors', 'LSLIMTDDIV', 'L&S Limited (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25014U', 'A', 'African American Studies BA', '25014', 'African American Studies', 'SP', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25019U', 'A', 'Afr Amer Stds-Humanities BA', '25019', 'Afr Amer Stds-Humanities', 'SP', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25020U', 'A', 'Afr Amer Stds-Social Sci BA', '25020', 'Afr Amer Stds-Social Sci', 'SP', 'AFRICAM', 'African American Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25054U', 'A', 'Ancient NE Civilizations BA', '25054', 'Ancient NE Civilizations', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25063U', 'A', 'Anthropology BA', '25063', 'Anthropology', 'MAJ', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25067U', 'A', 'Ancnt NE Archae & Art Hist BA', '25067', 'Ancnt NE Archae & Art Hist', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25090U', 'A', 'Art BA', '25090', 'Art', 'MAJ', 'ART', 'Art Practice', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25097U', 'A', 'Asian Studies - Japan BA', '25097', 'Asian Studies - Japan', 'SP', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('250HEU', 'A', 'MELC Middle Eastern Worlds BA', '250HE', 'MELC Middle Eastern Worlds', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('250Z9U', 'A', 'Asian Studies - India BA', '250Z9', 'Asian Studies - India', 'SP', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25100U', 'A', 'Asian American Studies BA', '25100', 'Asian American Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25108U', 'A', 'Bacteriology BA', '25108', 'Bacteriology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25111U', 'A', 'Biochemistry BA', '25111', 'Biochemistry', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25120U', 'A', 'Biological Sciences BA', '25120', 'Biological Sciences', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25126U', 'A', 'Biophysics BA', '25126', 'Biophysics', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25136U', 'A', 'BioSci-Pl Cell & Mol Bio BA', '25136', 'BioSci-Pl Cell & Mol Bio', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25138U', 'A', 'Botany BA', '25138', 'Botany', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25147U', 'A', 'Celtic Studies BA', '25147', 'Celtic Studies', 'MAJ', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25153U', 'A', 'Chemistry BA', '25153', 'L&S Chemistry', 'MAJ', 'LSCHEM', 'Letters and Science Chemistry', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25169U', 'A', 'Classical Civilizations BA', '25169', 'Classical Civilizations', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25174U', 'A', 'Classics BA', '25174', 'Classics', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25179U', 'A', 'Cognitive Science BA', '25179', 'Cognitive Science', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25192U', 'A', 'Comparative Literature BA', '25192', 'Comparative Literature', 'MAJ', 'COMLIT', 'Comparative Literature', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25234U', 'A', 'Dramatic Art BA', '25234', 'Dramatic Art', 'MAJ', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25235U', 'A', 'Dramatic Art - Dance BA', '25235', 'Dramatic Art - Dance', 'MAJ', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25236U', 'A', 'Dutch Studies BA', '25236', 'Dutch Studies', 'MAJ', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25240U', 'A', 'Earth Science BA', '25240', 'Earth Science', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25246U', 'A', 'Economics BA', '25246', 'Economics', 'MAJ', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252A4U', 'A', 'Earth & Planetary Science BA', '252A4', 'Earth & Planetary Science', 'MAJ', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252B1U', 'A', 'Planetary Science BA', '252B1', 'Planetary Science', 'SP', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252C2U', 'A', 'Asian Am & Asn Diaspora Std BA', '252C2', 'Asian Am & Asian Diasp St', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252E1U', 'A', 'E Asian Rel, Thought, & Cul BA', '252E1', 'E Asian Rel, Thought, & Cul', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252G3U', 'A', 'Ancient Grk & Roman Studies BA', '252G3', 'Ancient Grk & Roman Studies', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('252G8U', 'A', 'East Asian Humanities BA', '252G8', 'East Asian Humanities', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25351U', 'A', 'Environmental Sciences BA', '25351', 'L&S Environmental Sciences', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25360U', 'A', 'Ethnic Studies BA', '25360', 'Ethnic Studies', 'MAJ', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25370U', 'A', 'Environ Sci-Physical Sci BA', '25370', 'Environ Sci-Physical Sci', 'SP', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25387U', 'A', 'French BA', '25387', 'French', 'MAJ', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25390U', 'A', 'Genetics BA', '25390', 'L&S Genetics', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('253A0U', 'A', 'Environmental Earth Science BA', '253A0', 'Environmental Earth Science', 'SP', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25402U', 'A', 'Geology BA', '25402', 'Geology', 'SP', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25408U', 'A', 'German BA', '25408', 'German', 'MAJ', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25414U', 'A', 'Greek BA', '25414', 'Greek', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25429U', 'A', 'History BA', '25429', 'History', 'MAJ', 'HISTORY', 'History', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25477U', 'A', 'Italian BA', '25477', 'Italian', 'MAJ', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25492U', 'A', 'Global Studies BA', '25492', 'Global Studies', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25495U', 'A', 'Latin BA', '25495', 'Latin', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25497U', 'A', 'Legal Studies BA', '25497', 'L&S Legal Studies', 'MAJ', 'LSLEGST', 'Letters & Science Legal Studies', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25569U', 'A', 'Microbiology BA', '25569', 'Microbiology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25573U', 'A', 'Molecular Biology BA', '25573', 'Molecular Biology', 'MAJ', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25579U', 'A', 'Music BA', '25579', 'Music', 'MAJ', 'MUSIC', 'Music', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('255C2U', 'A', 'Ancnt Egypt/NE Art & Archae BA', '255C2', 'Ancnt Egypt/NE Art & Archae', 'SP', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25621U', 'A', 'East Asian Languages BA', '25621', 'East Asian Languages', 'MAJ', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25625U', 'A', 'Greek & Latin BA', '25625', 'Greek & Latin', 'MAJ', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25627U', 'A', 'Paleontology BA', '25627', 'Paleontology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25628U', 'A', 'Interdisciplinary Studies BA', '25628', 'Interdisciplinary Studies', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25631U', 'A', 'Peace & Conflict Studies BA', '25631', 'Peace & Conflict Studies', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25651U', 'A', 'Philosophy BA', '25651', 'Philosophy', 'MAJ', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25654U', 'A', 'Human Biodynamics BA', '25654', 'Human Biodynamics', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25657U', 'A', 'Physical Sci Field Major BA', '25657', 'Physical Sci Field Major', 'MAJ', 'PHYSOTH', 'Other Math and Physical Sciences Programs', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25675U', 'A', 'Physiology BA', '25675', 'Physiology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25697U', 'A', 'Pol Econ of Indust Soc BA', '25697', 'Pol Econ of Indust Soc', 'MAJ', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25779U', 'A', 'Environ Econ & Policy BA', '25779', 'L&S Environ Econ & Policy', 'MAJ', 'LSEEP', 'Letters & Science Environmental Economics & Policy', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25780U', 'A', 'Psychology BA', '25780', 'Psychology', 'MAJ', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25789U', 'A', 'Public Health BA', '25789', 'L&S Public Health', 'MAJ', 'LSPUBHLTH', 'Letters & Science Public Health', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25801U', 'A', 'Religious Studies BA', '25801', 'Religious Studies', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25858U', 'A', 'Social Sciences Field Maj BA', '25858', 'Social Sciences Field Maj', 'MAJ', 'SOCSCIOTHS', 'Other Social Sciences Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25864U', 'A', 'Social Welfare BA', '25864', 'L&S Social Welfare', 'MAJ', 'LSSOCWEL', 'Letters & Science Social Welfare', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25877U', 'A', 'South & SE Asian Studies BA', '25877', 'South & SE Asian Studies', 'MAJ', 'SSEASN', 'South and Southeast Asian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25882U', 'A', 'Span-Spanish Lang & Lit BA', '25882', 'Spanish-Spanish Lang & Lit', 'SP', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25891U', 'A', 'Statistics BA', '25891', 'Statistics', 'MAJ', 'STAT', 'Statistics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25907U', 'A', 'Span-Latin-Amer Lang & Lit BA', '25907', 'Spanish-Latin-Amer Lang & Lit', 'SP', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25928U', 'A', 'Womens Studies BA', '25928', 'Womens Studies', 'MAJ', 'GWS', 'Gender and Womens Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25933U', 'A', 'Zoology BA', '25933', 'Zoology', 'MAJ', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25963U', 'A', 'IB-Ecology BA', '25963', 'IB-Ecology', 'SP', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25967U', 'A', 'MCB-Genetics BA', '25967', 'MCB-Genetics', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25968U', 'A', 'MCB-Immunology BA', '25968', 'MCB-Immunology', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25969U', 'A', 'MCB-Microbiology BA', '25969', 'MCB-Microbiology', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25971U', 'A', 'MCB-Cell & Dev Biology BA', '25971', 'MCB-Cell & Dev Biology', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25972U', 'A', 'MCB-Neurobiology BA', '25972', 'MCB-Neurobiology', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25973U', 'A', 'MCB-Biophysics BA', '25973', 'MCB-Biophysics', 'SP', 'MCELLBI', 'Molecular and Cell Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('259A1U', 'A', 'Gender & Womens Studies BA', '259A1', 'Gender & Womens Studies', 'MAJ', 'GWS', 'Gender and Womens Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25A03U', 'I', 'Intending Math/Phys/Bio Sci UG', '25A03', 'Intending Math/Phys/Bio Sci', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A09U', 'I', 'Undecided Bio Sciences UG', '25A09', 'Undecided Bio Sciences', 'MAJ', 'BIOSCIOTHS', 'Other Biological Sciences Programs', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25A23U', 'A', 'Intending Education UG', '25A23', 'Intending Education', 'MAJ', 'LSUNDECL', 'Letters and Science Undeclared Majors', 'LSUNDCLDIV', 'Letters and Science Undeclared (Division Lvl)', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25I028U', 'A', 'Anct Egypt & Nr East Civ UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I030U', 'A', 'Art UG', '25MNRART', 'Art Practice Minors', 'MIN', 'ART', 'Art Practice', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I031U', 'A', 'Bosnia/Croat/Serbian Lit UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I033U', 'A', 'Celtic Studies UG', '25MNRSCANDIN', 'Scandinavian Minors', 'MIN', 'SCANDIN', 'Scandinavian', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I034U', 'A', 'Chinese UG', '25MNREALANG', 'East Asian Lang Culture Minors', 'MIN', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I036U', 'A', 'E. Euro/Eurasian Lang Cult UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I038U', 'A', 'Dutch Studies UG', '25MNRGERMAN', 'German Minors', 'MIN', 'GERMAN', 'German', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I039U', 'A', 'English UG', '25MNRENGLISH', 'English Minors', 'MIN', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I041U', 'A', 'French Civilization UG', '25MNRFRENCH', 'French Minors', 'MIN', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I042U', 'A', 'French Language Studies UG', '25MNRFRENCH', 'French Minors', 'MIN', 'FRENCH', 'French', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I045U', 'A', 'Greek UG', '25MNRCLASSIC', 'Classics Minors', 'MIN', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I048U', 'A', 'Italian Studies UG', '25MNRITALIAN', 'Italian Studies Minors', 'MIN', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I050U', 'A', 'Jewish Studies UG', '25MNRJWST', 'Jewish Studies Minors', 'MIN', 'GGJWST', 'Jewish Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I052U', 'A', 'Latin UG', '25MNRCLASSIC', 'Classics Minors', 'MIN', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I053U', 'A', 'Portuguese Lang, Lit & Cult UG', '25MNRSPANPOR', 'Spanish & Portuguese Minors', 'MIN', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I054U', 'A', 'Medieval Studies UG', '25MNRMEDST', 'Medieval Studies Minors', 'MIN', 'GGMEDST', 'Medieval Studies Program', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I055U', 'A', 'Music UG', '25MNRMUSIC', 'Music Minors', 'MIN', 'MUSIC', 'Music', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I056U', 'A', 'Persian UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I057U', 'A', 'Philosophy UG', '25MNRPHILOS', 'Philosophy Minors', 'MIN', 'PHILOS', 'Philosophy', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I060U', 'A', 'Russian Language UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I061U', 'A', 'Russian Culture UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I064U', 'A', 'South & SE Asian Studies UG', '25MNRSSEASN', 'South & SE Asian Stds Minors', 'MIN', 'SSEASN', 'South and Southeast Asian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I066U', 'A', 'Hispanic Lang & Linguistics UG', '25MNRSPANPOR', 'Spanish & Portuguese Minors', 'MIN', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I069U', 'A', 'Astrophysics UG', '25MNRASTRON', 'Astrophysics Minors', 'MIN', 'ASTRON', 'Astronomy', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I071U', 'A', 'Mathematics UG', '25MNRMATH', 'Mathematics Minors', 'MIN', 'MATH', 'Mathematics', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I075U', 'A', 'Anthropology UG', '25MNRANTHRO', 'Anthropology Minors', 'MIN', 'ANTHRO', 'Anthropology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I077U', 'A', 'Chicano Studies UG', '25MNRETHSTD', 'Ethnic Studies Minors', 'MIN', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I078U', 'A', 'Demography UG', '25MNRDEMOG', 'Demography Minors', 'MIN', 'DEMOG', 'Demography', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I079U', 'A', 'Ethnic Studies UG', '25MNRETHSTD', 'Ethnic Studies Minors', 'MIN', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I083U', 'A', 'Human Rights Interdisc UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I084U', 'A', 'LGBT Studies UG', '25MNRGWS', 'Gender & Womens Studies Minors', 'MIN', 'GWS', 'Gender and Womens Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I087U', 'A', 'Applied Language Studies UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I088U', 'A', 'Chinese Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I089U', 'A', 'Creative Writing UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I091U', 'A', 'European Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I093U', 'A', 'Japanese Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I102U', 'A', 'Interdisciplinary Stds UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I103U', 'A', 'Media Studies UG', '25MNRUGIS', 'UG Interdisc Studies Minors', 'MIN', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I105U', 'A', 'Economics UG', '25MNRECON', 'Economics Minors', 'MIN', 'ECON', 'Economics', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I108U', 'A', 'Asian Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I111U', 'A', 'Latin American Studies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I112U', 'A', 'Pol Econ Indus Societies UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I113U', 'A', 'Integrative Biology UG', '25MNRINTEGBI', 'Integrative Biology Minors', 'MIN', 'INTEGBI', 'Integrative Biology', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I117U', 'A', 'Near Eastern Studies UG', '25MNRNESTUD', 'Middle East Lang & Cul Minors', 'MIN', 'NESTUD', 'Middle Eastern Languages & Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I120U', 'A', 'Portuguese UG', '25MNRSPANPOR', 'Spanish & Portuguese Minors', 'MIN', 'SPANPOR', 'Spanish and Portuguese', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I125U', 'A', 'Tibetan UG', '25MNREALANG', 'East Asian Lang Culture Minors', 'MIN', 'EALANG', 'East Asian Languages and Cultures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I127U', 'A', 'Global Studies - Asia UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I129U', 'A', 'Global St - Middle East UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I130U', 'A', 'Global St - Europe & Russia UG', '25MNRISSP', 'Interdisc Soc Sci Pgms Minors', 'MIN', 'ISSP', 'Interdisciplinary Social Science Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I131U', 'A', 'Atmospheric Science UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I132U', 'A', 'Environmental Earth Science UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I133U', 'A', 'Geology UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I135U', 'A', 'Marine Science UG', '25MNREPS', 'Earth & Planetary Sci Minors', 'MIN', 'EPS', 'Earth and Planetary Science', 'LSMTHPSDIV', 'L&S Mathematical and Physical Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I140U', 'A', 'Dramatic Art UG', '25MNRTHEATER', 'Theater Dance Perf Stds Minors', 'MIN', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I141U', 'A', 'Dramatic Art - Dance UG', '25MNRTHEATER', 'Theater Dance Perf Stds Minors', 'MIN', 'THEATER', 'Theater, Dance, and Performance Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I143U', 'A', 'Literature in English UG', '25MNRENGLISH', 'English Minors', 'MIN', 'ENGLISH', 'English', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I145U', 'A', 'Women''s Studies UG', '25MNRGWS', 'Gender & Womens Studies Minors', 'MIN', 'GWS', 'Gender and Womens Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I152U', 'A', 'Early Dev & Learning Sci UG', '25MNRPSYCH', 'Psychology Minors', 'MIN', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I154U', 'A', 'Armenian Studies UG', '25MNRSLAVIC', 'Slavic Languages & Lit Minors', 'MIN', 'SLAVIC', 'Slavic Languages and Literatures', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I157U', 'A', 'Data Science UG', '25MNRDATASCI', 'Data Science Minors', 'MIN', 'LSDATASCI', 'Letters & Science Data Science', 'LSADMINPGM', 'L&S Administered Undergraduate Programs', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I162U', 'A', 'Ancient Grk & Roman Studies UG', '25MNRCLASSIC', 'Classics Minors', 'MIN', 'CLASSIC', 'Ancient Greek & Roman Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I165U', 'A', 'Health & Wellness UG', '25MNRPHYSED', 'Physical Education Minors', 'MIN', 'PHYSED', 'Physical Education', 'LSBIOSCDIV', 'L&S Biological Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I166U', 'A', 'Science, Tech, & Society UG', '25MNRSOCSCIOTHS', 'Other Social Sciences Minors', 'MIN', 'SOCSCIOTHS', 'Other Social Sciences Programs', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I167U', 'A', 'Transnational Italian UG', '25MNRITALIAN', 'Italian Studies Minors', 'MIN', 'ITALIAN', 'Italian Studies', 'LSARTHMDIV', 'L&S Arts and Humanities Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I169U', 'A', 'Clinical & Counseling Psych UG', '25MNRPSYCH', 'Psychology Minors', 'MIN', 'PSYCH', 'Psychology', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25I170U', 'A', 'Chicanx Latinx Studies UG', '25MNRETHSTD', 'Ethnic Studies Minors', 'MIN', 'ETHSTD', 'Ethnic Studies', 'LSSOCSCDIV', 'L&S Social Sciences Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('25INDU', 'A', 'L&S Individual Major BA', '25451', 'L&S Individual Major', 'MAJ', 'UGIS', 'Undergraduate Interdisciplinary Studies', 'LSUGSTDIV', 'L&S Undergraduate Studies Division', 'CLS', 'College of Letters and Science', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', 'AB', 'Bachelor of Arts'),
('25V03U', 'A', 'UC Davis Visitor L&S UG', '25V03', 'UC Davis Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V04ICVU', 'A', 'UC Los Angeles ICV L&S UG', '25V04', 'UC Los Angeles Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V04U', 'A', 'UC Los Angeles Visitor L&S UG', '25V04', 'UC Los Angeles Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V05U', 'A', 'UC Riverside Visitor L&S UG', '25V05', 'UC Riverside Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V06ICVU', 'A', 'UC San Diego ICV L&S UG', '25V06', 'UC San Diego Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V07U', 'A', 'UC Santa Cruz Visitor L&S UG', '25V07', 'UC Santa Cruz Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('25V08ICVU', 'A', 'UC Santa Barbara ICV LS UG', '25V08', 'UC Santa Barbara Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V09ICVU', 'A', 'UC Irvine ICV L&S UG', '25V09', 'UC Irvine Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UCLS', 'Undergrad Letters & Science', NULL, NULL),
('25V09U', 'A', 'UC Irvine Visitor L&S UG', '25V09', 'UC Irvine Visitor L&S', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('30FPFU', 'A', 'UCBX Fall Pgm First Semester', '30000', 'UCB Ext - FPF Undeclared', 'MAJ', 'FPFGENLDPT', 'UCB Extension Fall Program for Freshmen - General', 'FPFUGDIV', 'UCB Extension FPF - Undergraduate Division', 'UNEX', 'UC Berkeley Extension', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('30XCECCENG', 'A', 'UCBX Graduate Concurrent Enr', '30XCE', 'UCBX-Concurrent Enrollment', 'SS', 'UCBXCCEDPT', 'UCB Extension - Concurrent Enrollment Department', 'UCBXCCEDIV', 'UCB Extension - Concurrent Enrollment Division', 'UNEX', 'UC Berkeley Extension', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('30XCECCENI', 'A', 'UCBX Concurrent International', '30XCE', 'UCBX-Concurrent Enrollment', 'SS', 'UCBXCCEDPT', 'UCB Extension - Concurrent Enrollment Department', 'UCBXCCEDIV', 'UCB Extension - Concurrent Enrollment Division', 'UNEX', 'UC Berkeley Extension', 'UCBX', 'UC Berkeley Extension', 'XCCRT', 'UCBX Concurrent Enrollment', NULL, NULL),
('30XCECCENU', 'A', 'UCBX Undergrad Concurrent Enr', '30XCE', 'UCBX-Concurrent Enrollment', 'SS', 'UCBXCCEDPT', 'UCB Extension - Concurrent Enrollment Department', 'UCBXCCEDIV', 'UCB Extension - Concurrent Enrollment Division', 'UNEX', 'UC Berkeley Extension', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('70141BAHTG', 'A', 'Business Admin MBA-UCH JD CDP', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('70141BAJDG', 'A', 'Business Admin MBA-JD CDP', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('70141MSG', 'A', 'Business Administration MS', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('70141PHDG', 'A', 'Business Administration PhD', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('70141U', 'A', 'Business Administration BS', '70141', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'UGRD', 'Undergraduate', 'UBUS', 'Undergrad Business', 'BS', 'Bachelor of Science'),
('701C1MBAG', 'A', 'Berk-Columbia Exec MBA', '701C1', 'Berkeley-Columbia Exec MBA', 'SS', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '13', 'Master of Business Admin'),
('701E1MBAG', 'A', 'Evening & Weekend MBA', '701E1', 'Evening & Weekend MBA', 'SS', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '13', 'Master of Business Admin'),
('701F1C87G', 'A', 'Financial Eng Res Studies Cert', '701F1', 'Financial Engineering', 'CRT', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '87', 'Cert-Resident Studies'),
('702F7BAHTG', 'A', 'Business Admin MBA-UCL JD CDP', '702F7', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('702F7BAJDG', 'A', 'Business Admin MBA-JD CDP', '702F7', 'Business Administration', 'MAJ', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '13', 'Master of Business Admin'),
('70364MBAG', 'A', 'Berkeley MBA for Executives', '70364', 'Berkeley MBA for Executives', 'SS', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '13', 'Master of Business Admin'),
('70I107U', 'A', 'Business Administration UG', '70MNRBUS', 'Business Administration Minors', 'MIN', 'BUSDPT', 'Business', 'BUSDIV', 'Walter A. Haas School of Business (Division Lvl)', 'BUS', 'Walter A. Haas School of Business', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('71483JNJDG', 'A', 'Journalism MJ-JD CDP', '71483', 'Journalism', 'MAJ', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '25', 'Master of Journalism'),
('71483JNPHG', 'A', 'Journalism MJ-MPH CDP', '71483', 'Journalism', 'MAJ', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '25', 'Master of Journalism'),
('71483MJG', 'A', 'Journalism MJ', '71483', 'Journalism', 'MAJ', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '25', 'Master of Journalism'),
('71I164U', 'A', 'Journ Digital Citizenship UG', '71MNRJOURN', 'Journalism Minors', 'MIN', 'JOURNDPT', 'Journalism', 'JOURNDIV', 'Graduate School of Journalism (Division Lvl)', 'JOURN', 'Graduate School of Journalism', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('79248C83G', 'A', 'Ed Cred Pgm Single Subj Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '83', 'Crtfct-Educational Single Subj'),
('79248C90G', 'A', 'Ed Cred Pgm Lrn Hndc Spec Cert', '79248', 'Education Credential', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '90', 'Crtfct-Learning Handicapped Sp'),
('79249C81G', 'A', 'Education Admin Prelim Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, '81', 'Cert-Eductnl Admin Ser-Prelim'),
('79249C82G', 'A', 'Education Mult Subjects Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, '82', 'Crtfct-Eductnl Multiple Subj'),
('79249C84G', 'A', 'Education Pupil Personl Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '84', 'Crtfct-Educational Pupil Per'),
('79249C86G', 'A', 'Pupil Pers Svcs Sch Psych Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', NULL, NULL, '86', 'Crtfct-Educational Sch Pschgst'),
('79249C91G', 'A', 'Severely Handicapped Spec Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '91', 'Crtfct-Severely Handicapped Sp'),
('79249C93G', 'A', 'Education Math Specialist Cert', '79249', 'Education', 'CRT', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '93', 'Math Spec Credential'),
('79249CPHLG', 'A', 'Education CPhil', '79249', 'Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('79249EDDG', 'A', 'Education EdD', '79249', 'Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '55', 'Doctor of Education'),
('79892CPHLG', 'A', 'Special Ed Joint Pgm CPhil', '79892', 'Special Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('79892JPHDG', 'A', 'Special Ed Joint Pgm PhD', '79892', 'Special Education', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '63', 'Joint Doctor of Philosophy'),
('799A5MAG', 'A', 'Educational Leadership MA', '799A5', 'Educational Leadership', 'MAJ', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', 'MA', 'Master of Arts'),
('79I106U', 'A', 'Intdsc Stds Early Child UG', '79MNREDUC', 'Education Minors', 'MIN', 'EDUCDPT', 'Education', 'EDUCDIV', 'Berkeley School of Education (Division Lvl)', 'EDUCATION', 'Berkeley School of Education', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('812E0MIDSG', 'A', 'Info & Data Science MIDS', '812E0', 'Info & Data Science-MIDS', 'SS', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '99', 'Master of Info & Data Science'),
('81461PHDG', 'A', 'Information Science PhD', '81461', 'Information Science', 'MAJ', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('81504C79G', 'A', 'Library Media Teach Svcs Cert', '81504', 'Library & Info Studies', 'CRT', 'LINFOST', 'Library and Information Studies', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '79', 'Library Media Teach Serv Cred'),
('81504C80G', 'A', 'Library & Info Studies Cert', '81504', 'Library & Info Studies', 'CRT', 'LINFOST', 'Library and Information Studies', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '80', 'Cert-Grad Curr Lib and Info St'),
('81776CWOG', 'A', 'Info Mgmt & Systems CWO', '81776', 'Info Mgmt & Systems', 'MAJ', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('81776PHDG', 'A', 'Info Mgmt & Systems PhD', '81776', 'Info Mgmt & Systems', 'MAJ', 'INFODPT', 'Information', 'INFODIV', 'School of Information (Division Lvl)', 'INFO', 'School of Information', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('822E2MPAG', 'A', 'Public Affairs MPA', '822E2', 'Public Affairs', 'SS', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', 'W1', 'Master of Public Affairs'),
('82790CWOG', 'A', 'Public Policy CWO', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('82790MPPG', 'A', 'Public Policy MPP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPIEG', 'A', 'Public Policy MPP-IEOR MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPMEG', 'A', 'Pub Policy MPP-Mech Eng MS CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPPHG', 'A', 'Public Policy MPP-MPH CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82790PPSWG', 'A', 'Public Policy MPP-MSW CDP', '82790', 'Public Policy', 'MAJ', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '33', 'Master of Public Policy'),
('82I100U', 'A', 'Public Policy UG', '82MNRPUBPOL', 'Public Policy Minors', 'MIN', 'PUBPOLDPT', 'Public Policy', 'PUBPOLDIV', 'Goldman School of Public Policy (Division Lvl)', 'PUBPOL', 'Richard and Rhoda Goldman School of Public Policy', 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('84485JPJDG', 'A', 'Law JSP-JD CDP', '84485', 'Jurisprudence & Social Policy', 'MAJ', 'GGJSP', 'Jurisprudence and Social Policy Graduate Program', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', 'PD', 'Doctor of Philosophy'),
('84485MAG', 'A', 'JSP MA', '84485', 'Jurisprudence & Social Policy', 'MAJ', 'GGJSP', 'Jurisprudence and Social Policy Graduate Program', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LACAD', 'Law Academic Programs', 'MA', 'Master of Arts'),
('84501CWOG', 'A', 'Law JD CWO', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LNODG', 'Law Non-Degree/Non-FinAid', NULL, NULL),
('84501JDASG', 'A', 'Law JD-Asn St MA CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDCPG', 'A', 'Law JD-MCP CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDEAG', 'A', 'Law JD-Energy & Res MA CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDJNG', 'A', 'Law JD-Journalism MJ CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('84501JDPPG', 'A', 'Law JD-MPP CDP', '84501', 'Law (JD)', 'MAJ', 'LAWDPT', 'Law', 'LAWDIV', 'School of Law (Division Lvl)', 'LAW', 'School of Law', 'LAW', 'Law', 'LPRFL', 'Law Professional Programs', '68', 'Juris Doctor'),
('860EZFSWAG', 'A', 'Flex MSW - Advanced Standing', '860EZ', 'Flexible Master of Soc Welfare', 'SS', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GSSDP', 'Graduate Self-Supporting Pgms', '38', 'Master of Social Welfare'),
('86864C84G', 'A', 'Soc Welfare Ed Pupil Pers Cert', '86864', 'Social Welfare', 'CRT', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', NULL, NULL, '84', 'Crtfct-Educational Pupil Per'),
('86864DSWG', 'A', 'Social Welfare DSW', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '66', 'Doctor of Social Welfare'),
('86864SWJDG', 'A', 'Social Welfare MSW-JD CDP', '86864', 'Social Welfare', 'MAJ', 'SOCWELDPT', 'Social Welfare', 'SOCWELDIV', 'School of Social Welfare (Division Lvl)', 'SOCWEL', 'School of Social Welfare', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '38', 'Master of Social Welfare'),
('91008U', 'A', 'Optometry Limited UG', '91008', 'Optometry Limited', 'HS', 'OPTOMDPT', 'Optometry', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('91612ODG', 'A', 'Optometry OD', '91612', 'Optometry', 'HS', 'OPTOMDPT', 'Optometry', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '62', 'Doctor of Optometry'),
('91612U', 'A', 'Optometry BS', '91612', 'Optometry', 'HS', 'OPTOMDPT', 'Optometry', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'UGRD', 'Undergraduate', 'UOPTM', 'Undergrad Optometry', 'BS', 'Bachelor of Science'),
('91613C89G', 'A', 'Optometric Residency Cert', '91613', 'Optometric Residency Cert', 'CRT', 'OPTOMDPT', 'Optometry', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '89', 'Certificate-Grad Optometry'),
('91935CWOG', 'A', 'Vision Science CWO', '91935', 'Vision Science', 'MAJ', 'GGVISCI', 'Vision Science Graduate Group', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('91935MSG', 'A', 'Vision Science MS', '91935', 'Vision Science', 'MAJ', 'GGVISCI', 'Vision Science Graduate Group', 'OPTOMDIV', 'Optometry & Vision Science (Division Lvl)', 'OPTOM', 'Herbert Wertheim School of Optometry & Vision Sci', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('96132CPHLG', 'A', 'Biostatistics CPhil', '96132', 'Biostatistics', 'HS', 'GGBSTAT', 'Biostatistics Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '48', 'Candidate in Philosophy'),
('96132CWOG', 'A', 'Biostatistics CWO', '96132', 'Biostatistics', 'HS', 'GGBSTAT', 'Biostatistics Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('96132MSG', 'A', 'Biostatistics MS', '96132', 'Biostatistics', 'HS', 'GGBSTAT', 'Biostatistics Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('96354CWOG', 'A', 'Environ Health Sciences CWO', '96354', 'Environ Health Sciences', 'HS', 'GGEHS', 'Environmental Health Sciences Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('96354MSG', 'A', 'Environ Health Sciences MS', '96354', 'Environ Health Sciences', 'HS', 'GGEHS', 'Environmental Health Sciences Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('96357CWOG', 'A', 'Epidemiology CWO', '96357', 'Epidemiology', 'HS', 'GGEPIDM', 'Epidemiology Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('96357MPHG', 'A', 'Epidemiology MPH', '96357', 'Epidemiology', 'HS', 'GGEPIDM', 'Epidemiology Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', '36', 'Master of Public Health'),
('96357MSG', 'A', 'Epidemiology MS', '96357', 'Epidemiology', 'HS', 'GGEPIDM', 'Epidemiology Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('96357PHDG', 'A', 'Epidemiology PhD', '96357', 'Epidemiology', 'HS', 'GGEPIDM', 'Epidemiology Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'PD', 'Doctor of Philosophy'),
('96424MSG', 'A', 'HMS - Genetic Counseling MS', '96424', 'HMS - Genetic Counseling', 'HS', 'GGHMS', 'Health and Medical Sciences Graduate Group', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MS', 'Master of Science'),
('96447MAG', 'A', 'Immunology MA', '96447', 'Immunology', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GACAD', 'Graduate Academic Programs', 'MA', 'Master of Arts'),
('967895YPHG', 'A', 'Public Health 4+1 MPH', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96789CWOG', 'A', 'Public Health CWO', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('96789DPHG', 'A', 'Public Health DPH', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '65', 'Doctor of Public Health'),
('96789MPHG', 'A', 'Public Health MPH', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96789PHPPG', 'A', 'Public Health MPH-MPP CDP', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96789PHSFG', 'A', 'Public Health MPH-UCSF MD CDP', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('96789PHSWG', 'A', 'Public Health MPH-MSW CDP', '96789', 'Public Health', 'HS', 'PUBHLTHDPT', 'Public Health', 'PUBHLTHDIV', 'School of Public Health (Division Lvl)', 'PUBHEALTH', 'School of Public Health', 'GRAD', 'Graduate', 'GPRFL', 'Graduate Professional Programs', '36', 'Master of Public Health'),
('99000G', 'A', 'Summer Domestic Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99000INTG', 'A', 'Summer Internatnl Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99000INTU', 'A', 'Summer Internatnl Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99000U', 'A', 'Summer Domestic Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V00G', 'A', 'Summer Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V03U', 'A', 'Summer UC Davis Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V04G', 'A', 'Summer UC Los Angeles Vis GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V04U', 'A', 'Summer UC Los Angeles Vis UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V06U', 'A', 'Summer UC San Diego Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V08U', 'A', 'Summer UC Santa Barbara Vis UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V09G', 'A', 'Summer UC Irvine Visitor GR', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'GRAD', 'Graduate', 'GNODG', 'Graduate Non-Degree/Non-FinAid', NULL, NULL),
('99V09U', 'A', 'Summer UC Irvine Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('99V10U', 'A', 'Summer UC Merced Visitor UG', '99000', 'Summer Session Undeclared', 'MAJ', 'EVCPOTHDPT', 'Other Executive Vice Chancellor & Provost Programs', 'EVCPOTHDIV', 'Other Executive VC & Provost Pgms (Division Lvl)', 'EVCPOTHER', 'Other Executive Vice Chancellor & Provost Programs', 'UGRD', 'Undergraduate', 'UNODG', 'Undergrad Non-Degree/NonFinAid', NULL, NULL),
('A5201U', 'A', 'Computer Science BA', NULL, NULL, 'MAJ', NULL, NULL, NULL, NULL, NULL, NULL, 'UGRD', 'Undergraduate', 'UCDSS', 'Undergrad Comp Data Sci & Soc', 'AB', 'Bachelor of Arts'),
('A5891U', 'A', 'Statistics BA', NULL, NULL, 'MAJ', NULL, NULL, NULL, NULL, NULL, NULL, 'UGRD', 'Undergraduate', 'UCDSS', 'Undergrad Comp Data Sci & Soc', 'AB', 'Bachelor of Arts'),
('A5I172U', 'A', 'Data Science UG', NULL, NULL, 'MIN', NULL, NULL, NULL, NULL, NULL, NULL, 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('A5I173U', 'A', 'Statistics UG', NULL, NULL, 'MIN', NULL, NULL, NULL, NULL, NULL, NULL, 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL),
('PRE01PMEDU', 'A', 'Pre-Med/Health Sci Advising UG', NULL, NULL, 'PRP', NULL, NULL, NULL, NULL, NULL, NULL, 'UGRD', 'Undergraduate', NULL, NULL, NULL, NULL);

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

INSERT INTO student.academic_standing
(sid, term_id, acad_standing_action, acad_standing_status, action_date)
VALUES
('11667051', '2162', 'GS', 'GST', '2016-05-31'),
('11667051', '2172', 'GS', 'GST', '2017-05-31'),
('11667051', '2175', 'GS', 'GST', '2017-08-15'),
('11667051', '2178', 'AP', 'PRO', '2017-12-30'),
('11667051', '2182', 'PE', 'GST', '2018-05-31'),
('2345678901', '2172', 'SD', 'SUB', '2017-05-31'),
('2345678901', '2175', 'GS', 'GST', '2017-08-15'),
('3456789012', '2178', 'GS', 'GST', '2017-12-30'),
('5678901234', '2178', 'GS', 'GST', '2017-12-30');

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

INSERT INTO student.intended_majors
(sid, major)
VALUES
('11667051', 'Global Studies BA'),
('11667051', 'Electrical Eng & Comp Sci BS'),
('2345678901', 'Letters & Sci Undeclared UG'),
('3456789012', 'Public Health BA'),
('5678901234', 'Letters & Sci Undeclared UG'),
('8901234567', 'Economics BA'),
('890127492', 'Mathematics PhD'),
('9100000000', 'Engineering Undeclared UG');

INSERT INTO student.minors
(sid, minor)
VALUES
('11667051', 'Computer Science UG'),
('11667051', 'Physics UG');

INSERT INTO student.student_degrees
(sid, plan, date_awarded, term_id)
VALUES
('9100000000', 'Electrical Eng & Comp Sci BS', '2021-05-16', '2212'),
('2718281828', 'Nuclear Engineering BS', '2020-05-16', '2202'),
('3141592653', 'Philosophy BA', '2020-05-16', '2202'),
('11667051', 'Ed Cred Pgm Single Subj Cert', '1996-05-25', '1962');

INSERT INTO student.student_holds
(sid, feed)
VALUES
('5678901234', :holds_5678901234_S01),
('5678901234', :holds_5678901234_V00);

INSERT INTO student.student_incompletes
(sid, term_id, status, frozen, lapse_date, grade)
VALUES
('3141592653', '2052', 'I', FALSE, '2022-12-31', 'I');

INSERT INTO student.student_profiles
(sid, profile, profile_summary)
VALUES
('11667051', :profile_11667051, :profile_summary_11667051),
('2345678901', :profile_2345678901, :profile_summary_2345678901),
('3456789012', :profile_3456789012, :profile_summary_3456789012),
('5678901234', :profile_5678901234, :profile_summary_5678901234),
('7890123456', :profile_7890123456, :profile_summary_7890123456),
('8901234567', :profile_8901234567, :profile_summary_8901234567),
('890127492', :profile_890127492, :profile_summary_890127492),
('9000000000', :profile_9000000000, :profile_summary_9000000000),
('9100000000', :profile_9100000000, :profile_summary_9100000000),
('2718281828', :profile_completed_2718281828, :profile_summary_completed_2718281828),
('3141592653', :profile_inactive_3141592653, :profile_summary_inactive_3141592653),
('9191919191', :profile_inactive_9191919191, :profile_summary_inactive_9191919191);

INSERT INTO student.student_profile_index
(sid, uid, first_name, last_name, level, gpa, units, transfer, email_address, entering_term, expected_grad_term, terms_in_attendance, academic_career_status)
VALUES
('11667051', '61889', 'Deborah', 'Davies', NULL, 3.8, 0, FALSE, 'barnburner@berkeley.edu', '2158', '2198', NULL, 'active'),
('2345678901', '98765', 'Dave', 'Doolittle', '30', 3.495, 34, FALSE, 'debaser@berkeley.edu', '2155', '2192', 4, 'active'),
('3456789012', '242881', 'Pauline', 'Kerschen', '30', 3.005, 70, FALSE, 'doctork@berkeley.edu', '2152', '2192', 5, 'active'),
('5678901234', '9933311', 'Sandeep', 'Jayaprakash', '40', 3.501, 102, FALSE, 'ilovela@berkeley.edu', '2155', '2192', NULL, 'active'),
('7890123456', '1049291', 'Paul', 'Farestveit', '40', 3.9, 110, FALSE, 'qadept@berkeley.edu', '2155', '2202', 2, 'active'),
('8901234567', '123456', 'John David', 'Crossman', '10', 1.85, 12, FALSE, 'mrwonderful@berkeley.edu', '1938', '1978', 2, 'active'),
('890127492', '211159', 'Siegfried', 'Schlemiel', '20', 0.4, 8, FALSE, 'neerdowell@berkeley.edu', '2155', '2192', 2, 'active'),
('9000000000', '300847', 'Wolfgang', 'Pauli-O''Rourke', '20', 2.3, 55, TRUE, 'wpo@berkeley.edu', '2155', '2202', 2, 'active'),
('9100000000', '300848', 'Nora Stanton', 'Barney', '20', 3.85, 60, TRUE, 'nsb@berkeley.edu', '2155', '2192', 2, 'active'),
('2718281828', '271828', 'Ernest', 'Pontifex', 'GR', 4, 139, FALSE, 'ep@berkeley.edu', '2048', '2102', 12, 'completed'),
('3141592653', '314159', 'Johannes', 'Climacus', '40', 2.784, 149.6, FALSE, 'jc@berkeley.edu', '2155', '2118', 9, 'inactive'),
('9191919191', '191919', 'Paul', 'Tarsus', NULL, NULL, NULL, FALSE, NULL, NULL, NULL, NULL, 'inactive');

INSERT INTO student.student_majors
(sid, college, major, division)
VALUES
('11667051', 'Undergrad Letters & Science', 'English BA', 'L&S Arts & Humanities Division'),
('11667051', 'Undergrad Engineering', 'Nuclear Engineering BS', 'Clg of Engineering'),
('2345678901', 'Undergrad Chemistry', 'Chemistry BS', 'Clg of Chemistry'),
('3456789012', 'Undergrad Letters & Science', 'English BA', 'L&S Arts & Humanities Division'),
('3456789012', 'Undergrad Letters & Science', 'Political Economy BA', 'L&S Social Sciences Division'),
('5678901234', 'Undergrad Letters & Science', 'Letters & Sci Undeclared UG', 'L&S Undeclared'),
('7890123456', 'Undergrad Engineering', 'Nuclear Engineering BS', 'Clg of Engineering'),
('8901234567', 'Undergrad Letters & Science', 'Economics BA', 'L&S Social Sciences Division'),
('890127492', 'Graduate Academic Programs', 'Mathematics PhD', 'L&S Math & Phys Sciences Div'),
('9000000000', 'Undergrad Engineering', 'Engineering Undeclared UG', 'Clg of Engineering'),
('9100000000', 'Undergrad Engineering', 'Engineering Undeclared UG', 'Clg of Engineering'),
('2718281828', 'Undergrad Letters & Science', 'English BA', 'L&S Arts & Humanities Division');


INSERT INTO student.student_names
(sid, name)
VALUES
('11667051', 'DAVIES'),
('11667051', 'DEBORAH'),
('2345678901', 'DAVE'),
('2345678901', 'DOOLITTLE'),
('3456789012', 'KERSCHEN'),
('3456789012', 'PAULINE'),
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
(sid, term_id, enrollment_term, midpoint_deficient_grade, incomplete_grade, enrolled_units, term_gpa)
VALUES
('11667051', '2012', :enrollment_term_11667051_2012, FALSE, FALSE, 0.0, NULL),
('11667051', '2162', :enrollment_term_11667051_2162, FALSE, FALSE, 0.0, 3.8),
('11667051', '2172', :enrollment_term_11667051_2172, FALSE, FALSE, 10.0, 2.7),
('11667051', '2175', :enrollment_term_11667051_2175, FALSE, FALSE, 0.0, NULL),
('11667051', '2178', :enrollment_term_11667051_2178, TRUE, FALSE, 12.5, 1.8),
('11667051', '2182', :enrollment_term_11667051_2182, FALSE, FALSE, 3.0, 2.9),
('2345678901', '2172', :enrollment_term_2345678901_2172, FALSE, FALSE, 10.0, 3.5),
('2345678901', '2175', :enrollment_term_2345678901_2175, FALSE, FALSE, 4.0, 0.0),
('3456789012', '2178', :enrollment_term_3456789012_2178, FALSE, FALSE, 5.0, 3.2),
('5678901234', '2178', :enrollment_term_5678901234_2178, FALSE, FALSE, 7.0, 2.1),
('2718281828', '2058', :enrollment_term_completed_2718281828_2058, FALSE, FALSE, 10.0, 3.0),
('2718281828', '2102', :enrollment_term_completed_2718281828_2102, FALSE, FALSE, 10.0, 3.0),
('3141592653', '2052', :enrollment_term_inactive_3141592653_2052, FALSE, TRUE, 10.0, 3.0);


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

INSERT INTO student.visas
(sid, visa_status, visa_type)
VALUES
('2345678901', 'G', 'F1'),
('3456789012', 'A', 'J1'),
('5678901234', 'G', 'OT');

INSERT INTO terms.current_term_index
(current_term_name, future_term_name)
VALUES
('Fall 2017', 'Spring 2018');

INSERT INTO terms.term_definitions
(term_id, term_name, term_begins, term_ends)
VALUES
('2188', 'Fall 2018', '2018-08-15', '2018-12-14'),
('2185', 'Summer 2018', '2018-05-21', '2018-08-10'),
('2182', 'Spring 2018', '2018-01-09', '2018-05-11'),
('2178', 'Fall 2017', '2017-08-16', '2017-12-15'),
('2175', 'Summer 2017', '2017-05-22', '2017-08-11'),
('2172', 'Spring 2017', '2017-01-10', '2017-05-12'),
('2168', 'Fall 2016', '2016-08-17', '2016-12-16');
