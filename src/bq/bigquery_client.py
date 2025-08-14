"""BigQuery client wrapper (stub + real) for Phase 1.

Environment switch: set BIGQUERY_REAL=1 to use RealClient, else StubClient.
"""
from __future__ import annotations
from dataclasses import dataclass
import importlib
import os
from pathlib import Path
from typing import Any, Dict, List

SQL_DIR = Path("sql")


class BigQueryClientBase:
    """Interface for BigQuery client variants."""

    def run_sql_template(
        self, name: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class StubClient(BigQueryClientBase):
    """Offline stub returning deterministic rows for development."""

    def run_sql_template(
        self, name: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Support inline raw SQL passthrough (no-op, returns empty)
        if "raw_sql" in params:
            return []
        if name == "vector_search.sql":
            q = params.get("query_text", "")
            return [
                {"id": 1, "text": f"stub snippet for: {q}", "distance": 0.05},
            ]
        if name == "chunk_vector_search.sql":
            q = params.get("query_text", "")
            types = params.get("types") or []
            base = {
                "chunk_id": "chunk_1",
                "text": f"chunk snippet for: {q}",
                "distance": 0.07,
                "meta": {
                    "type": (types[0] if types else "pdf"),
                    "filename": "stub.pdf",
                },
            }
            return [base]
        return []


@dataclass
class RealClient(BigQueryClientBase):
    """Real BigQuery client using google-cloud-bigquery (best-effort)."""

    project: str | None = None
    location: str | None = None

    def __post_init__(self) -> None:
        try:  # lazy import
            bigquery_mod = importlib.import_module("google.cloud.bigquery")
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "bigquery lib missing; install or unset BIGQUERY_REAL."
            ) from exc
        self._bq_mod = bigquery_mod
        self._client = bigquery_mod.Client(
            project=self.project, location=self.location
        )

    def run_sql_template(
        self, name: str, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Raw SQL bypass
        if "raw_sql" in params:
            sql = params["raw_sql"]
        else:
            path = SQL_DIR / name
            if not path.exists():  # pragma: no cover
                raise FileNotFoundError(f"SQL template not found: {name}")
            sql_src = path.read_text(encoding="utf-8")
            sql = sql_src
        # Parameter placeholders
        batch_limit_env = os.getenv("EMBED_BATCH_LIMIT", "10000")
        try:
            batch_limit = min(50000, max(1, int(batch_limit_env)))
        except ValueError:
            batch_limit = 10000
        replacements = {
            "${PROJECT_ID}": self.project or "",
            "${DATASET}": os.getenv("BQ_DATASET", "demo_ai"),
            "${EMBED_MODEL}": os.getenv(
                "BQ_EMBED_MODEL", "text-embedding-004"
            ),
            "${QUERY_TEXT}": f"'{params.get('query_text', '')}'",
            "${TOP_K}": str(params.get("top_k", 5)),
            "${EMBED_BATCH_LIMIT}": str(batch_limit),
            "${TYPE_ARRAY}": (
                "[" + ",".join(f"'{t}'" for t in params.get("types", [])) + "]"
                if params.get("types")
                else "[]"
            ),
        }
        for k, v in replacements.items():
            sql = sql.replace(k, v)
        try:
            job = self._client.query(sql)
            rows = list(job.result())
        except Exception as exc:  # pragma: no cover
            if "credentials" in str(exc).lower():
                raise RuntimeError(
                    "BigQuery creds missing; set env or unset BIGQUERY_REAL."
                ) from exc
            raise
        out: List[Dict[str, Any]] = []
        for r in rows:
            d = dict(r)
            out.append(d)
        return out


def make_client() -> BigQueryClientBase:
    """Factory for appropriate client based on env switch."""
    if os.getenv("BIGQUERY_REAL") == "1":
        return RealClient(
            project=os.getenv("BQ_PROJECT_ID"),
            location=os.getenv("BQ_LOCATION"),
        )
    return StubClient()

# Reflection:
# Created stub + real client with simple template substitution.
# Next improvement: parameter binding and query caching.
