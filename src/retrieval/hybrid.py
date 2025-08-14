"""Hybrid retrieval (Phase 1) using vector search SQL template.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from ..bq.bigquery_client import BigQueryClientBase

MAX_K = 8


def vector_search(
    client: BigQueryClientBase,
    query_text: str,
    k: int = 5,
    types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:  # Backwards compatibility (demo table)
    # Fall back to old table; type filtering unsupported here.
    return _normalize_rows(
        client.run_sql_template(
            "vector_search.sql",
            {"query_text": query_text, "top_k": _clamp_k(k)},
        ),
    )


def chunk_vector_search(
    client: BigQueryClientBase,
    query_text: str,
    k: int = 5,
    types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Vector search over chunk embeddings with optional type filtering."""
    params: Dict[str, Any] = {
        "query_text": query_text,
        "top_k": _clamp_k(k),
        "types": types or [],
    }
    rows = client.run_sql_template("chunk_vector_search.sql", params)
    return _normalize_rows(rows)


def _clamp_k(k: int) -> int:
    return max(1, min(MAX_K, k))


def _normalize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        meta_raw = r.get("meta")
        meta: Dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
        src_parts: List[str] = ["bq.vector_search"]
        t = meta.get("type")
        fname = meta.get("filename") or meta.get("uri") or "unknown"
        if t == "log":
            # logs: bq.vector_search:log:{basename}:{line_no}
            src_parts.append("log")
            src_parts.append(str(fname))
            if "line_no" in meta:
                src_parts.append(str(meta["line_no"]))
        elif t == "pdf":
            # pdf: bq.vector_search:pdf:{basename}:p{page}
            src_parts.append("pdf")
            src_parts.append(str(fname))
            if "page" in meta:
                src_parts.append(f"p{meta['page']}")
        elif t == "image_ocr":
            # image_ocr: bq.vector_search:image_ocr:{basename}:p{page}
            src_parts.append("image_ocr")
            src_parts.append(str(fname))
            if "page" in meta:
                src_parts.append(f"p{meta['page']}")
        elif t == "image":
            # image: bq.vector_search:image:{basename}
            src_parts.append("image")
            src_parts.append(str(fname))
        else:
            if t:
                src_parts.append(str(t))
                src_parts.append(str(fname))
        out.append(
            {
                "id": r.get("id") or r.get("chunk_id"),
                "text": r.get("text"),
                "distance": r.get("distance"),
                "source": ":".join(src_parts),
            }
        )
    return out

# Reflection:
# Straightforward wrapper; future: add lexical blend or rerank stage.
