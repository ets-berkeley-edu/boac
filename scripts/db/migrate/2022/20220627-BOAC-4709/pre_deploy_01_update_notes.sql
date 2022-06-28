BEGIN;

CREATE TYPE note_contact_types AS ENUM (
    'Email',
    'Phone',
    'Online same day',
    'Online scheduled',
    'In-person same day',
    'In person scheduled',
    'Admin'
);

ALTER TABLE notes ADD COLUMN contact_type note_contact_types;
ALTER TABLE notes ADD COLUMN set_date DATE;

COMMIT;
