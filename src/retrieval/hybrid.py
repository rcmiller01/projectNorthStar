"""Hybrid retrieval (Phase 1) using vector search SQL template."""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Set
from ..bq.bigquery_client import BigQueryClientBase

logger = logging.getLogger(__name__)
MAX_K = 8


def vector_search(
    client: BigQueryClientBase,
    query_text: str,
    k: int = 5,
    types: Optional[List[str]] = None,
    graph_boost: float = 0.0,
    expand_neighbors: int = 5,
) -> List[Dict[str, Any]]:
    """Vector search with optional type filtering and graph expansion.

    If types are specified, uses chunk_vector_search for filtering.
    Otherwise falls back to simple vector_search for backwards compatibility.

    Parameters
    ----------
    graph_boost : float
        Graph expansion boost factor (0.0 = disabled, 0.2 = default)
    expand_neighbors : int
        Max neighbors to expand per initial result
    """
    if types:
        # Use advanced chunk search with type filtering
        initial_results = chunk_vector_search(client, query_text, k, types)
    else:
        # Fall back to old table for backwards compatibility
        initial_results = _normalize_rows(
            client.run_sql_template(
                "vector_search.sql",
                {"query_text": query_text, "top_k": _clamp_k(k)},
            ),
        )

    # Apply graph expansion if enabled
    if graph_boost > 0.0 and initial_results:
        return _expand_with_graph(client, initial_results, k, graph_boost, expand_neighbors)
    else:
        return initial_results


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


def _expand_with_graph(
    client: BigQueryClientBase,
    initial_results: List[Dict[str, Any]],
    final_k: int,
    graph_boost: float,
    expand_neighbors: int,
) -> List[Dict[str, Any]]:
    """Expand initial results with graph neighbors and re-rank."""
    try:
        # Extract chunk IDs from initial results
        chunk_ids = [r.get("id") for r in initial_results if r.get("id")]
        if not chunk_ids:
            logger.warning("No chunk IDs found in initial results")
            return initial_results

        # Get neighbors for expansion
        neighbor_rows = client.run_sql_template(
            "get_chunk_neighbors.sql",
            {
                "chunk_ids": chunk_ids,
                "max_neighbors": expand_neighbors,
            },
        )

        if not neighbor_rows:
            logger.debug("No neighbors found, returning initial results")
            return initial_results

        # Collect all neighbor chunk IDs
        neighbor_chunk_ids = [row["nbr_chunk_id"] for row in neighbor_rows]

        # Remove duplicates and exclude chunks already in initial results
        initial_chunk_ids = {r.get("id") for r in initial_results}
        unique_neighbor_ids = [cid for cid in neighbor_chunk_ids if cid not in initial_chunk_ids]

        if not unique_neighbor_ids:
            logger.debug("No new neighbors to add")
            return initial_results

        # Get chunk details for neighbors
        neighbor_details = client.run_sql_template(
            "get_chunk_details.sql", {"chunk_ids": unique_neighbor_ids}
        )

        # Create neighbor lookup
        neighbor_map = {row["chunk_id"]: row for row in neighbor_details}

        # Build expanded result set
        expanded_results = []
        seen_chunk_ids = set()

        # Add initial results with original scores
        for result in initial_results:
            distance = result.get("distance", 1.0)
            vector_score = 1.0 - distance
            chunk_id = result.get("id")

            if chunk_id and chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(chunk_id)
                expanded_results.append(
                    {
                        **result,
                        "final_score": vector_score,
                        "vector_score": vector_score,
                        "graph_weight": 0.0,
                        "source_type": "vector",
                    }
                )

        # Add neighbor results with graph-boosted scores
        for result in initial_results:
            src_chunk_id = result.get("id")
            if not src_chunk_id:
                continue

            for neighbor_row in neighbor_rows:
                if neighbor_row["src_chunk_id"] != src_chunk_id:
                    continue

                nbr_chunk_id = neighbor_row["nbr_chunk_id"]

                # Skip if already seen (deduplication)
                if nbr_chunk_id in seen_chunk_ids:
                    continue

                if nbr_chunk_id in neighbor_map:
                    seen_chunk_ids.add(nbr_chunk_id)
                    neighbor_detail = neighbor_map[nbr_chunk_id]
                    graph_weight = neighbor_row["weight"]

                    # Estimate distance for neighbor (no direct vector score)
                    estimated_distance = max(0.1, 1.0 - graph_weight)
                    vector_score = 1.0 - estimated_distance

                    # Combined score: vector + graph boost
                    final_score = (1.0 - graph_boost) * vector_score + graph_boost * graph_weight

                    expanded_results.append(
                        {
                            "id": nbr_chunk_id,
                            "text": neighbor_detail.get("text"),
                            "distance": estimated_distance,
                            "source": _build_source_string(neighbor_detail),
                            "final_score": final_score,
                            "vector_score": vector_score,
                            "graph_weight": graph_weight,
                            "source_type": "graph",
                            "graph_sources": neighbor_row.get("sources", ""),
                        }
                    )

        # Re-rank by final score and limit to final_k
        sorted_results = sorted(
            expanded_results, key=lambda x: x.get("final_score", 0.0), reverse=True
        )[:final_k]

        # Log expansion stats
        original_count = len(initial_results)
        expanded_count = len(expanded_results)
        final_count = len(sorted_results)
        graph_count = sum(1 for r in sorted_results if r.get("source_type") == "graph")

        logger.info(
            f"Graph expansion: {original_count} → {expanded_count} → "
            f"{final_count} (graph: {graph_count})"
        )

        return sorted_results

    except Exception as exc:
        logger.warning(f"Graph expansion failed, using vector-only: {exc}")
        return initial_results


def _build_source_string(chunk_detail: Dict[str, Any]) -> str:
    """Build source string for neighbor chunks."""
    meta_raw = chunk_detail.get("meta")
    meta: Dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
    src_parts: List[str] = ["bq.graph_expand"]

    t = meta.get("type")
    fname = meta.get("filename") or meta.get("uri") or "unknown"

    if t == "log":
        src_parts.extend(["log", str(fname)])
        if "line_no" in meta:
            src_parts.append(str(meta["line_no"]))
    elif t == "pdf":
        src_parts.extend(["pdf", str(fname)])
        if "page" in meta:
            src_parts.append(f"p{meta['page']}")
    elif t == "image_ocr":
        src_parts.extend(["image_ocr", str(fname)])
        if "page" in meta:
            src_parts.append(f"p{meta['page']}")
    elif t == "image":
        src_parts.extend(["image", str(fname)])
    else:
        if t:
            src_parts.extend([str(t), str(fname)])

    return ":".join(src_parts)


# Reflection:
# Enhanced with graph expansion and re-ranking capabilities.
# Next improvement: learn optimal boost weights from user feedback.
