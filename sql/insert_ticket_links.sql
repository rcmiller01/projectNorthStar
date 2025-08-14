-- Upsert ticket->chunk evidence link (MERGE)
-- Template placeholders: ${PROJECT_ID} ${DATASET}
MERGE `${PROJECT_ID}.${DATASET}.ticket_chunk_links` T
USING (
  SELECT @ticket_id AS ticket_id, @chunk_id AS chunk_id, @relation AS relation, @score AS score
) S
ON T.ticket_id = S.ticket_id AND T.chunk_id = S.chunk_id
WHEN MATCHED THEN UPDATE SET relation = S.relation, score = S.score
WHEN NOT MATCHED THEN INSERT (ticket_id, chunk_id, relation, score)
VALUES (S.ticket_id, S.chunk_id, S.relation, S.score);
