"""Tests for SQL verifier.

Copyright (c) 2025 Team NorthStar
Licensed under the MIT License. See LICENSE file for details.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(ROOT))

import src.verifier as verifier  # noqa: E402


def test_verify_sql_directory() -> None:
    sql_dir = Path("sql")
    assert verifier.verify_sql_directory(sql_dir) is True
