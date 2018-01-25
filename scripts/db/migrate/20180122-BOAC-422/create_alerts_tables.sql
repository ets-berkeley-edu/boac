BEGIN;

CREATE TABLE alerts (
  id SERIAL NOT NULL,
  sid VARCHAR(80) NOT NULL REFERENCES students (sid) ON DELETE CASCADE,
  alert_type VARCHAR(80) NOT NULL,
  key VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  active BOOLEAN DEFAULT TRUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL,

  PRIMARY KEY (id)
);

CREATE INDEX alerts_sid_idx ON alerts (sid);

ALTER TABLE alerts ADD CONSTRAINT alerts_sid_alert_type_key_unique_constraint UNIQUE (sid, alert_type, key);

CREATE TABLE alert_views (
  alert_id INTEGER NOT NULL REFERENCES alerts (id) ON DELETE CASCADE,
  viewer_id INTEGER NOT NULL REFERENCES authorized_users (id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  dismissed_at TIMESTAMP WITH TIME ZONE,

  PRIMARY KEY (alert_id, viewer_id)
);

CREATE INDEX alert_views_alert_id_idx ON alert_views (alert_id);
CREATE INDEX alert_views_viewer_id_idx ON alert_views (viewer_id);

COMMIT;
