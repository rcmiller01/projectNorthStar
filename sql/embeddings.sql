-- Phase 0 Embedding Generation
-- Variables: ${PROJECT_ID}, ${DATASET}, ${EMBED_MODEL}, ${SOURCE_TABLE}
-- Output table: `${PROJECT_ID}.${DATASET}.demo_texts_emb`

CREATE OR REPLACE TABLE `${PROJECT_ID}.${DATASET}.demo_texts_emb` AS
SELECT
  id,
  text,
  ML.GENERATE_EMBEDDING(
    MODEL `${PROJECT_ID}.${DATASET}.${EMBED_MODEL}`,
    text
  ) AS embedding
FROM `${PROJECT_ID}.${DATASET}.${SOURCE_TABLE}`
WHERE text IS NOT NULL;
