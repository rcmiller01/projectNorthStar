"""Loaders for documents and chunks using staging tables + MERGE.

Workflow:
  1. Create unique staging table name with timestamp suffix.
  2. Load JSON rows via BigQuery JSON literal (for simplicity, still inline).
  3. Execute MERGE template (sql/upsert_*.sql) with placeholders replaced.
  4. Drop staging table in finally block.

Offline stub returns len(input) without side effects.
"""
from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import os
import json
import datetime as _dt

from .bigquery_client import BigQueryClientBase


def _is_stub(client: BigQueryClientBase) -> bool:
    return client.__class__.__name__ == "StubClient"


def _ts() -> str:
    return _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")


def _create_staging(
    client: BigQueryClientBase, fq_table: str, rows: List[Dict[str, Any]]
) -> None:
    if not rows:
        return
    # Inline JSON ingestion (small batches) using temp table strategy.
    # For production volumes: use load_job with newline-delimited JSON.
    encoded = json.dumps(rows)
    sql = f"""
    CREATE TABLE `{fq_table}` AS
    SELECT
      JSON_VALUE(r, '$.doc_id') AS doc_id,
      JSON_VALUE(r, '$.type') AS type,
      JSON_VALUE(r, '$.uri') AS uri,
      JSON_VALUE(r, '$.chunk_id') AS chunk_id,
      JSON_VALUE(r, '$.text') AS text,
      TO_JSON(r) AS meta
    FROM UNNEST(JSON_QUERY_ARRAY(PARSE_JSON(@rows), '$')) r
    """
    sql = sql.replace(
        "@rows", f"'{encoded.replace(chr(39), chr(92) + chr(39))}'"
    )  # naive escaping
    client.run_sql_template("inline", {"raw_sql": sql})  # type: ignore


def _merge(
    template_name: str, client: BigQueryClientBase, **params: str
) -> Dict[str, int]:
    sql_path = {
        "documents": "sql/upsert_documents.sql",
        "chunks": "sql/upsert_chunks.sql",
    }[template_name]
    body = Path(sql_path).read_text(encoding="utf-8")  # type: ignore
    for k, v in params.items():
        body = body.replace(f"{{{k}}}", v)
    # Execute MERGE; row count accessible via job stats if real client.
    # Execute merge; RealClient exposes google Job via internal attribute.
    # Our abstraction returns only rows; attempt direct query for dml stats.
    try:  # best effort to access underlying real client
        real = getattr(client, "_client", None)
        if real:  # attempt direct query for dml stats
            job = real.query(body)
            list(job.result())
            stats = getattr(job, "dml_stats", None)
            if stats:  # type: ignore[attr-defined]
                return {
                    "inserted": getattr(stats, "inserted_row_count", 0),
                    "updated": getattr(stats, "updated_row_count", 0),
                    "deleted": getattr(stats, "deleted_row_count", 0),
                }
    except Exception:
        pass
    client.run_sql_template("inline", {"raw_sql": body})  # type: ignore
    return {"inserted": 0, "updated": 0, "deleted": 0}


def upsert_documents(
    client: BigQueryClientBase, docs: List[Dict[str, Any]]
) -> int:
    if not docs:
        return 0
    if _is_stub(client):
        return len(docs)
    project = os.getenv("PROJECT_ID", "")
    dataset = os.getenv("DATASET", "")
    staging = f"{project}.{dataset}.staging_documents_{_ts()}"
    try:
        _create_staging(client, staging, docs)
        stats = _merge(
            "documents",
            client,
            PROJECT=project,
            DATASET=dataset,
            STAGING=staging,
        )
        print(
            "documents upsert: inserted={i} updated={u} deleted={d}".format(
                i=stats["inserted"], u=stats["updated"], d=stats["deleted"]
            )
        )
        return stats["inserted"] + stats["updated"]
    finally:
        try:
            client.run_sql_template(
                "inline", {"raw_sql": f"DROP TABLE IF EXISTS `{staging}`"}
            )  # type: ignore
        except Exception:
            pass


def upsert_chunks(
    client: BigQueryClientBase, chunks: List[Dict[str, Any]]
) -> int:
    if not chunks:
        return 0
    if _is_stub(client):
        return len(chunks)
    project = os.getenv("PROJECT_ID", "")
    dataset = os.getenv("DATASET", "")
    staging = f"{project}.{dataset}.staging_chunks_{_ts()}"
    try:
        _create_staging(client, staging, chunks)
        stats = _merge(
            "chunks",
            client,
            PROJECT=project,
            DATASET=dataset,
            STAGING=staging,
        )
        print(
            "chunks upsert: inserted={i} updated={u} deleted={d}".format(
                i=stats["inserted"], u=stats["updated"], d=stats["deleted"]
            )
        )
        return stats["inserted"] + stats["updated"]
    finally:
        try:
            client.run_sql_template(
                "inline", {"raw_sql": f"DROP TABLE IF EXISTS `{staging}`"}
            )  # type: ignore
        except Exception:
            pass
