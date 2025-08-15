-- Create chunk neighbors table for graph-lite expansion
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Stores chunk relationships with weights for retrieval expansion

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.chunk_neighbors` (
  src_chunk_id STRING NOT NULL,
  nbr_chunk_id STRING NOT NULL,
  weight FLOAT64 NOT NULL
)
PARTITION BY DATE(_PARTITIONTIME)
CLUSTER BY src_chunk_id
OPTIONS (
  description = "Chunk neighborhood graph for retrieval expansion",
  partition_expiration_days = 90
);
