-- Create (or replace) two Vertex‑AI remote models in BigQuery ML:
--   1) Embeddings model  (e.g., text-embedding-004)
--   2) Text generation   (e.g., gemini-1.5-pro)
--
-- Pass the following named parameters when you run this script:
--   @embed_model_fqid  STRING   -- fully‑qualified model id:  project.dataset.embed_model_name
--   @embed_endpoint    STRING   -- Vertex endpoint name:      text-embedding-004 (or textembedding-gecko@001)
--   @text_model_fqid   STRING   -- fully‑qualified model id:  project.dataset.text_model_name
--   @text_endpoint     STRING   -- Vertex endpoint name:      gemini-1.5-pro (or gemini-1.5-flash etc.)
--   @region            STRING   -- Vertex region (e.g., us-central1)
--
-- Notes:
-- * This uses EXECUTE IMMEDIATE so we can pass model ids as parameters.
-- * Dataset must already exist (your Phase‑0 notebook or preflight script handles that).
-- * These statements are idempotent via CREATE OR REPLACE.

DECLARE embed_model_fqid STRING DEFAULT @embed_model_fqid;
DECLARE embed_endpoint   STRING DEFAULT @embed_endpoint;
DECLARE text_model_fqid  STRING DEFAULT @text_model_fqid;
DECLARE text_endpoint    STRING DEFAULT @text_endpoint;

/* Embedding remote model */
EXECUTE IMMEDIATE FORMAT("""
  CREATE OR REPLACE MODEL `%s`
  REMOTE WITH CONNECTION `%s.%s.vertex-ai`
  OPTIONS (
    ENDPOINT = '%s'
  );
""", embed_model_fqid, @project_id, @location, embed_endpoint);

/* Text generation remote model */
EXECUTE IMMEDIATE FORMAT("""
  CREATE OR REPLACE MODEL `%s`
  REMOTE WITH CONNECTION `%s.%s.vertex-ai`
  OPTIONS (
    ENDPOINT = '%s'
  );
""", text_model_fqid, @project_id, @location, text_endpoint);

/* Sanity prints (visible in job logs) */
SELECT 'created_embedding_model' AS step, embed_model_fqid AS model, embed_endpoint AS endpoint
UNION ALL
SELECT 'created_text_model'     AS step, text_model_fqid  AS model, text_endpoint  AS endpoint;
