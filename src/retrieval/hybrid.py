"""Hybrid retrieval (Phase 1) using vector search SQL template.
"""
from __future__ import annotations
from typing import Any, Dict, List
from ..bq.bigquery_client import BigQueryClientBase

MAX_K = 8


def vector_search(
    client: BigQueryClientBase, query_text: str, k: int = 5
) -> List[Dict[str, Any]]:
    """Run vector search (clamped) and normalize rows.

    Returns list of dicts with id, text, distance, source.
    """
    k_clamped = max(1, min(MAX_K, k))
    rows = client.run_sql_template(
        "vector_search.sql", {"query_text": query_text, "top_k": k_clamped}
    )
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "id": r.get("id"),
                "text": r.get("text"),
                "distance": r.get("distance"),
                "source": "bq.vector_search",
            }
        )
    return out

# Reflection:
# Straightforward wrapper; future: add lexical blend or rerank stage.
