-- Embedding refresh (idempotent insert of missing embeddings)
-- Placeholders:
--   {PROJECT}, {DATASET}, {EMBED_MODEL_FQID}, {BATCH_LIMIT}
--
-- Assumes target table exists:
--   chunks_emb(chunk_id, doc_id, text, meta, embedding ARRAY<FLOAT64>)
--
-- Only inserts rows whose chunk_id not yet present in chunks_emb.

INSERT INTO `{PROJECT}.{DATASET}.chunks_emb` (chunk_id, doc_id, text, meta, embedding)
SELECT c.chunk_id, c.doc_id, c.text, c.meta,
       ML.GENERATE_EMBEDDING(MODEL `{EMBED_MODEL_FQID}`, TEXT => c.text) AS embedding
FROM `{PROJECT}.{DATASET}.chunks` c
LEFT JOIN `{PROJECT}.{DATASET}.chunks_emb` e USING(chunk_id)
WHERE e.chunk_id IS NULL
LIMIT {BATCH_LIMIT};
