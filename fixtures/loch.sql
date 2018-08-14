DROP SCHEMA IF EXISTS boac_advising_asc cascade;
DROP SCHEMA IF EXISTS boac_advising_coe cascade;
DROP SCHEMA IF EXISTS student cascade;

CREATE SCHEMA boac_advising_asc;
CREATE SCHEMA boac_advising_coe;
CREATE SCHEMA student;

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
    advisor_ldap_uid VARCHAR
);

CREATE TABLE boac_advising_coe.student_profiles
(
    sid VARCHAR NOT NULL,
    profile TEXT NOT NULL
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
    units DECIMAL (4,1)
);

CREATE TABLE student.student_majors
(
    sid VARCHAR NOT NULL,
    major VARCHAR NOT NULL
);

CREATE TABLE student.student_enrollment_terms
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    enrollment_term TEXT NOT NULL
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
(sid, advisor_ldap_uid)
VALUES
('11667051', '90412'),
('7890123456', '1133399'),
('9000000000', '1133399'),
('9100000000', '90412');

INSERT INTO boac_advising_coe.student_profiles
(sid, profile)
VALUES
('11667051', :coe_profile_11667051),
('7890123456', :coe_profile_7890123456),
('9000000000', :coe_profile_9000000000),
('9100000000', :coe_profile_9100000000);

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
(sid, uid, first_name, last_name, level, gpa, units)
VALUES
('11667051', '61889', 'Deborah', 'Davies', NULL, NULL, 0),
('2345678901', '98765', 'Dave', 'Doolittle', '30', 3.495, 34),
('3456789012', '242881', 'Paul', 'Kerschen', '30', 3.005, 70),
('5678901234', '9933311', 'Sandeep', 'Jayaprakash', '40', 3.501, 102),
('7890123456', '1049291', 'Paul', 'Farestveit', '40', 3.9, 110),
('8901234567', '123456', 'John David', 'Crossman', '10', 1.85, 12),
('890127492', '211159', 'Siegfried', 'Schlemiel', '20', 0.4, 8),
('9000000000', '300847', 'Wolfgang', 'Pauli', '20', 2.3, 55),
('9100000000', '300848', 'Nora Stanton', 'Barney', '20', 3.85, 60);

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

INSERT INTO student.student_enrollment_terms
(sid, term_id, enrollment_term)
VALUES
('11667051', '2162', :enrollment_term_11667051_2162),
('11667051', '2172', :enrollment_term_11667051_2172),
('11667051', '2178', :enrollment_term_11667051_2178),
('11667051', '2182', :enrollment_term_11667051_2182),
('2345678901', '2172', :enrollment_term_2345678901_2172);
