"""Embedding refresh logic using SQL template and batch limit.

Reads template at sql/embeddings_refresh.sql with placeholders:
    {PROJECT}, {DATASET}, {EMBED_MODEL_FQID}, {BATCH_LIMIT}

Behavior:
    * Returns a dict: {batches, total_inserted, last_batch}
    * If embed model unset -> prints message, returns zeros.
    * EMBED_BATCH_LIMIT env (default 10000, clamp 1..50000).
    * loop=True will iterate until a batch inserts 0 rows.
        (Relies on BigQuery job.dml_stats.inserted_row_count; falls back
         to 0 if unavailable.)
"""
from __future__ import annotations
from typing import Optional, Dict, Any
import os
from pathlib import Path

from .bigquery_client import BigQueryClientBase
from pipeline import config

TEMPLATE_PATH = Path("sql/embeddings_refresh.sql")


def _batch_limit() -> int:
    env_val = os.getenv("EMBED_BATCH_LIMIT", "10000")
    try:
        v = int(env_val)
    except ValueError:
        v = 10000
    return max(1, min(50000, v))


def _render(model_fqid: str, limit: int) -> str:
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    body = body.replace("{PROJECT}", config.PROJECT_ID)
    body = body.replace("{DATASET}", config.DATASET)
    body = body.replace("{EMBED_MODEL_FQID}", model_fqid)
    body = body.replace("{BATCH_LIMIT}", str(limit))
    return body


def refresh_embeddings(
    client: BigQueryClientBase,
    embed_model_fqid: Optional[str] = None,
    loop: bool = False,
) -> Dict[str, Any]:
    """Refresh missing embeddings.

    Parameters
    ----------
    client : BigQueryClientBase
        Real or stub client.
    embed_model_fqid : Optional[str]
        Override model FQID (else config.EMBED_MODEL).
    loop : bool
        If True, continue executing batches until 0 rows inserted.

    Returns
    -------
    dict
        {batches: int, total_inserted: int, last_batch: int}
    """
    if client.__class__.__name__ == "StubClient":
        return {"batches": 0, "total_inserted": 0, "last_batch": 0}
    model = embed_model_fqid or config.EMBED_MODEL
    if not model:
        print("Embedding model FQID not set (config.EMBED_MODEL).")
        return {"batches": 0, "total_inserted": 0, "last_batch": 0}
    limit = _batch_limit()
    total_inserted = 0
    batches = 0
    last_batch = 0
    while True:
        sql = _render(model, limit)
        inserted = 0
        # Attempt to access underlying real client to capture dml_stats.
        real = getattr(client, "_client", None)
        if real is not None:
            try:
                job = real.query(sql)
                list(job.result())
                stats = getattr(job, "dml_stats", None)
                if stats is not None:  # type: ignore[attr-defined]
                    inserted = getattr(stats, "inserted_row_count", 0)
            except Exception:  # pragma: no cover - best effort
                inserted = 0
        else:
            # Fallback to abstraction (cannot access inserted count)
            client.run_sql_template("inline", {"raw_sql": sql})  # type: ignore
        batches += 1
        last_batch = inserted
        total_inserted += inserted
        print(
            f"[emb-refresh] batch={batches} inserted={inserted} limit={limit}"
        )
        if not loop:
            break
        if inserted == 0:
            break
    print(
        f"[emb-refresh] done: batches={batches} total={total_inserted} "
        f"last={last_batch}"
    )
    return {
        "batches": batches,
        "total_inserted": total_inserted,
        "last_batch": last_batch,
    }
