BEGIN;

CREATE TYPE degree_progress_category_types AS ENUM ('Category', 'Subcategory', 'Course');

CREATE TABLE degree_progress_categories (
    id integer NOT NULL,
    parent_category_id integer,
    template_id integer NOT NULL,
    category_type degree_progress_category_types NOT NULL,
    course_units integer,
    description text,
    name character varying(255) NOT NULL,
    position integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
ALTER TABLE degree_progress_categories OWNER TO app_boa;
CREATE SEQUENCE degree_progress_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE degree_progress_categories_id_seq OWNER TO app_boa;
ALTER SEQUENCE degree_progress_categories_id_seq OWNED BY degree_progress_categories.id;
ALTER TABLE ONLY degree_progress_categories ALTER COLUMN id SET DEFAULT nextval('degree_progress_categories_id_seq'::regclass);
ALTER TABLE ONLY degree_progress_categories
    ADD CONSTRAINT degree_progress_categories_pkey PRIMARY KEY (id);
ALTER TABLE ONLY degree_progress_categories
    ADD CONSTRAINT degree_progress_categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES degree_progress_categories(id) ON DELETE CASCADE;
ALTER TABLE ONLY degree_progress_categories
    ADD CONSTRAINT degree_progress_categories_template_id_fkey FOREIGN KEY (template_id) REFERENCES degree_progress_templates(id) ON DELETE CASCADE;
CREATE INDEX degree_progress_categories_id_idx ON degree_progress_categories USING btree (template_id);

COMMIT;
