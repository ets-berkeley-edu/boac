BEGIN;

CREATE TABLE tool_settings (
  id SERIAL PRIMARY KEY,
  key VARCHAR(255) NOT NULL,
  value VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE tool_settings ADD CONSTRAINT tool_settings_key_unique_constraint UNIQUE (key);
CREATE INDEX tool_settings_key_idx ON tool_settings (key);

COMMIT;
