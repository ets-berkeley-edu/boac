BEGIN;

CREATE TABLE cohort_filters (
  id SERIAL NOT NULL,
  label VARCHAR(255) NOT NULL,
  filter_criteria TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (id)
);

CREATE TABLE cohort_filter_owners (
  cohort_filter_id INTEGER NOT NULL REFERENCES cohort_filters (id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES authorized_users (id) ON DELETE CASCADE,

  PRIMARY KEY (cohort_filter_id, user_id)
);

COMMIT;
