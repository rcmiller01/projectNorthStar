"""Top-level hybrid retrieval wrapper re-exporting src.retrieval.hybrid logic.

Bridges earlier src/ layout so absolute import works.
"""
from __future__ import annotations
from src.retrieval.hybrid import vector_search  # type: ignore
__all__ = ["vector_search"]
