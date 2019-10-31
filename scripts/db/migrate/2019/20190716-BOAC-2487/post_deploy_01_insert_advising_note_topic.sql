BEGIN;

-- New column to support soft-deletes
ALTER TABLE topics ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

-- Additions
INSERT INTO topics (topic, created_at) VALUES ('Minors', now()) ON CONFLICT DO NOTHING;
INSERT INTO topics (topic, created_at) VALUES ('Advising Holds', now()) ON CONFLICT DO NOTHING;
INSERT INTO topics (topic, created_at) VALUES ('AP/IB/GCE test units', now()) ON CONFLICT DO NOTHING;
INSERT INTO topics (topic, created_at) VALUES ('Breadth requirement(s)', now()) ON CONFLICT DO NOTHING;
INSERT INTO topics (topic, created_at) VALUES ('COCI', now()) ON CONFLICT DO NOTHING;
INSERT INTO topics (topic, created_at) VALUES ('Readmission After Dismissal', now()) ON CONFLICT DO NOTHING;

-- Modifications
UPDATE topics SET topic = 'Premed/Pre-Health Advising' WHERE topic = 'Pre-Med Advising';
UPDATE topics SET topic = 'Retroactive Add' WHERE topic = 'Retroactive Addition';

-- Deletions (soft)
UPDATE topics SET deleted_at = now() WHERE topic = 'Retroactive Grading Option';

COMMIT;
