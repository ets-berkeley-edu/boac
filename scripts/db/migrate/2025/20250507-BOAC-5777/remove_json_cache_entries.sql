BEGIN;

DELETE FROM json_cache WHERE
  key IN ('all_team_groups')
  OR
  key LIKE 'cohort_filter_options_%';

COMMIT;
