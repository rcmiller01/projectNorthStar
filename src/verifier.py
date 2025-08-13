"""Verification utilities ensuring contest compliance.

Goals:
- Detect usage of BigQuery AI features in SQL templates.
- Provide a simple report for reviewers.

Copyright (c) 2025 Team NorthStar
Licensed under the MIT License. See LICENSE file for details.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable

KEY_TERMS = [
    "ML.GENERATE_EMBEDDING",
    "ML.VECTOR_SEARCH",
]

OPTIONAL_TERMS = [
    "ML.GENERATE_TEXT",
]


def scan_sql_files(paths: Iterable[Path]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for p in paths:
        text = p.read_text(encoding="utf-8")
        hits: list[str] = []
        for term in KEY_TERMS:
            if term in text:
                hits.append(term)
        if hits:
            findings[p.name] = hits
    return findings


def verify_sql_directory(dir_path: Path) -> bool:
    sql_files = [p for p in dir_path.glob("*.sql") if p.is_file()]
    findings = scan_sql_files(sql_files)
    has_embedding = any(
        KEY_TERMS[0] in v for v in findings.values()
    )
    has_vector = any(KEY_TERMS[1] in v for v in findings.values())
    # Optional: text generation
    # Presence of optional text gen (informational)
    has_text = any(
        any(opt in vv for opt in OPTIONAL_TERMS) for vv in findings.values()
    )
    if has_text:  # pragma: no cover
        print("INFO: Optional ML.GENERATE_TEXT usage detected")
    return has_embedding and has_vector
