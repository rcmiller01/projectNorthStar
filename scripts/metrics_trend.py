"""Metrics trend summarizer for CI.

Reads:
  metrics/eval_results.json (current)
  metrics/baseline.json (optional baseline; if missing, copies current)

Outputs:
  - Prints one-line delta summary
  - Prints a Markdown block (suitable for $GITHUB_STEP_SUMMARY)
  - Applies optional threshold gates via env vars:
      MIN_HIT_RATE (float)
      MAX_MIN_DIST (float)
      MIN_VERIFIER (float)
Exit codes:
  0 success / no threshold breach
  1 threshold failure or missing current metrics
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict

CUR_PATH = Path("metrics/eval_results.json")
BASE_PATH = Path("metrics/baseline.json")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_gate(name: str) -> float | None:
    raw = os.getenv(name)
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def main() -> int:  # pragma: no cover
    if not CUR_PATH.exists():
        print("[metrics-trend] current metrics missing")
        return 1
    cur = load_json(CUR_PATH)["aggregate"]
    if BASE_PATH.exists():
        base = load_json(BASE_PATH)["aggregate"]
    else:
        # Establish baseline
        write_json(BASE_PATH, load_json(CUR_PATH))
        base = cur
        print("[metrics-trend] baseline created")

    # Extract values (default 0 / None safe)
    fields = [
        ("hit_rate", True),  # higher better
        ("mean_min_distance", False),  # lower better
        ("mean_verifier_score", True),  # higher better (may be None)
    ]
    deltas: list[str] = []
    md_lines = [
        "### Evaluation Metrics",
        "",
        "| metric | base | current | delta | note |",
        "|--------|------|---------|-------|------|",
    ]
    for name, higher_better in fields:
        cur_val = cur.get(name)
        base_val = base.get(name)
        if cur_val is None or base_val is None:
            delta_str = "n/a"
            note = "(missing)"
        else:
            delta = cur_val - base_val
            sign = "+" if delta >= 0 else ""
            delta_str = f"{sign}{delta:.3f}"
            improved = delta > 0 if higher_better else delta < 0
            if delta == 0:
                note = ""
            else:
                note = "improved" if improved else "regressed"
        md_lines.append(
            f"| {name} | {base_val} | {cur_val} | {delta_str} | {note} |"
        )
        deltas.append(f"{name}={delta_str}")

    summary_line = "[metrics-trend] " + " ".join(deltas)
    print(summary_line)
    md = "\n".join(md_lines)
    print("\n" + md + "\n")

    # Threshold gates
    min_hit = get_gate("MIN_HIT_RATE")
    max_dist = get_gate("MAX_MIN_DIST")
    min_ver = get_gate("MIN_VERIFIER")
    fail = False
    if min_hit is not None and cur.get("hit_rate", 0) < min_hit:
        print(
            f"[metrics-trend] FAIL hit_rate {cur.get('hit_rate')} < {min_hit}"
        )
        fail = True
    if max_dist is not None and cur.get("mean_min_distance", 1) > max_dist:
        print(
            (
                "[metrics-trend] FAIL mean_min_distance "
                f"{cur.get('mean_min_distance')} > {max_dist}"
            )
        )
        fail = True
    mv = cur.get("mean_verifier_score")
    if min_ver is not None and mv is not None and mv < min_ver:
        print(f"[metrics-trend] FAIL mean_verifier_score {mv} < {min_ver}")
        fail = True

    return 1 if fail else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
