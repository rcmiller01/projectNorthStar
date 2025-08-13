"""Public-facing BigQuery AI client (contest version).

Minimal surface mirroring internal core client but without private logic.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(slots=True)
class QueryResult:
    rows: list[dict[str, Any]]
    job_id: str
    bytes_processed: int


class BigQueryClient:
    def __init__(
        self,
        project_id: str,
        location: str = "US",
        dry_run: bool = True,
    ):
        self.project_id = project_id
        self.location = location
        self.dry_run = dry_run

    def generate_embedding(self, text: str) -> list[float]:  # stub
        seed = sum(ord(c) for c in text) % 997
        return [((seed * i) % 100) / 100 for i in range(1, 9)]

    def batch_generate_embeddings(
        self, texts: Iterable[str]
    ) -> list[list[float]]:
        return [self.generate_embedding(t) for t in texts]

    def vector_search(
        self, query_vec: list[float], top_k: int = 5
    ) -> list[dict[str, Any]]:
        # deterministic placeholder
        return [
            {
                "id": f"doc_{i}",
                "distance": i / (top_k + 1),
                "title": f"Title {i}",
            }
            for i in range(1, top_k + 1)
        ]

    def run_sql(
        self, sql: str, params: dict[str, Any] | None = None
    ) -> QueryResult:
        return QueryResult(rows=[], job_id="DRY", bytes_processed=0)
