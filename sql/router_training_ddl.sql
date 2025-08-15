-- Router training table DDL
-- Variables: ${PROJECT_ID}, ${DATASET}
-- Creates table for storing training data with text and routing labels

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.router_training` (
  text STRING NOT NULL,
  label STRING NOT NULL  -- logs_only | pdf_image | mixed
);
