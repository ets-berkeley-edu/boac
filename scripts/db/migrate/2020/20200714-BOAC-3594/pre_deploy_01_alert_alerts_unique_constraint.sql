BEGIN;

ALTER TABLE alerts
    DROP CONSTRAINT alerts_sid_alert_type_key_unique_constraint;
ALTER TABLE alerts
    ADD CONSTRAINT alerts_sid_alert_type_key_created_at_unique_constraint UNIQUE (sid, alert_type, key, created_at);

COMMIT;
