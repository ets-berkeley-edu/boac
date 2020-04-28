BEGIN;

CREATE MATERIALIZED VIEW advisor_author_index AS (
  SELECT DISTINCT aa.* FROM (
    SELECT a.advisor_name, a.advisor_uid
    FROM appointments a
    UNION
    SELECT n.author_name AS advisor_name, n.author_uid AS advisor_uid
    FROM notes n
  ) aa
  ORDER BY aa.advisor_name
);
  
CREATE INDEX idx_advisor_author_index ON advisor_author_index USING btree(advisor_name);

COMMIT;