-- Create view for chunk neighbors based on ticket co-links
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Computes co-occurrence weights from ticket_chunk_links

CREATE OR REPLACE VIEW `${PROJECT_ID}.${DATASET}.chunk_neighbors_ticket` AS
WITH chunk_pairs AS (
  SELECT
    a.chunk_id AS src_chunk_id,
    b.chunk_id AS nbr_chunk_id,
    COUNT(*) AS co_occurrences,
    COUNT(*) / (
      SELECT COUNT(DISTINCT ticket_id) 
      FROM `${PROJECT_ID}.${DATASET}.ticket_chunk_links`
    ) AS weight
  FROM `${PROJECT_ID}.${DATASET}.ticket_chunk_links` a
  JOIN `${PROJECT_ID}.${DATASET}.ticket_chunk_links` b
    ON a.ticket_id = b.ticket_id 
    AND a.chunk_id != b.chunk_id
  GROUP BY a.chunk_id, b.chunk_id
  HAVING COUNT(*) >= 2  -- Require at least 2 co-occurrences
)
SELECT
  src_chunk_id,
  nbr_chunk_id,
  LEAST(weight, 1.0) AS weight  -- Cap weight at 1.0
FROM chunk_pairs
WHERE weight >= 0.1;  -- Minimum weight threshold
