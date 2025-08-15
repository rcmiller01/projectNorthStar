-- Get chunk details for neighbor expansion
-- Variables: ${PROJECT_ID}, ${DATASET}, ${CHUNK_IDS_ARRAY}
-- Returns chunk details needed for re-ranking

SELECT
  chunk_id,
  text,
  meta
FROM `${PROJECT_ID}.${DATASET}.chunks_emb`
WHERE chunk_id IN UNNEST(${CHUNK_IDS_ARRAY});
