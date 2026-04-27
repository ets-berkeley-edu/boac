BEGIN;

ALTER TABLE notes ADD COLUMN parent_note_id INTEGER;

ALTER TABLE ONLY notes
    ADD CONSTRAINT notes_parent_note_id_fkey FOREIGN KEY (parent_note_id) REFERENCES notes(id) ON DELETE CASCADE;

COMMIT;
