BEGIN;

CREATE TABLE user_logins (
  id SERIAL PRIMARY KEY,
  uid VARCHAR(255) NOT NULL REFERENCES authorized_users(uid) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX user_logins_uid_idx ON user_logins (uid);

COMMIT;