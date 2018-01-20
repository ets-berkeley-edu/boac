BEGIN;

CREATE TABLE advisor_watchlists (
  watchlist_owner_uid VARCHAR(80) REFERENCES authorized_users (uid) ON DELETE CASCADE,
  sid VARCHAR(80) REFERENCES students (sid) ON DELETE CASCADE,

  PRIMARY KEY (watchlist_owner_uid, sid)
);

COMMIT;
