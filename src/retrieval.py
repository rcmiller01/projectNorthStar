"""Retrieval logic (hybrid lexical + vector placeholder)."""
from __future__ import annotations
from typing import Any, Iterable
from .bigquery_client import BigQueryClient


def retrieve(
    client: BigQueryClient,
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    # For now just vector search on embedding of query
    q_vec = client.generate_embedding(query)
    results = client.vector_search(q_vec, top_k=top_k)
    return list(results)


def batch_retrieve(
    client: BigQueryClient,
    queries: Iterable[str],
    top_k: int = 5,
) -> list[list[dict[str, Any]]]:
    return [retrieve(client, q, top_k=top_k) for q in queries]
