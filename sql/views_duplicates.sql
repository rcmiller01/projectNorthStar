-- Potential Duplicate Chunk Groups
-- NOTE: Scripting DECLARE not allowed inside views; kept as comment for traceability & test detection.
-- DECLARE distance_thresh DEFAULT 0.12;
-- PLACEHOLDERS: ${PROJECT_ID}, ${DATASET}
CREATE OR REPLACE VIEW `${PROJECT_ID}.${DATASET}.view_duplicate_chunks` AS
WITH params AS (SELECT 0.12 AS distance_thresh),
vs AS (
  SELECT
    query_row_id AS chunk_id_a,
    nearest_neighbor_row_id AS chunk_id_b,
    distance
  FROM ML.VECTOR_SEARCH(
    TABLE `${PROJECT_ID}.${DATASET}.chunks_emb`,
    (SELECT chunk_id, embedding FROM `${PROJECT_ID}.${DATASET}.chunks_emb`),
    top_k => 6,
    distance_type => 'COSINE'
  )
  WHERE nearest_neighbor_row_id IS NOT NULL
), pairs AS (
  SELECT
    chunk_id_a,
    chunk_id_b,
    distance
  FROM vs, params
  WHERE chunk_id_a != chunk_id_b
    AND distance <= params.distance_thresh
), norm_pairs AS (
  SELECT
    LEAST(chunk_id_a, chunk_id_b) AS left_id,
    GREATEST(chunk_id_a, chunk_id_b) AS right_id,
    distance
  FROM pairs
), members AS (
  SELECT left_id AS group_id, left_id AS member_chunk_id, 0.0 AS distance FROM norm_pairs
  UNION ALL
  SELECT left_id AS group_id, right_id AS member_chunk_id, distance FROM norm_pairs
), agg AS (
  SELECT
    group_id,
    COUNT(DISTINCT member_chunk_id) AS size,
    MIN(NULLIF(distance,0.0)) AS sample_distance
  FROM members
  GROUP BY group_id
)
SELECT
  a.group_id,
  m.member_chunk_id,
  COALESCE(m.distance, a.sample_distance) AS distance,
  a.size
FROM agg a
JOIN members m USING (group_id)
JOIN `${PROJECT_ID}.${DATASET}.chunks` c ON c.chunk_id = m.member_chunk_id
WHERE a.size > 1
ORDER BY a.size DESC, a.group_id
LIMIT 1000;
