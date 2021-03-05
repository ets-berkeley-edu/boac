BEGIN;

CREATE TABLE degrees (
  id integer NOT NULL,
  name character varying(255) NOT NULL,
  created_at timestamp with time zone NOT NULL,
  created_by integer NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  updated_by integer NOT NULL,
  deleted_at timestamp with time zone,
  deleted_by integer
);
ALTER TABLE degrees OWNER TO app_boa;
CREATE SEQUENCE degrees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE degrees_id_seq OWNER TO app_boa;
ALTER SEQUENCE degrees_id_seq OWNED BY degrees.id;
ALTER TABLE ONLY degrees ALTER COLUMN id SET DEFAULT nextval('degrees_id_seq'::regclass);
ALTER TABLE ONLY degrees
    ADD CONSTRAINT degrees_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degrees
    ADD CONSTRAINT degrees_created_by_fkey FOREIGN KEY (created_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degrees
    ADD CONSTRAINT degrees_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES authorized_users(id) ON DELETE CASCADE;
ALTER TABLE ONLY degrees
    ADD CONSTRAINT degrees_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES authorized_users(id) ON DELETE CASCADE;

COMMIT;