BEGIN;

CREATE TYPE cohort_filter_event_types AS ENUM ('added', 'removed');

CREATE TABLE cohort_filter_events (
    id integer NOT NULL,
    cohort_filter_id integer NOT NULL,
    sid character varying(80) NOT NULL,
    event_type cohort_filter_event_types NOT NULL,
    created_at timestamp with time zone NOT NULL
);
ALTER TABLE cohort_filter_events OWNER TO boac;
CREATE SEQUENCE cohort_filter_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE cohort_filter_events_id_seq OWNER TO boac;
ALTER SEQUENCE cohort_filter_events_id_seq OWNED BY cohort_filter_events.id;
ALTER TABLE ONLY cohort_filter_events ALTER COLUMN id SET DEFAULT nextval('cohort_filter_events_id_seq'::regclass);
ALTER TABLE ONLY cohort_filter_events
    ADD CONSTRAINT cohort_filter_events_pkey PRIMARY KEY (id);

CREATE INDEX cohort_filter_events_cohort_filter_id_idx ON cohort_filter_events USING btree (cohort_filter_id);
CREATE INDEX cohort_filter_events_sid_idx ON cohort_filter_events USING btree (sid);
CREATE INDEX cohort_filter_events_event_type_idx ON cohort_filter_events USING btree (event_type);
CREATE INDEX cohort_filter_events_created_at_idx ON cohort_filter_events USING btree (created_at);

ALTER TABLE ONLY cohort_filter_events
    ADD CONSTRAINT cohort_filter_events_cohort_filter_id_fkey FOREIGN KEY (cohort_filter_id) REFERENCES cohort_filters(id) ON DELETE CASCADE;

COMMIT;
