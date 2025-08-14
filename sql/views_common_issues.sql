-- Common Issues View
-- Derives a naive fingerprint for chunks to aggregate recurring issues.
-- PLACEHOLDERS: ${PROJECT_ID}, ${DATASET}
CREATE OR REPLACE VIEW `${PROJECT_ID}.${DATASET}.view_common_issues` AS
WITH base AS (
  SELECT
    chunk_id,
    text,
    meta,
    COALESCE(
      SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(meta, '$.ingested_at')),
      SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', JSON_VALUE(meta, '$.ingested_at')),
      SAFE.TIMESTAMP(JSON_VALUE(meta, '$.ingested_at_ts')),
      TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 0 SECOND)
    ) AS ingested_ts
  FROM `${PROJECT_ID}.${DATASET}.chunks`
), cleaned AS (
  SELECT
    chunk_id,
    -- lowercase + strip punctuation to spaces
    REGEXP_REPLACE(LOWER(text), r'[^a-z0-9\s]', ' ') AS lower_alnum,
    text,
    ingested_ts
  FROM base
), normalized AS (
  SELECT
    chunk_id,
    -- collapse whitespace then remove common stopwords
    REGEXP_REPLACE(
      REGEXP_REPLACE(lower_alnum, r'\s+', ' '),
      r'\b(the|a|an|and|or|to|of|for|in|on)\b',
      ''
    ) AS no_stop,
    text,
    ingested_ts
  FROM cleaned
), tokens AS (
  SELECT
    chunk_id,
    SPLIT(TRIM(no_stop), ' ') AS words,
    text,
    ingested_ts
  FROM normalized
), fingerprints AS (
  SELECT
    -- first 8 words after normalization become the fingerprint key
    (SELECT STRING_AGG(word, ' ' ORDER BY offset LIMIT 8)
       FROM UNNEST(words) AS word WITH OFFSET) AS fingerprint,
    text,
    ingested_ts
  FROM tokens
)
SELECT
  fingerprint,
  ANY_VALUE(SUBSTR(text, 1, 200)) AS issue_example,
  COUNT(*) AS count,
  MAX(ingested_ts) AS last_seen
FROM fingerprints
WHERE fingerprint IS NOT NULL AND fingerprint != ''
GROUP BY fingerprint
ORDER BY count DESC;
