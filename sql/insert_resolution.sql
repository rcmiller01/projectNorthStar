-- Upsert resolution snapshot (MERGE)
-- Template placeholders: ${PROJECT_ID} ${DATASET}
MERGE `${PROJECT_ID}.${DATASET}.resolutions` T
USING (
  SELECT
    @ticket_id AS ticket_id,
    @resolved_at AS resolved_at,
    @resolution_text AS resolution_text,
    @playbook_md AS playbook_md
) S
ON T.ticket_id = S.ticket_id
WHEN MATCHED THEN UPDATE SET
  resolved_at = S.resolved_at,
  resolution_text = S.resolution_text,
  playbook_md = S.playbook_md
WHEN NOT MATCHED THEN INSERT (ticket_id, resolved_at, resolution_text, playbook_md)
VALUES (S.ticket_id, S.resolved_at, S.resolution_text, S.playbook_md);
