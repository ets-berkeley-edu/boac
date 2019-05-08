UPDATE cohort_filters
SET filter_criteria = jsonb_set(filter_criteria, '{genders}', UPPER(filter_criteria->>'genders')::jsonb, false)
WHERE filter_criteria->>'genders' IS NOT NULL;
