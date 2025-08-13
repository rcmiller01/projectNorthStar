-- Example embedding generation (parameterized)
-- Variables to substitute client-side: ${PROJECT_ID}, ${DATASET}, ${SOURCE_TABLE}, ${TARGET_TABLE}, ${TEXT_COLUMN}
-- NOTE: In real execution ensure TARGET_TABLE exists or use CREATE TABLE AS SELECT.

INSERT INTO `${PROJECT_ID}.${DATASET}.${TARGET_TABLE}` (id, embedding)
SELECT
  id,
  ML.GENERATE_EMBEDDING(MODEL `${PROJECT_ID}.${DATASET}.embedding_model`, ${TEXT_COLUMN}) AS embedding
FROM `${PROJECT_ID}.${DATASET}.${SOURCE_TABLE}`
WHERE ${TEXT_COLUMN} IS NOT NULL;
