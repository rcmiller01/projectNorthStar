-- Get chunk neighbors for graph expansion
-- Variables: ${PROJECT_ID}, ${DATASET}, ${CHUNK_IDS_ARRAY}, ${MAX_NEIGHBORS}
-- Returns neighbors from both similarity and co-occurrence tables

WITH target_chunks AS (
  SELECT chunk_id
  FROM UNNEST(${CHUNK_IDS_ARRAY}) AS chunk_id
),
neighbors_union AS (
  -- Similarity-based neighbors
  SELECT
    cn.src_chunk_id,
    cn.nbr_chunk_id,
    cn.weight,
    'similarity' AS source_type
  FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors` cn
  JOIN target_chunks tc ON cn.src_chunk_id = tc.chunk_id
  
  UNION ALL
  
  -- Co-occurrence neighbors
  SELECT
    cnt.src_chunk_id,
    cnt.nbr_chunk_id,
    cnt.weight,
    'co_occurrence' AS source_type
  FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors_ticket` cnt
  JOIN target_chunks tc ON cnt.src_chunk_id = tc.chunk_id
),
ranked_neighbors AS (
  SELECT
    src_chunk_id,
    nbr_chunk_id,
    MAX(weight) AS weight,  -- Take max weight if same pair from multiple sources
    STRING_AGG(source_type, ',') AS sources
  FROM neighbors_union
  GROUP BY src_chunk_id, nbr_chunk_id
),
limited_neighbors AS (
  SELECT
    src_chunk_id,
    nbr_chunk_id,
    weight,
    sources,
    ROW_NUMBER() OVER (
      PARTITION BY src_chunk_id 
      ORDER BY weight DESC, nbr_chunk_id
    ) AS rn
  FROM ranked_neighbors
)
SELECT
  src_chunk_id,
  nbr_chunk_id,
  weight,
  sources
FROM limited_neighbors
WHERE rn <= ${MAX_NEIGHBORS}
ORDER BY src_chunk_id, weight DESC;
