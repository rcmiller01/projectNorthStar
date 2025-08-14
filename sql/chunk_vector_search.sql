-- Vector search over chunk embeddings with provenance meta
-- Variables: ${PROJECT_ID}, ${DATASET}, ${TOP_K}, ${QUERY_TEXT}, ${EMBED_MODEL}
-- Multi-type filter supported via ${TYPE_ARRAY} literal (e.g., ['pdf','log'])
-- If empty array literal [] then no filtering.

WITH query_vec AS (
  SELECT ML.GENERATE_EMBEDDING(
    MODEL `${PROJECT_ID}.${DATASET}.${EMBED_MODEL}`,
    ${QUERY_TEXT} AS text
  ) AS qvec
)
SELECT
  vs.chunk_id,
  vs.distance,
  c.text,
  c.meta
FROM ML.VECTOR_SEARCH(
  TABLE `${PROJECT_ID}.${DATASET}.chunks_emb`,
  (SELECT qvec FROM query_vec),
  top_k => ${TOP_K}
) AS vs
JOIN `${PROJECT_ID}.${DATASET}.chunks_emb` c ON c.chunk_id = vs.chunk_id
WHERE (ARRAY_LENGTH(${TYPE_ARRAY}) = 0 OR JSON_VALUE(c.meta, '$.type') IN UNNEST(${TYPE_ARRAY}))
ORDER BY vs.distance ASC;
