-- Chunk neighbors table DDL for graph-lite expansion
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Creates table for storing chunk neighbor relationships with weights

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.chunk_neighbors` (
  src_chunk_id STRING NOT NULL,
  nbr_chunk_id STRING NOT NULL,
  weight FLOAT64 NOT NULL
);
