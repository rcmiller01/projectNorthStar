"""Micro evaluation harness.

Loads metrics/eval_set.jsonl and computes simple retrieval metrics.

Metrics per item:
  hit@k: 1 if any retrieved chunk text contains any expected term (ci)
  min_distance: min distance across retrieved (fallback 1.0)
  verifier_score: 1 if draft_ok else 0 (optional; skip if orchestrator fails)

Aggregate metrics:
  hit_rate, mean_min_distance, mean_verifier_score

Supports real BigQuery (if BIGQUERY_REAL=1) else stub retrieval.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from statistics import mean
from typing import List

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


def load_items() -> List[dict]:
    if not EVAL_SET_PATH.exists():
        raise SystemExit("Eval set missing; run gen_eval_set first")
    items: List[dict] = []
    for line in EVAL_SET_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        items.append(json.loads(line))
    return items


def retrieve_chunks(
    client, query: str, k: int, types: List[str] | None
) -> List[dict]:
    # Pass through to hybrid vector_search which accepts 'types'
    return vector_search(client, query_text=query, k=k, types=types or [])


def evaluate(items: List[dict], k: int, use_stub: bool) -> dict:
    client = make_client()
    orch = Orchestrator(client)
    per_item: List[dict] = []
    for it in items:
        q = it["query_text"]
        types = it.get("types")
        chunks = retrieve_chunks(client, q, k=k, types=types)
        # hit@k
        expected_terms = [t.lower() for t in it.get("expected_terms", [])]
        hit = 0
        for c in chunks:
            text = (c.get("text") or c.get("snippet") or "").lower()
            if any(term in text for term in expected_terms):
                hit = 1
                break
        min_distance = min(
            (c.get("distance", 1.0) for c in chunks), default=1.0
        )
        # verifier (optional)
        verifier_score = None
        try:
            draft = orch.triage(
                {"title": q, "body": q, "severity": "Unknown"}, k=k
            )
            verifier_score = 1 if draft.get("draft_ok") else 0
        except Exception:
            verifier_score = None
        per_item.append(
            {
                "id": it["id"],
                "hit": hit,
                "min_distance": float(min_distance),
                "verifier_score": verifier_score,
            }
        )
    agg = {
        "hit_rate": mean([p["hit"] for p in per_item]) if per_item else 0.0,
        "mean_min_distance": mean(
            [p["min_distance"] for p in per_item]
        )
        if per_item
        else 0.0,
        "mean_verifier_score": mean(
            [
                p["verifier_score"]
                for p in per_item
                if p["verifier_score"] is not None
            ]
        )
        if any(p["verifier_score"] is not None for p in per_item)
        else None,
    }
    return {"items": per_item, "aggregate": agg}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run micro eval")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", default="metrics/eval_results.json")
    parser.add_argument(
        "--use-stub",
        action="store_true",
        help="Force stub retrieval (ignore BIGQUERY_REAL)"
    )
    args = parser.parse_args(argv)

    use_stub = args.use_stub or os.getenv("BIGQUERY_REAL") != "1"
    items = load_items()
    results = evaluate(items, k=args.top_k, use_stub=use_stub)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    agg = results["aggregate"]
    print(
        "[eval-summary] hit_rate={hr:.2f} mean_min_distance={md:.3f} "
        "mean_verifier_score={vs}".format(
            hr=agg.get("hit_rate"),
            md=agg.get("mean_min_distance"),
            vs=agg.get("mean_verifier_score"),
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
