"""Micro evaluation harness.

Loads metrics/eval_set.jsonl and computes comprehensive retrieval metrics.

Metrics per item:
  hit@k: 1 if any retrieved chunk text contains any expected term (ci)
  min_distance: min distance across retrieved (fallback 1.0)
  verifier_score: 1 if draft_ok else 0 (optional; skip if orchestrator fails)
  ndcg@k: normalized DCG based on expected_terms matches
  mrr: mean reciprocal rank of first expected_terms match
  semantic_cosine: max cosine similarity with query embedding

Aggregate metrics:
  hit_rate, mean_min_distance, mean_verifier_score, ndcg@k, mrr,
  semantic_cosine (p25/p50/p75/mean), timings (mean/p95), cost estimates

Supports real BigQuery (if BIGQUERY_REAL=1) else stub retrieval.
"""

from __future__ import annotations
import argparse
import json
import math
import os
import time
from pathlib import Path
from statistics import mean, quantiles
from typing import List, Dict, Any, Optional

try:  # ensure project root on path when running as a script
    from bq import make_client  # type: ignore
    from core.orchestrator import Orchestrator  # type: ignore
    from retrieval.hybrid import vector_search  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - path fix branch
    import pathlib
    import sys as _sys

    root = pathlib.Path(__file__).resolve().parent.parent
    if str(root) not in _sys.path:
        _sys.path.insert(0, str(root))
    from bq import make_client  # type: ignore
    from core.orchestrator import Orchestrator  # type: ignore
    from retrieval.hybrid import vector_search  # type: ignore

EVAL_SET_PATH = Path("metrics/eval_set.jsonl")


def dcg_at_k(relevances: List[float], k: int) -> float:
    """Compute Discounted Cumulative Gain at k."""
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        if i == 0:
            dcg += rel
        else:
            dcg += rel / math.log2(i + 1)
    return dcg


def ndcg_at_k(relevances: List[float], k: int) -> float:
    """Compute Normalized DCG at k."""
    dcg = dcg_at_k(relevances, k)
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal_relevances, k)
    return dcg / idcg if idcg > 0 else 0.0


def compute_mrr(relevances: List[float]) -> float:
    """Compute Mean Reciprocal Rank - reciprocal of first relevant position."""
    for i, rel in enumerate(relevances):
        if rel > 0:
            return 1.0 / (i + 1)
    return 0.0


def embed_query(client, query_text: str) -> Optional[List[float]]:
    """Get query embedding using the same model as vector search."""
    try:
        # Use ML.GENERATE_EMBEDDING to get query embedding
        embedding_sql = """
        SELECT embedding
        FROM ML.GENERATE_EMBEDDING(
            MODEL `${PROJECT_ID}.${DATASET}.text_embedding_model`,
            (SELECT '${QUERY_TEXT}' AS content)
        )
        """
        result = client.run_sql_template("", {"raw_sql": embedding_sql, "query_text": query_text})
        if result and "embedding" in result[0]:
            return result[0]["embedding"]["values"]
    except Exception:
        pass
    return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def get_chunk_embedding(chunk: Dict[str, Any]) -> Optional[List[float]]:
    """Extract embedding from chunk if available."""
    # Check various possible embedding field names
    for field in ["embedding", "embeddings", "vector"]:
        if field in chunk:
            emb = chunk[field]
            if isinstance(emb, list):
                return emb
            elif isinstance(emb, dict) and "values" in emb:
                return emb["values"]
    return None


def extract_timing_from_stats(stats: Dict[str, Any]) -> Dict[str, float]:
    """Extract timing information from orchestrator stats."""
    timings = {}

    # Look for timing information in various stats fields
    if "query_time_ms" in stats:
        timings["total_ms"] = stats["query_time_ms"]

    if "router_time_ms" in stats:
        timings["router_ms"] = stats["router_time_ms"]

    if "retrieval_time_ms" in stats:
        timings["retrieval_ms"] = stats["retrieval_time_ms"]

    if "verification_time_ms" in stats:
        timings["verification_ms"] = stats["verification_time_ms"]

    return timings


