"""Idempotent remote model creation for embeddings + text generation.

Creates remote Vertex models in BigQuery ML only if missing.

Env vars:
  PROJECT_ID, DATASET, LOCATION
  VERTEX_REGION (default: us-central1)
  EMBED_ENDPOINT (default: text-embedding-004)
  TEXT_ENDPOINT  (default: gemini-1.5-pro)
  EMBED_MODEL_FQID (default: PROJECT.DATASET.embed_model)
  TEXT_MODEL_FQID  (default: PROJECT.DATASET.text_model)

Behavior:
  - If both models exist: skip and exit 0.
  - If one exists: create only the missing one.
  - If none exist: create both.

Requires google-cloud-bigquery extra.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
# (no optional typing needed)

from _bq_utils import model_exists, dataset_location

try:  # pragma: no cover
    from google.cloud import bigquery  # type: ignore
except Exception:  # pragma: no cover
    print(
        "google-cloud-bigquery not installed. Install: "
        "pip install -e .[bigquery]"
    )
    raise

PROJECT = os.getenv("PROJECT_ID") or "bq_project_northstar"
DATASET = os.getenv("DATASET") or "demo_ai"
LOCATION = os.getenv("LOCATION") or "US"
VERTEX_REGION = os.getenv("VERTEX_REGION") or "us-central1"
EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT") or "text-embedding-004"
TEXT_ENDPOINT = os.getenv("TEXT_ENDPOINT") or "gemini-1.5-pro"
EMBED_MODEL_FQID = (
    os.getenv("EMBED_MODEL_FQID") or f"{PROJECT}.{DATASET}.embed_model"
)
TEXT_MODEL_FQID = (
    os.getenv("TEXT_MODEL_FQID") or f"{PROJECT}.{DATASET}.text_model"
)
SQL_BOTH = Path("sql/create_remote_models.sql")

# Optional individual SQL (fallback: generated statements)
SQL_EMBED = Path("sql/create_embed_model.sql")
SQL_TEXT = Path("sql/create_text_model.sql")


def read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def create_model_via_exec(
    client: "bigquery.Client", fqid: str, endpoint: str, service: str
) -> None:
    # service: TEXT_EMBEDDING or GEN_AI
    stmt = f"""
    CREATE OR REPLACE MODEL `{fqid}`
    OPTIONS (
      MODEL_TYPE = 'VERTEX_AI',
      REMOTE_SERVICE_TYPE = '{service}',
      ENDPOINT = '{endpoint}',
      REGION = '{VERTEX_REGION}'
    )
    """
    client.query(stmt).result()


def run() -> None:
    client = bigquery.Client(project=PROJECT, location=LOCATION)
    bq_loc = dataset_location(client, PROJECT, DATASET)
    if (
        bq_loc
        and bq_loc.upper() in {"US", "EU"}
        and VERTEX_REGION not in ("us-central1", "europe-west4")
    ):
        print(
            "⚠️  Vertex region differs from common default for multi-region "
            "dataset"
        )

    embed_exists = model_exists(client, EMBED_MODEL_FQID)
    text_exists = model_exists(client, TEXT_MODEL_FQID)

    if embed_exists and text_exists:
        print(
            f"✅ Both exist: {EMBED_MODEL_FQID}, {TEXT_MODEL_FQID} (skip)"
        )
        return

    # If both missing and we have combined SQL, use it (fast path)
    if not embed_exists and not text_exists and SQL_BOTH.exists():
        sql = read_sql(SQL_BOTH)
        job = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "embed_model_fqid", "STRING", EMBED_MODEL_FQID
                    ),
                    bigquery.ScalarQueryParameter(
                        "embed_endpoint", "STRING", EMBED_ENDPOINT
                    ),
                    bigquery.ScalarQueryParameter(
                        "text_model_fqid", "STRING", TEXT_MODEL_FQID
                    ),
                    bigquery.ScalarQueryParameter(
                        "text_endpoint", "STRING", TEXT_ENDPOINT
                    ),
                    bigquery.ScalarQueryParameter(
                        "region", "STRING", VERTEX_REGION
                    ),
                ]
            ),
        )
        job.result()
        print(
            f"✅ Created embedding + text models: {EMBED_MODEL_FQID}, "
            f"{TEXT_MODEL_FQID}"
        )
        return

    # Partial creation path
    if not embed_exists:
        print(
            f"➡ Creating embedding model {EMBED_MODEL_FQID} "
            f"(endpoint={EMBED_ENDPOINT})"
        )
        if SQL_EMBED.exists():  # optional single-file path
            sql = read_sql(SQL_EMBED)
            client.query(
                sql,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter(
                            "embed_model_fqid", "STRING", EMBED_MODEL_FQID
                        ),
                        bigquery.ScalarQueryParameter(
                            "embed_endpoint", "STRING", EMBED_ENDPOINT
                        ),
                        bigquery.ScalarQueryParameter(
                            "region", "STRING", VERTEX_REGION
                        ),
                    ]
                ),
            ).result()
        else:
            create_model_via_exec(
                client, EMBED_MODEL_FQID, EMBED_ENDPOINT, "TEXT_EMBEDDING"
            )
        print("✅ Embedding model created")
    else:
        print(f"✅ Embedding model exists: {EMBED_MODEL_FQID} (skip)")

    if not text_exists:
        print(
            f"➡ Creating text model {TEXT_MODEL_FQID} "
            f"(endpoint={TEXT_ENDPOINT})"
        )
        if SQL_TEXT.exists():
            sql = read_sql(SQL_TEXT)
            client.query(
                sql,
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter(
                            "text_model_fqid", "STRING", TEXT_MODEL_FQID
                        ),
                        bigquery.ScalarQueryParameter(
                            "text_endpoint", "STRING", TEXT_ENDPOINT
                        ),
                        bigquery.ScalarQueryParameter(
                            "region", "STRING", VERTEX_REGION
                        ),
                    ]
                ),
            ).result()
        else:
            create_model_via_exec(
                client, TEXT_MODEL_FQID, TEXT_ENDPOINT, "GEN_AI"
            )
        print("✅ Text model created")
    else:
        print(f"✅ Text model exists: {TEXT_MODEL_FQID} (skip)")

    print("🎉 Remote model creation complete.")


if __name__ == "__main__":  # pragma: no cover
    try:
        run()
    except KeyboardInterrupt:  # pragma: no cover
        print("Interrupted", file=sys.stderr)
        sys.exit(130)
