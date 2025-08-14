-- Idempotent chunks upsert using staging table.
-- Placeholders:
--   {PROJECT}, {DATASET}, {STAGING}
--
-- Target schema (created if missing):
--   chunks(chunk_id STRING PRIMARY KEY, doc_id STRING, text STRING, meta JSON)

CREATE TABLE IF NOT EXISTS `{PROJECT}.{DATASET}.chunks` (
	chunk_id STRING,
	doc_id STRING,
	text STRING,
	meta JSON
);

MERGE `{PROJECT}.{DATASET}.chunks` T
USING `{STAGING}` S
ON T.chunk_id = S.chunk_id
WHEN NOT MATCHED THEN
	INSERT (chunk_id, doc_id, text, meta)
	VALUES (S.chunk_id, S.doc_id, S.text, S.meta);
