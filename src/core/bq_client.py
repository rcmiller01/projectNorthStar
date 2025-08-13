"""BigQuery / BigQuery AI client helpers (placeholder).

This module will abstract:
- Table access
- Embedding & ML invocation (BQ AI models)
- Query templating and cost controls

Phase 1: Provide interface + dry-run stub.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class QueryResult:
    rows: list[dict[str, Any]]
    job_id: str
    bytes_processed: int | None = None


class BigQueryAIClient:
    def __init__(
        self,
        project_id: str,
        location: str = "US",
        dry_run: bool = True,
    ):
        self.project_id = project_id
        self.location = location
        self.dry_run = dry_run

    def run_sql(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> QueryResult:  # stub
        """Execute SQL (stubbed).

        Replace with actual google.cloud.bigquery usage. For dry-run, returns
        empty set and pseudo job id.
        """
        return QueryResult(rows=[], job_id="DRY_JOB", bytes_processed=0)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:  # stub
        """Call BigQuery AI embedding model (stub)."""
        return [[0.0] * 8 for _ in texts]  # tiny fixed-size mock embedding
