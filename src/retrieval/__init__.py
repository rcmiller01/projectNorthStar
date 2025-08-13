"""Retrieval package bridging legacy import path.

Exports retrieve and batch_retrieve from top-level src.retrieval module.
"""
from .logic import retrieve, batch_retrieve  # noqa: F401
