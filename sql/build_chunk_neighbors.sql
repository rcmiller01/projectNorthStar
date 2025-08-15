-- Build chunk neighbors from existing views
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Derives neighbor relationships from duplicates and ticket co-links

-- Clear existing data
DELETE FROM `${PROJECT_ID}.${DATASET}.chunk_neighbors` WHERE TRUE;

-- Add neighbors from duplicate chunks (high weight)
INSERT INTO `${PROJECT_ID}.${DATASET}.chunk_neighbors` (src_chunk_id, nbr_chunk_id, weight)
SELECT DISTINCT 
  chunk_id AS src_chunk_id, 
  dup_id AS nbr_chunk_id, 
  0.9 AS weight
FROM `${PROJECT_ID}.${DATASET}.view_duplicate_chunks`
WHERE chunk_id != dup_id;

-- Add bidirectional relationships for duplicates
INSERT INTO `${PROJECT_ID}.${DATASET}.chunk_neighbors` (src_chunk_id, nbr_chunk_id, weight)
SELECT DISTINCT 
  dup_id AS src_chunk_id, 
  chunk_id AS nbr_chunk_id, 
  0.9 AS weight
FROM `${PROJECT_ID}.${DATASET}.view_duplicate_chunks`
WHERE chunk_id != dup_id;

-- Add ticket co-links (moderate weight)
INSERT INTO `${PROJECT_ID}.${DATASET}.chunk_neighbors` (src_chunk_id, nbr_chunk_id, weight)
SELECT DISTINCT
  l1.chunk_id AS src_chunk_id,
  l2.chunk_id AS nbr_chunk_id,
  0.5 AS weight
FROM `${PROJECT_ID}.${DATASET}.ticket_chunk_links` l1
JOIN `${PROJECT_ID}.${DATASET}.ticket_chunk_links` l2
  ON l1.ticket_id = l2.ticket_id 
  AND l1.chunk_id != l2.chunk_id;