def estimate_cost_from_stats(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate costs from orchestrator stats and BQ metadata."""
    cost_info = {
        "ml_calls": 0,
        "bytes_processed": 0,
        "embedding_calls": 0,
        "vector_search_calls": 0,
    }

    # Count ML calls based on what operations were performed
    if stats.get("router_strategy") == "learned":
        cost_info["ml_calls"] += 1  # Router prediction

    cost_info["embedding_calls"] += 1  # Query embedding
    cost_info["vector_search_calls"] += 1  # Vector search

    # Estimate bytes processed (placeholder - would need actual BQ job info)
    k = stats.get("k", 5)
    cost_info["bytes_processed"] = k * 1000  # Rough estimate

    return cost_info


def load_items() -> List[dict]:
    if not EVAL_SET_PATH.exists():
        raise SystemExit("Eval set missing; run gen_eval_set first")
    items: List[dict] = []
    for line in EVAL_SET_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        items.append(json.loads(line))
    return items


def retrieve_chunks(client, query: str, k: int, types: List[str] | None) -> List[dict]:
    # Pass through to hybrid vector_search which accepts 'types'
    return vector_search(client, query_text=query, k=k, types=types or [])


def evaluate(items: List[dict], k: int, use_stub: bool) -> dict:
    client = make_client()
    orch = Orchestrator(client)
    per_item: List[dict] = []
    all_timings: List[Dict[str, float]] = []
    all_costs: List[Dict[str, Any]] = []

    for it in items:
        q = it["query_text"]
        types = it.get("types")

        # Time the retrieval step
        start_time = time.time()
        chunks = retrieve_chunks(client, q, k=k, types=types)
        retrieval_time = (time.time() - start_time) * 1000  # ms

        # Get query embedding for semantic similarity
        query_embedding = embed_query(client, q) if not use_stub else None

        # Compute relevance scores for each chunk
        expected_terms = [t.lower() for t in it.get("expected_terms", [])]
        relevances = []
        distances = []
        cosine_scores = []

        for c in chunks:
            text = (c.get("text") or c.get("snippet") or "").lower()

            # Binary relevance based on expected terms
            relevance = 1.0 if any(term in text for term in expected_terms) else 0.0
            relevances.append(relevance)

            # Distance for min_distance metric
            distances.append(c.get("distance", 1.0))

            # Cosine similarity if embeddings available
            if query_embedding:
                chunk_embedding = get_chunk_embedding(c)
                if chunk_embedding:
                    cosine_score = cosine_similarity(query_embedding, chunk_embedding)
                    cosine_scores.append(cosine_score)

        # Compute metrics
        hit = 1 if any(r > 0 for r in relevances) else 0
        min_distance = min(distances) if distances else 1.0
        ndcg = ndcg_at_k(relevances, k)
        mrr = compute_mrr(relevances)
        max_cosine = max(cosine_scores) if cosine_scores else None

        # Time the full triage step and capture stats
        triage_start = time.time()
        verifier_score = None
        stats = {}
        try:
            result = orch.triage({"title": q, "body": q, "severity": "Unknown"}, k=k)
            verifier_score = 1 if result.get("draft_ok") else 0
            stats = result.get("stats", {})
        except Exception:
            verifier_score = None

        triage_time = (time.time() - triage_start) * 1000  # ms

        # Extract timing info
        timings = extract_timing_from_stats(stats)
        timings["retrieval_ms"] = retrieval_time
        timings["triage_total_ms"] = triage_time
        all_timings.append(timings)

        # Estimate costs
        cost_info = estimate_cost_from_stats(stats)
        all_costs.append(cost_info)

        per_item.append(
            {
                "id": it["id"],
                "hit": hit,
                "min_distance": float(min_distance),
                "verifier_score": verifier_score,
                "ndcg_at_k": ndcg,
                "mrr": mrr,
                "max_cosine": max_cosine,
                "timings": timings,
                "cost_info": cost_info,
            }
        )

    # Aggregate metrics
    hits = [p["hit"] for p in per_item]
    distances = [p["min_distance"] for p in per_item]
    verifier_scores = [p["verifier_score"] for p in per_item if p["verifier_score"] is not None]
    ndcg_scores = [p["ndcg_at_k"] for p in per_item]
    mrr_scores = [p["mrr"] for p in per_item]
    cosine_scores = [p["max_cosine"] for p in per_item if p["max_cosine"] is not None]

    agg = {
        "hit_rate": mean(hits) if hits else 0.0,
        "mean_min_distance": mean(distances) if distances else 0.0,
        "mean_verifier_score": (mean(verifier_scores) if verifier_scores else None),
        "ndcg_at_k": mean(ndcg_scores) if ndcg_scores else 0.0,
        "mrr": mean(mrr_scores) if mrr_scores else 0.0,
    }

    # Semantic cosine statistics
    if cosine_scores:
        if len(cosine_scores) >= 4:
            q25, q50, q75 = quantiles(cosine_scores, n=4)[0:3]
            agg["semantic_cosine"] = {
                "mean": mean(cosine_scores),
                "p25": q25,
                "p50": q50,
                "p75": q75,
            }
        else:
            agg["semantic_cosine"] = {
                "mean": mean(cosine_scores),
                "p25": min(cosine_scores),
                "p50": mean(cosine_scores),
                "p75": max(cosine_scores),
            }
    else:
        agg["semantic_cosine"] = None

    # Timing aggregation
    if all_timings:
        total_times = [t.get("triage_total_ms", 0) for t in all_timings if t.get("triage_total_ms")]
        retrieval_times = [t.get("retrieval_ms", 0) for t in all_timings if t.get("retrieval_ms")]

        timing_dict = {
            "mean_total_ms": mean(total_times) if total_times else 0.0,
            "mean_retrieval_ms": (mean(retrieval_times) if retrieval_times else 0.0),
        }

        if len(total_times) >= 20:  # Need reasonable sample for p95
            sorted_total = sorted(total_times)
            p95_idx = int(0.95 * len(sorted_total))
            timing_dict["p95_total_ms"] = sorted_total[p95_idx]
        else:
            timing_dict["p95_total_ms"] = max(total_times) if total_times else 0.0

        agg["timings"] = timing_dict
    else:
        agg["timings"] = None

    # Cost aggregation
    if all_costs:
        total_ml_calls = sum(c.get("ml_calls", 0) for c in all_costs)
        total_embedding_calls = sum(c.get("embedding_calls", 0) for c in all_costs)
        total_vector_calls = sum(c.get("vector_search_calls", 0) for c in all_costs)
        total_bytes = sum(c.get("bytes_processed", 0) for c in all_costs)

        agg["cost_estimates"] = {
            "total_ml_calls": total_ml_calls,
            "total_embedding_calls": total_embedding_calls,
            "total_vector_search_calls": total_vector_calls,
            "total_bytes_processed": total_bytes,
            "avg_ml_calls_per_query": total_ml_calls / len(all_costs),
        }
    else:
        agg["cost_estimates"] = None

    return {"items": per_item, "aggregate": agg}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run comprehensive eval")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", default="metrics/eval_results.json")
    parser.add_argument(
        "--use-stub", action="store_true", help="Force stub retrieval (ignore BIGQUERY_REAL)"
    )
    args = parser.parse_args(argv)

    use_stub = args.use_stub or os.getenv("BIGQUERY_REAL") != "1"
    items = load_items()
    results = evaluate(items, k=args.top_k, use_stub=use_stub)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    agg = results["aggregate"]

    # Enhanced summary output
    semantic_info = ""
    if agg.get("semantic_cosine"):
        sem = agg["semantic_cosine"]
        semantic_info = f" semantic_cosine_mean={sem['mean']:.3f}"

    timing_info = ""
    if agg.get("timings"):
        timings = agg["timings"]
        timing_info = (
            f" mean_total_ms={timings['mean_total_ms']:.1f} "
            f"p95_total_ms={timings['p95_total_ms']:.1f}"
        )

    print(
        "[eval-summary] hit_rate={hr:.2f} ndcg@k={ndcg:.3f} "
        "mrr={mrr:.3f} mean_min_distance={md:.3f} "
        "mean_verifier_score={vs}{sem}{timing}".format(
            hr=agg.get("hit_rate", 0),
            ndcg=agg.get("ndcg_at_k", 0),
            mrr=agg.get("mrr", 0),
            md=agg.get("mean_min_distance", 0),
            vs=agg.get("mean_verifier_score"),
            sem=semantic_info,
            timing=timing_info,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
