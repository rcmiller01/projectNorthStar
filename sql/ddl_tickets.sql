-- Ticket system generic schema (idempotent creates)
-- Dataset resolved via template substitutions: ${PROJECT_ID}.${DATASET}

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.tickets` (
  ticket_id STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP,
  status STRING,
  severity STRING,
  source STRING,
  reporter STRING,
  assignee STRING,
  component STRING,
  title STRING,
  body STRING,
  tags ARRAY<STRING>,
  meta JSON
);

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.ticket_events` (
  event_id STRING NOT NULL,
  ticket_id STRING NOT NULL,
  ts TIMESTAMP NOT NULL,
  type STRING,
  actor STRING,
  text STRING,
  meta JSON
);

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.ticket_attachments` (
  attachment_id STRING NOT NULL,
  ticket_id STRING NOT NULL,
  uri STRING,
  type STRING,
  meta JSON
);

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.ticket_chunk_links` (
  ticket_id STRING NOT NULL,
  chunk_id STRING NOT NULL,
  relation STRING,
  score FLOAT64,
  meta JSON
);

CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${DATASET}.resolutions` (
  ticket_id STRING NOT NULL,
  resolved_at TIMESTAMP,
  resolution_text STRING,
  playbook_md STRING,
  meta JSON
);
