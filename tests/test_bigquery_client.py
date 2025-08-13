"""Tests for BigQueryClient.

Copyright (c) 2025 Team NorthStar
Licensed under the MIT License. See LICENSE file for details.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))

from src.bigquery_client import BigQueryClient  # noqa: E402


def test_embed_deterministic() -> None:
    c = BigQueryClient(project_id="demo")
    e1 = c.generate_embedding("hello")
    e2 = c.generate_embedding("hello")
    assert e1 == e2
    assert len(e1) == 8


def test_vector_search_shape() -> None:
    c = BigQueryClient(project_id="demo")
    res = c.vector_search([0.1] * 8, top_k=3)
    assert len(res) == 3
    assert {"id", "distance", "title"}.issubset(res[0].keys())
