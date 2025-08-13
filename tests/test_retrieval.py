"""Tests for retrieval module.

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
import src.retrieval as retrieval  # noqa: E402


def test_retrieve_basic() -> None:
    c = BigQueryClient(project_id="demo")
    results = retrieval.retrieve(c, "test query", top_k=4)
    assert len(results) == 4
