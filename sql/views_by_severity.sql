-- Issues By Severity (weekly buckets)
-- PLACEHOLDERS: ${PROJECT_ID}, ${DATASET}
CREATE OR REPLACE VIEW `${PROJECT_ID}.${DATASET}.view_issues_by_severity` AS
WITH src AS (
  SELECT
    COALESCE(
      SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(meta, '$.ingested_at')),
      SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', JSON_VALUE(meta, '$.ingested_at')),
      SAFE.TIMESTAMP(JSON_VALUE(meta, '$.ingested_at_ts')),
      TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 0 SECOND)
    ) AS ingested_ts,
    CASE
      WHEN LOWER(JSON_VALUE(meta, '$.severity')) = 'p0' THEN 'P0'
      WHEN LOWER(JSON_VALUE(meta, '$.severity')) IN ('p1','high') THEN 'P1'
      WHEN LOWER(JSON_VALUE(meta, '$.severity')) IN ('p2','medium') THEN 'P2'
      WHEN LOWER(JSON_VALUE(meta, '$.severity')) IN ('p3','low') THEN 'P3'
      ELSE 'Unknown'
    END AS severity
  FROM `${PROJECT_ID}.${DATASET}.chunks`
)
SELECT
  DATE_TRUNC(ingested_ts, WEEK(MONDAY)) AS week,
  severity,
  COUNT(*) AS count
FROM src
GROUP BY week, severity
ORDER BY week, severity;
