-- Select ticket core fields + most recent comments (concatenated)
-- Params: ticket_id (parameter), max_comments (parameter)
-- Template placeholders: ${PROJECT_ID} ${DATASET}
WITH base AS (
  SELECT ticket_id, title, body, severity, component
  FROM `${PROJECT_ID}.${DATASET}.tickets`
  WHERE ticket_id = @ticket_id
),
comments AS (
  SELECT text, ts
  FROM `${PROJECT_ID}.${DATASET}.ticket_events`
  WHERE ticket_id = @ticket_id AND type = 'comment'
  ORDER BY ts DESC
  LIMIT @max_comments
)
SELECT
  b.ticket_id,
  b.title,
  b.body,
  b.severity,
  b.component,
  ARRAY_TO_STRING(ARRAY(SELECT CONCAT(FORMAT_TIMESTAMP('%Y-%m-%d %H:%M', ts), ': ', text) FROM comments), '\n') AS recent_comments
FROM base b;
