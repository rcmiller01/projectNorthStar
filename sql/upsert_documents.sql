-- Idempotent documents upsert using staging table.
-- Placeholders (simple string replacement in loader):
--   {PROJECT}  : GCP project id
--   {DATASET}  : BigQuery dataset
--   {STAGING}  : fully-qualified staging table containing rows to merge
--
-- Target schema (created if missing):
--   documents(doc_id STRING PRIMARY KEY, type STRING, uri STRING, meta JSON)
--
-- Behavior:
--   * CREATE TABLE IF NOT EXISTS to ensure target exists
--   * MERGE inserts new rows (upsert semantics; only INSERT on NOT MATCHED)
--   * Returns affected row count via job statistics (read by loader)

CREATE TABLE IF NOT EXISTS `{PROJECT}.{DATASET}.documents` (
	doc_id STRING,
	type STRING,
	uri STRING,
	meta JSON
);

MERGE `{PROJECT}.{DATASET}.documents` T
USING `{STAGING}` S
ON T.doc_id = S.doc_id
WHEN NOT MATCHED THEN
	INSERT (doc_id, type, uri, meta) VALUES (S.doc_id, S.type, S.uri, S.meta);
