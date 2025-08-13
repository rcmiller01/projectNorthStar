-- Phase 0 Text Generation (Optional Classification)
-- Variables: ${PROJECT_ID}, ${DATASET}, ${GEN_MODEL}, ${LIMIT}
-- Produces tiny JSON with severity & component guess per text row.

WITH raw AS (
  SELECT
    id,
    ML.GENERATE_TEXT(
      MODEL `${PROJECT_ID}.${DATASET}.${GEN_MODEL}`,
      CONCAT('Return JSON {"severity": <low|medium|high>, "component": <area>} for: ', text)
    ) AS output
  FROM `${PROJECT_ID}.${DATASET}.demo_texts`
  LIMIT ${LIMIT}
)
SELECT
  id,
  output AS raw_output,
  SAFE.JSON_EXTRACT_SCALAR(output, '$.severity') AS severity,
  SAFE.JSON_EXTRACT_SCALAR(output, '$.component') AS component
FROM raw;
