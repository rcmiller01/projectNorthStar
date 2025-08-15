"""Idempotent creation of Phase-5 dashboard views in BigQuery.

Reads environment:
  PROJECT_ID, DATASET, LOCATION

Templates (sql/):
  views_common_issues.sql -> view_common_issues
  views_by_severity.sql   -> view_issues_by_severity
  views_duplicates.sql    -> view_duplicate_chunks

Substitution: ${PROJECT_ID} and ${DATASET} already used in templates; we
simply pass through content (no Python .format on braces to avoid collisions).

Usage:
  PROJECT_ID=... DATASET=... LOCATION=... python scripts/create_views.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment configuration
from config import load_env
load_env()

from src.bq.bigquery_client import make_client

TEMPLATES: List[Tuple[str, str]] = [
    ("views_common_issues.sql", "view_common_issues"),
    ("views_by_severity.sql", "view_issues_by_severity"),
    ("views_duplicates.sql", "view_duplicate_chunks"),
]

SQL_DIR = Path("sql")


def _die(msg: str) -> None:
    print(f"[create-views] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def _check_env(var: str) -> str:
    val = os.getenv(var)
    if not val:
        _die(f"Environment variable {var} not set")
    return val


def _dataset_exists(client, project: str, dataset: str) -> bool:
    real = getattr(client, "_client", None)
    if not real:
        # Stub: assume exists
        return True
    try:
        real.get_dataset(f"{project}.{dataset}")
        return True
    except Exception:
        return False


def main() -> int:
    project = _check_env("PROJECT_ID")
    dataset = _check_env("DATASET")
    _check_env("LOCATION")  # only for user signalling; not used directly here

    client = make_client()
    if not _dataset_exists(client, project, dataset):
        _die(f"Dataset not found: {project}.{dataset}")

    created = 0
    for fname, view_name in TEMPLATES:
        path = SQL_DIR / fname
        if not path.exists():
            _die(f"Template missing: {fname}")
        sql = path.read_text(encoding="utf-8")
        # Replace placeholders (${PROJECT_ID} etc.) manually
        sql_exec = sql.replace("${PROJECT_ID}", project).replace("${DATASET}", dataset)
        # Execution via raw SQL (RealClient path uses underlying bigquery client)
        try:
            # For real client, we want to surface errors clearly.
            real = getattr(client, "_client", None)
            if real is not None:
                job = real.query(sql_exec)
                list(job.result())
            else:
                client.run_sql_template("inline", {"raw_sql": sql_exec})  # type: ignore
            created += 1
            print(f"[create-views] upserted: {project}.{dataset}.{view_name}")
        except Exception as exc:
            snippet = sql_exec[:200].replace("\n", " ")
            _die(f"Failed creating {view_name}: {exc} | SQL: {snippet}")

    print(f"[create-views] created {created}/{len(TEMPLATES)} views (idempotent)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
