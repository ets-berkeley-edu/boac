BEGIN;

ALTER TABLE cohort_filters ALTER COLUMN owner_id SET NOT NULL;
ALTER TABLE ONLY cohort_filters
    ADD CONSTRAINT cohort_filters_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES authorized_users(id) ON DELETE CASCADE;

DROP TABLE cohort_filter_owners CASCADE;

COMMIT;
