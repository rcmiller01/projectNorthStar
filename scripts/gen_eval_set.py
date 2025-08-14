"""Generate deterministic synthetic eval set (Phase micro-eval).

Writes metrics/eval_set.jsonl with ~20 items.
Fields per line:
  id: string
  query_text: string
  expected_terms: list[str]
  severity: string
  types: list[str]

Deterministic via fixed RNG seed.
"""
from __future__ import annotations
import json
from pathlib import Path
import random

COUNT = 20
SEVERITIES = ["P0", "P1", "P2", "P3", "High", "Medium", "Low"]
TYPES_POOL = [
    ["log"],
    ["pdf"],
    ["image_ocr"],
    ["log", "pdf"],
]
QUERIES = [
    ("login 500 error", ["login", "500"]),
    ("image upload fails", ["upload", "image"]),
    ("timeout after reset", ["timeout", "reset"]),
    ("auth token expired", ["token", "expired"]),
    ("pdf render blank", ["pdf", "blank"]),
    ("rate limit exceeded", ["rate", "limit"]),
    ("cache warming slow", ["cache", "slow"]),
    ("db connection refused", ["connection", "refused"]),
    ("search indexing lag", ["index", "lag"]),
    ("memory leak suspected", ["memory", "leak"]),
]


def make_items() -> list[dict]:
    rnd = random.Random(1337)
    items: list[dict] = []
    for i in range(COUNT):
        q_txt, terms = QUERIES[i % len(QUERIES)]
        item = {
            "id": f"item-{i+1}",
            "query_text": q_txt,
            "expected_terms": terms,
            "severity": rnd.choice(SEVERITIES),
            "types": rnd.choice(TYPES_POOL),
        }
        items.append(item)
    return items


def main() -> None:  # pragma: no cover
    out_dir = Path("metrics")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / "eval_set.jsonl"
    items = make_items()
    with path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    print(f"[gen-eval-set] wrote {len(items)} items -> {path}")


if __name__ == "__main__":  # pragma: no cover
    main()
