-- Teardown script: drop remote embedding & text models (idempotent).
-- Environment variables expanded by shell before submission:
--   PROJECT_ID, DATASET, BQ_EMBED_MODEL (optional FQID), BQ_GEN_MODEL (optional FQID)
-- Fallback names (if FQIDs not set):
--   ${PROJECT_ID}.${DATASET}.embed_model
--   ${PROJECT_ID}.${DATASET}.text_model
-- Usage (bash):
--   bq query --use_legacy_sql=false "$(cat sql/drop_remote_models.sql)"

DECLARE project STRING DEFAULT '${PROJECT_ID}';
DECLARE dataset STRING DEFAULT '${DATASET}';
DECLARE embed_model_fqid STRING DEFAULT '${BQ_EMBED_MODEL}';
DECLARE text_model_fqid  STRING DEFAULT '${BQ_GEN_MODEL}';

IF embed_model_fqid IS NULL OR embed_model_fqid = '' THEN
  SET embed_model_fqid = FORMAT('%s.%s.embed_model', project, dataset);
END IF;
IF text_model_fqid IS NULL OR text_model_fqid = '' THEN
  SET text_model_fqid = FORMAT('%s.%s.text_model', project, dataset);
END IF;

-- Drop embedding model
EXECUTE IMMEDIATE FORMAT('DROP MODEL IF EXISTS `%s`', embed_model_fqid);
-- Drop text model
EXECUTE IMMEDIATE FORMAT('DROP MODEL IF EXISTS `%s`', text_model_fqid);

-- Confirmation output
SELECT 'dropped_embedding_model' AS step, embed_model_fqid AS model
UNION ALL
SELECT 'dropped_text_model' AS step, text_model_fqid AS model;
