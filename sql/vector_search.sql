-- Vector search example using approximate similarity
-- Variables: ${PROJECT_ID}, ${DATASET}, ${EMBED_TABLE}, ${QUERY_EMBED_PARAM}, ${TOP_K}

SELECT
  id,
  distance
FROM ML.VECTOR_SEARCH(
  TABLE `${PROJECT_ID}.${DATASET}.${EMBED_TABLE}`,
  ${QUERY_EMBED_PARAM},
  top_k => ${TOP_K}
) ORDER BY distance ASC;
