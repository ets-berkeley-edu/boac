BEGIN;

ALTER TABLE advisor_watchlists DROP CONSTRAINT advisor_watchlists_sid_fkey;
ALTER TABLE advisor_watchlists DROP CONSTRAINT advisor_watchlists_watchlist_owner_uid_fkey;
ALTER TABLE advisor_watchlists DROP CONSTRAINT advisor_watchlists_pkey;

DROP TABLE advisor_watchlists CASCADE;

COMMIT;
