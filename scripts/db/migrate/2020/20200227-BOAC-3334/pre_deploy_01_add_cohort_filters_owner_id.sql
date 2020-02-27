BEGIN;

ALTER TABLE cohort_filters ADD COLUMN owner_id INTEGER;
CREATE INDEX cohort_filters_owner_id_idx ON cohort_filters USING btree (owner_id);

UPDATE cohort_filters cf
    SET owner_id = cfo.user_id
    FROM cohort_filter_owners cfo
    WHERE cf.id = cfo.cohort_filter_id;

COMMIT;
