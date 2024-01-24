BEGIN;

ALTER TYPE appointment_event_types OWNER TO app_boa;
ALTER TYPE university_dept_member_role_type OWNER TO app_boa;
ALTER TYPE cohort_filter_event_types OWNER TO app_boa;
ALTER TYPE cohort_domain_types OWNER TO app_boa;

COMMIT;
