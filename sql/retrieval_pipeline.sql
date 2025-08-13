-- End-to-end retrieval pipeline (baseline)
-- Variables: ${PROJECT_ID}, ${DATASET}, ${EMBED_TABLE}, ${DOC_TABLE}, ${QUERY_EMBED_PARAM}, ${TOP_K}
-- Joins nearest neighbor vector search results with original document content.

WITH nn AS (
  SELECT id, distance
  FROM ML.VECTOR_SEARCH(
    TABLE `${PROJECT_ID}.${DATASET}.${EMBED_TABLE}`,
    ${QUERY_EMBED_PARAM},
    top_k => ${TOP_K}
  )
)
SELECT
  d.id,
  d.title,
  d.content,
  nn.distance
FROM `${PROJECT_ID}.${DATASET}.${DOC_TABLE}` d
JOIN nn USING (id)
ORDER BY nn.distance ASC;
