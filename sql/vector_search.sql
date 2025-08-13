-- Phase 0 Vector Search
-- Variables: ${PROJECT_ID}, ${DATASET}, ${EMBED_MODEL}, ${QUERY_TEXT}, ${TOP_K}

WITH query_vec AS (
  SELECT ML.GENERATE_EMBEDDING(
    MODEL `${PROJECT_ID}.${DATASET}.${EMBED_MODEL}`,
    ${QUERY_TEXT} AS text
  ) AS qvec
)
SELECT
  vs.id,
  vs.distance,
  t.text
FROM ML.VECTOR_SEARCH(
  TABLE `${PROJECT_ID}.${DATASET}.demo_texts_emb`,
  (SELECT qvec FROM query_vec),
  top_k => ${TOP_K}
) AS vs
JOIN `${PROJECT_ID}.${DATASET}.demo_texts_emb` t ON t.id = vs.id
ORDER BY vs.distance ASC;
