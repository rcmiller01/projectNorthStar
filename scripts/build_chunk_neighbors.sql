-- Build chunk neighbors from duplicates view and triage patterns
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Populates chunk_neighbors table with similarity and co-occurrence weights

-- Clear existing data
DELETE FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors` WHERE TRUE;

-- Insert neighbors from duplicate detection (similarity-based)
INSERT INTO `${PROJECT_ID}.${DATASET}.chunk_neighbors` (
  src_chunk_id, nbr_chunk_id, weight
)
WITH duplicate_pairs AS (
  SELECT
    a.chunk_id AS src_chunk_id,
    b.chunk_id AS nbr_chunk_id,
    -- Convert distance to similarity weight (1 - distance)
    GREATEST(0.0, LEAST(1.0, 1.0 - a.distance)) AS weight
  FROM `${PROJECT_ID}.${DATASET}.view_duplicate_chunks` a
  JOIN `${PROJECT_ID}.${DATASET}.view_duplicate_chunks` b
    ON a.duplicate_group = b.duplicate_group
    AND a.chunk_id != b.chunk_id
  WHERE a.distance <= 0.3  -- Similarity threshold
    AND a.distance > 0.0    -- Exclude perfect matches
)
SELECT DISTINCT
  src_chunk_id,
  nbr_chunk_id,
  AVG(weight) AS weight  -- Average if multiple paths
FROM duplicate_pairs
GROUP BY src_chunk_id, nbr_chunk_id
HAVING AVG(weight) >= 0.2;  -- Minimum weight threshold

-- Insert neighbors from ticket co-occurrence patterns
INSERT INTO `${PROJECT_ID}.${DATASET}.chunk_neighbors` (
  src_chunk_id, nbr_chunk_id, weight
)
SELECT
  src_chunk_id,
  nbr_chunk_id,
  -- Scale co-occurrence weight to complement similarity weights
  weight * 0.5 AS weight
FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors_ticket`
WHERE NOT EXISTS (
  -- Avoid duplicates with similarity-based neighbors
  SELECT 1 FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors` cn
  WHERE cn.src_chunk_id = chunk_neighbors_ticket.src_chunk_id
    AND cn.nbr_chunk_id = chunk_neighbors_ticket.nbr_chunk_id
);

-- Create summary statistics
SELECT
  COUNT(*) AS total_neighbor_pairs,
  COUNT(DISTINCT src_chunk_id) AS chunks_with_neighbors,
  AVG(weight) AS avg_weight,
  MIN(weight) AS min_weight,
  MAX(weight) AS max_weight
FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors`;
