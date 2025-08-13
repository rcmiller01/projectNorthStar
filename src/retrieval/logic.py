"""Legacy retrieval logic moved from src/retrieval.py for clarity."""
from __future__ import annotations
from typing import Any, Iterable
from src.bigquery_client import BigQueryClient


def retrieve(
    client: BigQueryClient,
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    q_vec = client.generate_embedding(query)
    results = client.vector_search(q_vec, top_k=top_k)
    return list(results)


def batch_retrieve(
    client: BigQueryClient,
    queries: Iterable[str],
    top_k: int = 5,
) -> list[list[dict[str, Any]]]:
    return [retrieve(client, q, top_k=top_k) for q in queries]
