"""Verification utilities ensuring contest compliance.

Goals:
- Detect usage of BigQuery AI features in SQL templates.
- Provide a simple report for reviewers.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable

KEY_TERMS = [
    "ML.GENERATE_EMBEDDING",
    "ML.VECTOR_SEARCH",
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
    # Contest rule (baseline): at least one embedding and vector search usage
    has_embedding = any(
        "ML.GENERATE_EMBEDDING" in v for v in findings.values()
    )
    has_vector = any("ML.VECTOR_SEARCH" in v for v in findings.values())
    return has_embedding and has_vector
